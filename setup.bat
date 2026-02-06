@echo off
chcp 65001 > nul
echo ========================================
echo  웹 표준/호환성 증빙 자료 생성기 설치
echo ========================================
echo.

REM Python 가상환경 생성
echo [1/4] 가상환경 생성 중...
python -m venv venv

REM 가상환경 활성화
echo [2/4] 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 패키지 설치
echo [3/4] 필요한 패키지 설치 중...
pip install -r requirements.txt

REM Playwright 브라우저 설치
echo [4/4] Playwright 브라우저 설치 중...
playwright install chromium webkit

echo.
echo ========================================
echo  설치가 완료되었습니다!
echo  run.bat 파일을 실행하여 앱을 시작하세요.
echo ========================================
pause
