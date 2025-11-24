from flask import Flask, render_template, Response
import sqlite3
import os
import datetime
import cv2  # 카메라 모듈 추가

app = Flask(__name__)

# --- 경로 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "logs.db")
PHOTO_DIR = os.path.join(BASE_DIR, "static", "photos")

# --- [핵심] 카메라 설정 (GStreamer 모드) ---
# 라즈베리파이 최신 OS에서 OV5647 카메라를 켜기 위한 설정 문자열
gst_str = (
    "libcamerasrc ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! "
    "appsink"
)

def generate_frames():
    """카메라 프레임을 생성하여 스트리밍하는 함수"""
    # GStreamer 모드로 카메라 열기
    camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
    
    if not camera.isOpened():
        print("❌ 카메라를 열 수 없습니다. (다른 파이썬 프로그램이 사용 중인지 확인하세요)")
        return

    print("✅ 웹캠 스트리밍 시작...")
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                # 이미지를 JPG로 인코딩
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                
                # MJPEG 스트리밍 형식으로 전송
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # 스트리밍이 끊기면 카메라 자원 해제
        camera.release()
        print("⏹ 웹캠 스트리밍 종료")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def logs():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT method, success, created_at FROM logs ORDER BY id DESC")
        logs = c.fetchall()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")
        logs = []
    return render_template("logs.html", logs=logs)

@app.route("/photos")
def photos():
    """저장된 사진 목록을 보여주는 페이지"""
    photos_data = []
    # 사진 폴더가 없으면 생성
    if not os.path.exists(PHOTO_DIR):
        try:
            os.makedirs(PHOTO_DIR)
        except:
            pass
            
    try:
        # 폴더 내 파일 목록 읽기
        files = os.listdir(PHOTO_DIR)
        photo_files = [f for f in files if f.endswith(('.jpg', '.png'))]
        photo_files.sort(reverse=True) # 최신순 정렬
    except Exception as e:
        print(f"Photo Error: {e}")

    # 파일 정보 구성
    for f in photo_files:
        full_path = os.path.join(PHOTO_DIR, f)
        created_at = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
        photos_data.append({
            "path": f"/static/photos/{f}",
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return render_template("photos.html", photos=photos_data)

@app.route("/camera")
def camera():
    """실시간 카메라 화면을 보여주는 페이지"""
    # camera.html에서 video_feed 주소를 불러옵니다.
    return render_template("camera.html")

@app.route("/video_feed")
def video_feed():
    """HTML <img> 태그의 src에 들어갈 스트리밍 주소"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/capture", methods=["POST"])
def capture():
    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    save_path = os.path.join(PHOTO_DIR, filename)

    os.system(f"libcamera-still -n -o {save_path} --immediate --width 640 --height 480")

    return {"success": True, "path": save_path}


if __name__ == "__main__":
    # use_reloader=False 필수: 이게 없으면 카메라가 2번 켜져서 'Device Busy' 에러 남
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)