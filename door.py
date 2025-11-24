import RPi.GPIO as GPIO
import time
import sqlite3
import requests
from mfrc522 import SimpleMFRC522

# --- 설정 ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

SERVO_PIN = 5
AUTHORIZED_ID = 838204234412

# 키패드 핀
R1, R2, R3, R4 = 21, 20, 16, 12
C1, C2, C3, C4 = 26, 19, 13, 6
ROWS = [R1, R2, R3, R4]
COLS = [C1, C2, C3, C4]

KEYPAD = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]

CORRECT_PASSWORD = "135A"
current_input = ""
fail_count = 0
MAX_FAIL = 3

DB_FILE = "/home/naye/iot_응용2025/logs.db"
WEB_CAPTURE_URL = "http://127.0.0.1:8080/capture"

# --- 하드웨어 초기화 ---
reader = SimpleMFRC522()

for pin in ROWS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
for pin in COLS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# --- 유틸리티 함수 ---
def log_event(method, success=True):
    """SQLite DB에 출입 이벤트 기록"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (method, success) VALUES (?, ?)",
        (method, 1 if success else 0)
    )
    conn.commit()
    conn.close()

def set_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

def open_and_close_door():
    global current_input
    print(">>> 접근 승인! 문을 엽니다.")
    set_angle(90)
    time.sleep(5)
    print(">>> 문을 닫습니다.")
    set_angle(0)
    current_input = ""
    print("\n--- 다시 대기 상태 ---")

def take_photo():
    """웹서버에 사진 촬영 요청"""
    requests.post(WEB_CAPTURE_URL, timeout=3)


# --- 메인 루프 ---
try:
    print("--- 통합 도어락 시스템 시작 ---")
    set_angle(0)
    print("RFID 또는 비밀번호 입력 (종료: Ctrl+C)")

    while True:
        # RFID 체크
        id = reader.read_id_no_block()
        if id:
            if id == AUTHORIZED_ID:
                print(f"[RFID] 승인 ID: {id}")
                log_event("RFID", True)
                open_and_close_door()
            else:
                print(f"[RFID] 비인가 ID: {id}")
                log_event("RFID", False)
                # RFID 실패 → 즉시 사진 촬영
                take_photo()

            time.sleep(1)

        # 키패드 체크
        key_pressed = None
        for r_index, row_pin in enumerate(ROWS):
            GPIO.output(row_pin, GPIO.HIGH)
            for c_index, col_pin in enumerate(COLS):
                if GPIO.input(col_pin) == GPIO.HIGH:
                    key_pressed = KEYPAD[r_index][c_index]
                    while GPIO.input(col_pin) == GPIO.HIGH:
                        time.sleep(0.01)
                    break
            GPIO.output(row_pin, GPIO.LOW)
            if key_pressed:
                break

        if key_pressed:
            if key_pressed == '*':
                current_input = ""
                print("[키패드] 입력 취소")
            elif key_pressed == '#':
                if current_input == CORRECT_PASSWORD:
                    print("[키패드] 비밀번호 일치!")
                    log_event("KEYPAD", True)
                    open_and_close_door()
                else:
                    print("[키패드] 비밀번호 불일치!")
                    log_event("KEYPAD", False)

                    fail_count += 1
                    # print(f"실패 횟수: {fail_count}")

                    # 3회 실패 → 사진 촬영
                    if fail_count >= MAX_FAIL:
                        take_photo()
                        fail_count = 0

                current_input = ""
            else:
                current_input += key_pressed
                print(f"[키패드] 입력: {'*'*len(current_input)}")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    pwm.stop()
    GPIO.cleanup()
