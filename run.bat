@echo off
chcp 65001 > nul
echo ========================================
echo  웹 표준/호환성 증빙 자료 생성기 실행
echo ========================================
echo.

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM Streamlit 앱 실행
echo 브라우저에서 앱이 열립니다...
echo 종료하려면 Ctrl+C를 누르세요.
echo.
streamlit run app.py --server.port 8501
