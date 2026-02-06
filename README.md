# 🔍 웹 표준/호환성 증빙 자료 생성기

웹사이트의 W3C 웹 표준 검사 결과와 다양한 브라우저 호환성을 자동으로 캡처하는 SaaS 도구입니다.

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| **W3C 웹 표준 검사** | validator.w3.org 결과 자동 캡처 |
| **Chrome 호환성** | Chrome 브라우저 진입 화면 캡처 |
| **Edge 호환성** | Edge 브라우저 진입 화면 캡처 |
| **Whale 호환성** | Whale 브라우저 진입 화면 캡처 |
| **Safari 호환성** | Safari(WebKit) 진입 화면 캡처 |
| **이력 관리** | 검사 결과 저장 및 조회 |
| **이미지 다운로드** | 개별 캡처 이미지 다운로드 |

## 🚀 배포 방법

### Streamlit Cloud (권장)

1. 이 폴더를 GitHub 저장소에 업로드
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. "New app" 클릭
4. GitHub 저장소 선택
5. Main file path: `app.py`
6. Deploy 클릭

> ⚠️ 첫 실행 시 "브라우저 설치" 버튼을 클릭해야 합니다.

### Render

1. [render.com](https://render.com) 접속
2. New Web Service 생성
3. GitHub 저장소 연결
4. Build Command: `pip install -r requirements.txt && playwright install chromium webkit`
5. Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### Railway

1. [railway.app](https://railway.app) 접속
2. New Project → Deploy from GitHub repo
3. 자동으로 `Procfile` 감지하여 배포

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnss3 libnspr4 libdbus-1-3 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 \
    libcairo2 libatspi2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium webkit

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📁 파일 구조

```
품질관련자동화/
├── .streamlit/
│   └── config.toml      # Streamlit 테마 설정
├── app.py               # 메인 애플리케이션
├── requirements.txt     # Python 패키지
├── packages.txt         # Linux 시스템 의존성
├── Procfile             # Heroku/Railway 배포용
├── runtime.txt          # Python 버전 지정
├── postinstall.sh       # 배포 후 스크립트
└── README.md            # 이 파일
```

## 🎨 디자인 특징

- **Pretendard 폰트** 적용
- **다크 테마** (#1E1E1E 카드 배경)
- **Glow 효과** (민트색 #64ffda 강조)
- **반응형 레이아웃**

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python + SQLite
- **자동화**: Playwright (Chromium, WebKit)
- **인증**: bcrypt 해싱

## 📝 사용 방법

1. **회원가입/로그인**: 사이드바에서 계정 생성 및 로그인
2. **URL 입력**: 검사할 웹페이지 제목과 URL 입력 (최대 10개)
3. **검사 시작**: 버튼 클릭으로 자동 캡처 시작
4. **결과 확인**: W3C 및 4개 브라우저 캡처 결과 확인
5. **다운로드**: 필요한 이미지 개별 다운로드
6. **이력 조회**: 이전 검사 결과 다시 보기

## ⚠️ 주의사항

- 첫 배포 후 "브라우저 설치" 버튼을 반드시 클릭하세요.
- Streamlit Cloud 무료 플랜은 리소스 제한이 있습니다.
- 대용량 사이트 캡처 시 시간이 오래 걸릴 수 있습니다.
