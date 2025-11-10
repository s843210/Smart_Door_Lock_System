import sqlite3

DB_FILE = "/home/naye/iot_응용2025/logs.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# 로그 테이블 생성
c.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method TEXT NOT NULL,      -- 'RFID' 또는 'KEYPAD'
    success INTEGER NOT NULL,  -- 1=성공, 0=실패
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("SQLite DB 초기화 완료")
