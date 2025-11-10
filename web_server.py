from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
# DB_FILE = "/home/naye/iot_응용2025/logs.db"
DB_FILE = "D:\\Visual Studio Code\\home\\naye\\iot_응용2025\\logs.db"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)