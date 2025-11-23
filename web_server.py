from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
# DB_FILE = "/home/naye/iot_응용2025/logs.db"
import os
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def logs():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT method, success, created_at FROM logs ORDER BY id DESC")
    logs = c.fetchall()
    conn.close()
    return render_template("logs.html", logs=logs)

@app.route("/photos")
def photos():
    # conn = sqlite3.connect(DB_FILE)
    # c = conn.cursor()
    # c.execute("SELECT path, created_at FROM photos ORDER BY id DESC")
    # photos_list = [{"path": row[0], "created_at": row[1]} for row in c.fetchall()]
    # conn.close()

    return render_template("photos.html")

@app.route("/camera")
def camera():
    return render_template("camera.html")

# @app.route("/video_feed")
# def video_feed():
#    """실시간 카메라 스트림"""
#    from camera_module import generate_frames
#    return Response(generate_frames(),
#                    mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route("/capture", methods=["POST"])
# def capture():
#    """사진 캡처 및 저장"""
#    from camera_module import capture_photo
#    success, message = capture_photo()
#    return jsonify({"success": success, "message": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)