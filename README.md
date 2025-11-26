# IoT 스마트 도어락 시스템 (Smart Door Lock System)

라즈베리파이(Raspberry Pi)를 활용한 IoT 기반 스마트 도어락 프로젝트입니다. RFID 카드와 키패드 비밀번호를 이용한 출입 제어, 실시간 웹 모니터링, 그리고 비인가 접근 시 사진 촬영 기능을 제공합니다.

## 📝 주요 기능

### 1. 출입 제어 (Door Control)
- **RFID 인증**: 등록된 RFID 태그를 태깅하여 문을 열 수 있습니다.
- **비밀번호 인증**: 4x4 키패드를 통해 비밀번호(`135A`)를 입력하여 문을 열 수 있습니다.
- **자동 잠금**: 문이 열린 후 5초 뒤에 자동으로 잠깁니다 (서보 모터 제어).

### 2. 보안 및 감시 (Security & Monitoring)
- **출입 로그 기록**: 모든 출입 시도(성공/실패)는 날짜, 시간, 인증 방식과 함께 데이터베이스(SQLite)에 기록됩니다.
- **침입자 촬영**:
  - RFID 인증 실패 시 즉시 사진을 촬영합니다.
  - 비밀번호 3회 연속 입력 실패 시 사진을 촬영합니다.
- **실시간 비디오 스트리밍**: 웹 브라우저를 통해 실시간으로 현관 상황을 확인할 수 있습니다.

### 3. 웹 인터페이스 (Web Interface)
- **대시보드**: 시스템 상태 확인.
- **로그 조회 (`/logs`)**: 출입 기록을 최신순으로 조회할 수 있습니다.
- **사진 앨범 (`/photos`)**: 보안 위협으로 인해 촬영된 사진들을 확인할 수 있습니다.
- **실시간 카메라 (`/camera`)**: 라즈베리파이 카메라의 실시간 영상을 스트리밍합니다.

## 🛠 하드웨어 구성

- **Raspberry Pi** (카메라 모듈 연결 가능 모델)
- **Pi Camera Module** (OV5647 등)
- **RFID-RC522** 모듈
- **4x4 Keypad**
- **Servo Motor** (SG90 등)
- **Jumper Wires & Breadboard**

### 핀 연결 (GPIO BCM 기준)
- **Servo Motor**: GPIO 5
- **Keypad**:
  - Rows: 21, 20, 16, 12
  - Cols: 26, 19, 13, 6
- **RFID**: SPI 인터페이스 사용 (SDA, SCK, MOSI, MISO, RST 등)

## ⚙️ 설치 및 실행 방법

### 1. 환경 설정
필요한 파이썬 라이브러리를 설치합니다.

```bash
pip install flask opencv-python RPi.GPIO mfrc522 requests
```
*참고: 라즈베리파이 환경에 따라 추가적인 시스템 패키지 설치가 필요할 수 있습니다 (예: `libcamera-apps`).*

### 2. 데이터베이스 초기화
로그 저장을 위한 데이터베이스 테이블을 생성합니다.

```bash
python init_db.py
```

### 3. 웹 서버 실행
웹 인터페이스와 카메라 스트리밍을 담당하는 서버를 실행합니다.

```bash
python web_server.py
```
- 접속 주소: `http://<라즈베리파이_IP>:8080`

### 4. 도어락 시스템 실행
하드웨어 제어 및 로직을 담당하는 메인 프로그램을 실행합니다.

```bash
python door.py
```

## 📂 프로젝트 구조

```
📦 iot_--2025
 ┣ 📂 static
 ┃ ┗ 📂 photos       # 촬영된 사진 저장소
 ┣ 📂 templates      # 웹 페이지 HTML 템플릿
 ┣ 📜 door.py        # 하드웨어 제어 및 메인 로직 (RFID, Keypad, Servo)
 ┣ 📜 web_server.py  # Flask 웹 서버 (스트리밍, 로그/사진 조회)
 ┣ 📜 init_db.py     # DB 초기화 스크립트
 ┗ 📜 logs.db        # 출입 로그 데이터베이스 (자동 생성)
```
