from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# --- [핵심] 카메라 설정 (GStreamer 모드) ---
# 라즈베리파이 최신 OS에서 OV5647 카메라를 켜기 위한 주문입니다.
gst_str = (
    "libcamerasrc ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! "
    "appsink"
)

def generate_frames():
    # 카메라 열기
    camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
    
    if not camera.isOpened():
        print("❌ 카메라를 열 수 없습니다. (다른 프로그램이 사용 중인지 확인하세요)")
        return

    print("✅ 카메라 스트리밍 시작...")
    
    while True:
        # 프레임 읽기
        success, frame = camera.read()
        if not success:
            break
        else:
            # 이미지를 JPG로 변환 (인코딩)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # 웹 브라우저로 전송 (MJPEG 스트리밍 방식)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()

@app.route('/')
def index():
    """메인 페이지에서 바로 카메라 화면 보여주기"""
    return render_template('camera.html')

@app.route('/video_feed')
def video_feed():
    """실시간 영상 주소"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # use_reloader=False를 해야 카메라가 2번 켜지는 오류를 막습니다.
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)