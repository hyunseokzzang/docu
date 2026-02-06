"""
==============================================================================
SaaS형 웹 표준/호환성 증빙 자료 생성기 (웹 배포용)
==============================================================================

Streamlit Cloud 배포 방법:
1. GitHub에 이 폴더 업로드
2. https://share.streamlit.io 에서 앱 배포
3. Advanced settings에서 Python 3.10 이상 선택

필요 파일:
- app.py (이 파일)
- requirements.txt
- packages.txt (시스템 의존성)
"""

import streamlit as st
import sqlite3
import hashlib
import os
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path
import base64
import tempfile

# bcrypt 설치 확인 및 대체
try:
    import bcrypt
    USE_BCRYPT = True
except ImportError:
    USE_BCRYPT = False

# Playwright 설치 확인 및 자동 설치
PLAYWRIGHT_AVAILABLE = False
BROWSERS_INSTALLED = False

def check_and_install_playwright():
    """Playwright 및 브라우저 확인/설치"""
    global PLAYWRIGHT_AVAILABLE, BROWSERS_INSTALLED
    
    try:
        from playwright.sync_api import sync_playwright
        PLAYWRIGHT_AVAILABLE = True
    except ImportError:
        PLAYWRIGHT_AVAILABLE = False
        return False
    
    # 브라우저 설치 확인 (캐시 파일로 체크)
    cache_dir = Path(tempfile.gettempdir()) / ".playwright_installed"
    
    if not cache_dir.exists():
        try:
            # 브라우저 자동 설치
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True, capture_output=True
            )
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "webkit"],
                check=True, capture_output=True
            )
            cache_dir.touch()
            BROWSERS_INSTALLED = True
        except Exception as e:
            print(f"Browser install error: {e}")
            BROWSERS_INSTALLED = False
    else:
        BROWSERS_INSTALLED = True
    
    return PLAYWRIGHT_AVAILABLE and BROWSERS_INSTALLED

# 앱 시작 시 Playwright 초기화
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ============================================================================
# 1. Custom CSS 스타일
# ============================================================================
CUSTOM_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

* {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
}

/* 메인 배경 */
.stApp {
    background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 50%, #16213e 100%);
}

/* 사이드바 스타일 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E1E1E 0%, #2d2d2d 100%);
    border-right: 1px solid #3a3a3a;
}

[data-testid="stSidebar"] .stMarkdown {
    color: #e0e0e0;
}

/* 카드 스타일 */
.bento-card {
    background: #1E1E1E;
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #3a3a3a;
    box-shadow: 0 0 20px rgba(100, 255, 218, 0.1),
                0 0 40px rgba(100, 255, 218, 0.05);
    transition: all 0.3s ease;
}

.bento-card:hover {
    box-shadow: 0 0 30px rgba(100, 255, 218, 0.2),
                0 0 60px rgba(100, 255, 218, 0.1);
    border-color: #64ffda;
}

/* 글로우 효과 헤더 */
.glow-header {
    color: #64ffda;
    text-shadow: 0 0 10px rgba(100, 255, 218, 0.5),
                 0 0 20px rgba(100, 255, 218, 0.3);
    font-weight: 700;
    font-size: 2rem;
    margin-bottom: 1rem;
}

/* 서브 헤더 */
.sub-header {
    color: #a0a0a0;
    font-size: 0.9rem;
    margin-bottom: 2rem;
}

/* 버튼 스타일 */
.stButton > button {
    background: linear-gradient(135deg, #64ffda 0%, #00bfa5 100%);
    color: #1E1E1E;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 2rem;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    box-shadow: 0 0 20px rgba(100, 255, 218, 0.4);
    transform: translateY(-2px);
}

/* 입력 필드 */
.stTextInput > div > div > input {
    background: #2a2a2a;
    border: 1px solid #3a3a3a;
    color: #e0e0e0;
    border-radius: 8px;
}

.stTextInput > div > div > input:focus {
    border-color: #64ffda;
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
}

/* 진행 로그 */
.progress-log {
    background: #0a0a0a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 15px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 0.85rem;
    color: #64ffda;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* 이미지 카드 */
.img-card {
    background: #252525;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    border: 1px solid #3a3a3a;
    transition: all 0.3s ease;
}

.img-card:hover {
    border-color: #64ffda;
    box-shadow: 0 0 15px rgba(100, 255, 218, 0.15);
}

.img-card img {
    border-radius: 8px;
    max-width: 100%;
    cursor: pointer;
}

.img-card-title {
    color: #64ffda;
    font-weight: 600;
    margin-top: 10px;
    font-size: 0.9rem;
}

/* 히스토리 아이템 */
.history-item {
    background: #252525;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    border-left: 3px solid #64ffda;
    cursor: pointer;
    transition: all 0.2s ease;
}

.history-item:hover {
    background: #2a2a2a;
    transform: translateX(5px);
}

/* 성공/에러 메시지 */
.success-msg {
    background: rgba(100, 255, 218, 0.1);
    border: 1px solid #64ffda;
    border-radius: 8px;
    padding: 10px 15px;
    color: #64ffda;
}

.error-msg {
    background: rgba(255, 82, 82, 0.1);
    border: 1px solid #ff5252;
    border-radius: 8px;
    padding: 10px 15px;
    color: #ff5252;
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #252525;
    border-radius: 8px 8px 0 0;
    color: #a0a0a0;
    border: 1px solid #3a3a3a;
}

.stTabs [aria-selected="true"] {
    background: #1E1E1E;
    color: #64ffda;
    border-color: #64ffda;
}

/* 스크롤바 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1E1E1E;
}

::-webkit-scrollbar-thumb {
    background: #3a3a3a;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #64ffda;
}

/* 뱃지 스타일 */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 8px;
}

.badge-chrome {
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white;
}

.badge-edge {
    background: linear-gradient(135deg, #0078d4, #00bcf2);
    color: white;
}

.badge-whale {
    background: linear-gradient(135deg, #00c4b4, #00a89d);
    color: white;
}

.badge-safari {
    background: linear-gradient(135deg, #5ac8fa, #007aff);
    color: white;
}

.badge-w3c {
    background: linear-gradient(135deg, #005a9c, #0077b6);
    color: white;
}

/* 다운로드 버튼 */
.download-btn {
    display: inline-block;
    padding: 8px 16px;
    background: linear-gradient(135deg, #64ffda 0%, #00bfa5 100%);
    color: #1E1E1E;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    margin: 5px;
}

/* 상태 표시 */
.status-running {
    color: #ffd700;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
</style>
"""

# ============================================================================
# 2. 데이터베이스 설정 (임시 디렉토리 사용)
# ============================================================================
# 웹 환경에서는 임시 디렉토리 사용
if os.environ.get('STREAMLIT_SHARING_MODE') or os.environ.get('IS_CLOUD'):
    DB_DIR = tempfile.gettempdir()
else:
    DB_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(DB_DIR, "users.db")
SCREENSHOTS_DIR = os.path.join(tempfile.gettempdir(), "web_checker_screenshots")

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 사용자 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 히스토리 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            page_title TEXT,
            url TEXT NOT NULL,
            screenshot_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    if USE_BCRYPT:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        # bcrypt 없으면 SHA256 사용 (보안 낮음, 데모용)
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    if USE_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    else:
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed

def create_user(username: str, password: str) -> tuple:
    """사용자 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (username, hashed_pw))
        conn.commit()
        return True, "회원가입이 완료되었습니다!"
    except sqlite3.IntegrityError:
        return False, "이미 존재하는 사용자명입니다."
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> tuple:
    """사용자 인증"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and verify_password(password, result[1]):
        return True, result[0]
    return False, None

def save_history(user_id: int, page_title: str, url: str, screenshot_data: dict):
    """검사 히스토리 저장 (base64 이미지 포함)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (user_id, page_title, url, screenshot_data)
        VALUES (?, ?, ?, ?)
    """, (user_id, page_title, url, json.dumps(screenshot_data)))
    conn.commit()
    conn.close()

def get_user_history(user_id: int) -> list:
    """사용자의 검사 히스토리 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, page_title, url, screenshot_data, created_at 
        FROM history 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_history_by_id(history_id: int) -> dict:
    """히스토리 ID로 상세 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, page_title, url, screenshot_data, created_at 
        FROM history 
        WHERE id = ?
    """, (history_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'page_title': result[1],
            'url': result[2],
            'screenshot_data': json.loads(result[3]) if result[3] else {},
            'created_at': result[4]
        }
    return None

# ============================================================================
# 3. Playwright 자동화 (동기 방식 - 웹 배포 호환)
# ============================================================================

# User-Agent 문자열
USER_AGENTS = {
    'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'whale': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Whale/3.24.223.21 Safari/537.36',
}

def capture_w3c_validation(page, url: str) -> bytes:
    """W3C 웹 표준 검사 결과 캡처"""
    try:
        validator_url = f"https://validator.w3.org/nu/?doc={url}"
        page.goto(validator_url, wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(3000)
        screenshot = page.screenshot(full_page=True)
        return screenshot
    except Exception as e:
        st.warning(f"W3C 검사 오류: {str(e)}")
        return None

def capture_browser(playwright, url: str, browser_name: str) -> bytes:
    """브라우저 호환성 캡처"""
    try:
        # Safari는 WebKit 사용
        if browser_name.lower() == 'safari':
            browser = playwright.webkit.launch(
                headless=True
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
        else:
            # Chrome, Edge, Whale은 Chromium 기반 + User-Agent
            browser = playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            user_agent = USER_AGENTS.get(browser_name.lower(), USER_AGENTS['chrome'])
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=user_agent
            )
        
        page = context.new_page()
        page.goto(url, wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(2000)
        screenshot = page.screenshot(full_page=False)
        browser.close()
        return screenshot
    except Exception as e:
        st.warning(f"{browser_name} 캡처 오류: {str(e)}")
        return None

def run_full_check(url: str, page_title: str, user_id: int, progress_placeholder, log_placeholder):
    """전체 검사 실행"""
    logs = []
    screenshot_data = {}
    
    def add_log(message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        logs.append(f"[{timestamp}] {message}")
        log_placeholder.markdown(
            f'<div class="progress-log">{"<br>".join(logs[-15:])}</div>', 
            unsafe_allow_html=True
        )
    
    if not PLAYWRIGHT_AVAILABLE:
        add_log("❌ Playwright가 설치되지 않았습니다.")
        return None
    
    try:
        with sync_playwright() as playwright:
            total_steps = 5
            current_step = 0
            
            # 1. W3C 웹 표준 검사
            add_log("=" * 40)
            add_log("🏁 웹 표준(W3C) 검사 시작")
            add_log("=" * 40)
            
            current_step += 1
            progress_placeholder.progress(current_step / total_steps, f"W3C 검사 중... ({current_step}/{total_steps})")
            
            add_log(f"🔍 W3C 검사 페이지 접속 중...")
            
            browser = playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            w3c_screenshot = capture_w3c_validation(page, url)
            if w3c_screenshot:
                screenshot_data['w3c'] = base64.b64encode(w3c_screenshot).decode('utf-8')
                add_log("✅ W3C 검사 캡처 완료")
            
            browser.close()
            
            # 2-5. 브라우저 호환성 검사
            browsers = ['Chrome', 'Edge', 'Whale', 'Safari']
            
            for browser_name in browsers:
                current_step += 1
                progress_placeholder.progress(current_step / total_steps, f"{browser_name} 검사 중... ({current_step}/{total_steps})")
                
                add_log("")
                add_log("=" * 40)
                add_log(f"🏁 {browser_name} 호환성 검사 시작")
                add_log("=" * 40)
                add_log(f"🌐 {browser_name} 브라우저 시작 중...")
                add_log(f"🔗 {url} 접속 중...")
                
                screenshot = capture_browser(playwright, url, browser_name)
                if screenshot:
                    screenshot_data[browser_name.lower()] = base64.b64encode(screenshot).decode('utf-8')
                    add_log(f"✅ {browser_name} 캡처 완료")
        
        # 히스토리 저장
        if screenshot_data:
            save_history(user_id, page_title, url, screenshot_data)
            add_log("")
            add_log("=" * 40)
            add_log("🎉 모든 검사가 완료되었습니다!")
            add_log("=" * 40)
        
        return screenshot_data
        
    except Exception as e:
        add_log(f"❌ 오류 발생: {str(e)}")
        return None

# ============================================================================
# 4. Streamlit UI
# ============================================================================

def render_screenshot(title: str, img_base64: str, badge_class: str):
    """스크린샷 렌더링"""
    if img_base64:
        st.markdown(f"""
            <div class="bento-card">
                <span class="badge {badge_class}">{title}</span>
                <span style="color: #e0e0e0; font-weight: 600; margin-left: 10px;">{title} 캡처</span>
            </div>
        """, unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{img_base64}", use_container_width=True)
        
        # 다운로드 버튼
        st.download_button(
            label=f"📥 {title} 이미지 다운로드",
            data=base64.b64decode(img_base64),
            file_name=f"{title.lower()}_capture.png",
            mime="image/png",
            key=f"download_{title}_{datetime.now().timestamp()}"
        )

def auto_install_browsers():
    """앱 시작 시 Playwright 브라우저 자동 설치"""
    cache_file = Path(tempfile.gettempdir()) / ".playwright_browsers_ok_v2"
    
    if cache_file.exists():
        return True
    
    try:
        # 시스템 의존성과 함께 Chromium 설치
        result1 = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
            capture_output=True, text=True, timeout=600
        )
        # WebKit 설치
        result2 = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--with-deps", "webkit"],
            capture_output=True, text=True, timeout=600
        )
        
        # 설치 결과 확인
        if result1.returncode == 0 or result2.returncode == 0:
            cache_file.touch()
            return True
        else:
            # 의존성 없이 재시도
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], timeout=300)
            subprocess.run([sys.executable, "-m", "playwright", "install", "webkit"], timeout=300)
            cache_file.touch()
            return True
    except Exception as e:
        print(f"Browser install error: {e}")
        # 마지막 시도
        try:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], timeout=300)
            cache_file.touch()
            return True
        except:
            pass
    
    return False

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="웹 표준/호환성 증빙 자료 생성기",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS 적용
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # 데이터베이스 초기화
    init_db()
    
    # 스크린샷 디렉토리 생성
    Path(SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
    
    # 앱 시작 시 브라우저 자동 설치 (백그라운드)
    if 'browser_install_attempted' not in st.session_state:
        st.session_state.browser_install_attempted = True
        if PLAYWRIGHT_AVAILABLE:
            cache_file = Path(tempfile.gettempdir()) / ".playwright_browsers_installed"
            if not cache_file.exists():
                with st.spinner("🔧 첫 실행: 브라우저 설치 중... (1-2분 소요)"):
                    if auto_install_browsers():
                        st.session_state.browsers_ready = True
                        st.success("✅ 브라우저 설치 완료!")
                    else:
                        st.warning("⚠️ 브라우저 설치 실패. 일부 기능이 제한될 수 있습니다.")
            else:
                st.session_state.browsers_ready = True
    
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'view_history_id' not in st.session_state:
        st.session_state.view_history_id = None
    if 'checking' not in st.session_state:
        st.session_state.checking = False
    
    # ========== 사이드바 ==========
    with st.sidebar:
        st.markdown('<h2 style="color: #64ffda; margin-bottom: 0;">🔍 Web Checker</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666; font-size: 0.8rem;">웹 표준/호환성 증빙 자료 생성기</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Playwright 상태 표시
        if PLAYWRIGHT_AVAILABLE:
            cache_file = Path(tempfile.gettempdir()) / ".playwright_browsers_installed"
            if cache_file.exists() or st.session_state.get('browsers_ready', False):
                st.success("✅ 시스템 준비 완료")
            else:
                st.info("🔄 브라우저 준비 중...")
        else:
            st.error("❌ Playwright 미설치")
        
        st.markdown("---")
        
        # 로그인/회원가입 섹션
        if not st.session_state.logged_in:
            st.markdown("### 🔐 로그인 / 회원가입")
            
            tab1, tab2 = st.tabs(["로그인", "회원가입"])
            
            with tab1:
                login_username = st.text_input("아이디", key="login_username", placeholder="아이디 입력")
                login_password = st.text_input("비밀번호", type="password", key="login_password", placeholder="비밀번호 입력")
                
                if st.button("로그인", key="login_btn", use_container_width=True):
                    if login_username and login_password:
                        success, user_id = authenticate_user(login_username, login_password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            st.session_state.username = login_username
                            st.success("로그인 성공!")
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                    else:
                        st.warning("아이디와 비밀번호를 입력해주세요.")
            
            with tab2:
                signup_username = st.text_input("아이디", key="signup_username", placeholder="사용할 아이디")
                signup_password = st.text_input("비밀번호", type="password", key="signup_password", placeholder="비밀번호")
                signup_password_confirm = st.text_input("비밀번호 확인", type="password", key="signup_password_confirm", placeholder="비밀번호 확인")
                
                if st.button("회원가입", key="signup_btn", use_container_width=True):
                    if signup_username and signup_password and signup_password_confirm:
                        if signup_password == signup_password_confirm:
                            if len(signup_password) >= 4:
                                success, message = create_user(signup_username, signup_password)
                                if success:
                                    st.success(message)
                                else:
                                    st.error(message)
                            else:
                                st.warning("비밀번호는 4자 이상이어야 합니다.")
                        else:
                            st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        st.warning("모든 필드를 입력해주세요.")
        
        else:
            # 로그인된 상태
            st.markdown(f"### 👤 {st.session_state.username}")
            
            if st.button("로그아웃", key="logout_btn", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.current_results = None
                st.session_state.view_history_id = None
                st.rerun()
            
            st.markdown("---")
            
            # URL 입력 섹션
            st.markdown("### 📝 검사할 페이지")
            st.caption("최대 10개 URL 입력 가능")
            
            num_urls = st.number_input("URL 개수", min_value=1, max_value=10, value=1)
            
            url_inputs = []
            for i in range(int(num_urls)):
                st.markdown(f"**페이지 {i+1}**")
                title = st.text_input(f"제목", key=f"title_{i}", placeholder="페이지명", label_visibility="collapsed")
                url = st.text_input(f"URL", key=f"url_{i}", placeholder="https://...", label_visibility="collapsed")
                if title and url:
                    # URL 검증
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    url_inputs.append((title, url))
                st.markdown("---")
            
            if st.button("🚀 검사 시작", key="start_check", use_container_width=True, type="primary"):
                if url_inputs:
                    st.session_state.current_results = None
                    st.session_state.view_history_id = None
                    st.session_state.checking = True
                    st.session_state.urls_to_check = url_inputs
                    st.rerun()
                else:
                    st.warning("최소 1개의 페이지 정보를 입력해주세요.")
            
            st.markdown("---")
            
            # 검사 히스토리
            st.markdown("### 📋 나의 점검 이력")
            history = get_user_history(st.session_state.user_id)
            
            if history:
                for item in history[:10]:
                    hist_id, title, url, _, created_at = item
                    created_date = created_at[:10] if created_at else ""
                    display_title = title[:15] + "..." if len(title) > 15 else title
                    
                    if st.button(f"📄 {display_title} ({created_date})", key=f"hist_{hist_id}", use_container_width=True):
                        st.session_state.view_history_id = hist_id
                        st.session_state.current_results = None
                        st.session_state.checking = False
                        st.rerun()
            else:
                st.caption("아직 점검 이력이 없습니다.")
    
    # ========== 메인 패널 ==========
    if not st.session_state.logged_in:
        # 로그인 전 화면
        st.markdown('<h1 class="glow-header">🔍 웹 표준/호환성 증빙 자료 생성기</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">웹사이트의 W3C 웹 표준 검사 결과와 다양한 브라우저 호환성을 자동으로 캡처합니다.</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="bento-card">
                    <h3 style="color: #64ffda;">🌐 W3C 웹 표준 검사</h3>
                    <p style="color: #a0a0a0;">validator.w3.org에 URL을 입력하고 결과 화면을 자동 캡처합니다.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="bento-card">
                    <h3 style="color: #64ffda;">📸 자동 스크린샷</h3>
                    <p style="color: #a0a0a0;">증빙 자료용 고품질 스크린샷을 자동으로 저장하고 다운로드할 수 있습니다.</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="bento-card">
                    <h3 style="color: #64ffda;">🖥️ 크로스 브라우저 호환성</h3>
                    <p style="color: #a0a0a0;">Chrome, Edge, Whale, Safari 4개 브라우저에서 진입 화면을 캡처합니다.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="bento-card">
                    <h3 style="color: #64ffda;">📋 이력 관리</h3>
                    <p style="color: #a0a0a0;">검사 이력을 저장하고 언제든 다시 확인할 수 있습니다.</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 👈 왼쪽 사이드바에서 로그인하여 시작하세요!")
        
        # 사용법 설명
        with st.expander("📖 사용 방법"):
            st.markdown("""
            1. **회원가입/로그인**: 사이드바에서 계정을 만들고 로그인합니다.
            2. **URL 입력**: 검사할 웹페이지의 제목과 URL을 입력합니다 (최대 10개).
            3. **검사 시작**: '검사 시작' 버튼을 클릭하면 자동으로 캡처가 진행됩니다.
            4. **결과 확인**: 캡처된 이미지를 확인하고 다운로드합니다.
            5. **이력 조회**: 이전에 검사한 결과는 '나의 점검 이력'에서 다시 볼 수 있습니다.
            """)
    
    else:
        # 로그인 후 대시보드
        st.markdown('<h1 class="glow-header">📊 대시보드</h1>', unsafe_allow_html=True)
        
        # 검사 진행 중
        if st.session_state.checking:
            st.markdown("### 🔄 검사 진행 중...")
            st.markdown('<p class="status-running">⏳ 잠시만 기다려주세요. 브라우저 자동화가 진행 중입니다...</p>', unsafe_allow_html=True)
            
            progress_placeholder = st.empty()
            log_placeholder = st.empty()
            
            urls_to_check = st.session_state.get('urls_to_check', [])
            all_results = []
            
            for idx, (title, url) in enumerate(urls_to_check):
                st.markdown(f"#### 📄 [{idx+1}/{len(urls_to_check)}] {title}")
                
                results = run_full_check(url, title, st.session_state.user_id, progress_placeholder, log_placeholder)
                if results:
                    all_results.append({
                        'title': title,
                        'url': url,
                        'screenshots': results
                    })
            
            progress_placeholder.progress(1.0, "✅ 완료!")
            st.session_state.checking = False
            st.session_state.current_results = all_results
            st.rerun()
        
        # 히스토리 보기
        elif st.session_state.view_history_id:
            history_data = get_history_by_id(st.session_state.view_history_id)
            
            if history_data:
                st.markdown(f"### 📄 {history_data['page_title']}")
                st.markdown(f"**URL:** `{history_data['url']}`")
                st.markdown(f"**검사일:** {history_data['created_at']}")
                st.markdown("---")
                
                screenshots = history_data['screenshot_data']
                
                # W3C 결과
                if 'w3c' in screenshots:
                    render_screenshot("W3C", screenshots['w3c'], "badge-w3c")
                
                st.markdown("---")
                st.markdown("### 🌐 브라우저 호환성")
                
                col1, col2 = st.columns(2)
                
                browser_info = [
                    ('chrome', 'Chrome', 'badge-chrome'),
                    ('edge', 'Edge', 'badge-edge'),
                    ('whale', 'Whale', 'badge-whale'),
                    ('safari', 'Safari', 'badge-safari')
                ]
                
                for idx, (key, name, badge) in enumerate(browser_info):
                    col = col1 if idx % 2 == 0 else col2
                    with col:
                        if key in screenshots:
                            render_screenshot(name, screenshots[key], badge)
                
                st.markdown("---")
                if st.button("← 대시보드로 돌아가기", use_container_width=True):
                    st.session_state.view_history_id = None
                    st.rerun()
        
        # 검사 결과 표시
        elif st.session_state.current_results:
            st.markdown("### ✅ 검사 완료!")
            
            for result in st.session_state.current_results:
                with st.expander(f"📄 {result['title']}", expanded=True):
                    st.markdown(f"**URL:** `{result['url']}`")
                    
                    screenshots = result['screenshots']
                    
                    # W3C 결과
                    if 'w3c' in screenshots:
                        render_screenshot("W3C", screenshots['w3c'], "badge-w3c")
                    
                    st.markdown("---")
                    st.markdown("#### 🌐 브라우저 호환성")
                    
                    col1, col2 = st.columns(2)
                    
                    browser_info = [
                        ('chrome', 'Chrome', 'badge-chrome'),
                        ('edge', 'Edge', 'badge-edge'),
                        ('whale', 'Whale', 'badge-whale'),
                        ('safari', 'Safari', 'badge-safari')
                    ]
                    
                    for idx, (key, name, badge) in enumerate(browser_info):
                        col = col1 if idx % 2 == 0 else col2
                        with col:
                            if key in screenshots:
                                render_screenshot(name, screenshots[key], badge)
            
            st.markdown("---")
            if st.button("🔄 새 검사 시작", use_container_width=True):
                st.session_state.current_results = None
                st.rerun()
        
        else:
            # 기본 대시보드
            st.markdown(f"### 👋 환영합니다, {st.session_state.username}님!")
            
            st.markdown("""
                <div class="bento-card">
                    <h3 style="color: #64ffda;">🚀 시작하기</h3>
                    <p style="color: #a0a0a0;">왼쪽 사이드바에서 검사할 페이지의 제목과 URL을 입력하고 '검사 시작' 버튼을 클릭하세요.</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="bento-card">
                        <h4 style="color: #64ffda;">📋 검사 항목</h4>
                        <ul style="color: #a0a0a0;">
                            <li><strong>W3C 웹 표준 검사</strong> - validator.w3.org 결과 캡처</li>
                            <li><strong>Chrome 호환성</strong> - 진입 화면 캡처</li>
                            <li><strong>Edge 호환성</strong> - 진입 화면 캡처</li>
                            <li><strong>Whale 호환성</strong> - 진입 화면 캡처</li>
                            <li><strong>Safari 호환성</strong> - WebKit 엔진 캡처</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="bento-card">
                        <h4 style="color: #64ffda;">💡 팁</h4>
                        <ul style="color: #a0a0a0;">
                            <li>최대 10개의 URL을 한 번에 검사 가능</li>
                            <li>검사 결과는 자동으로 DB에 저장</li>
                            <li>이미지는 개별 다운로드 가능</li>
                            <li>이전 검사 이력은 사이드바에서 확인</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            # 최근 검사 이력
            history = get_user_history(st.session_state.user_id)
            if history:
                st.markdown("---")
                st.markdown("### 📊 최근 검사 이력")
                
                for item in history[:5]:
                    hist_id, title, url, _, created_at = item
                    st.markdown(f"""
                        <div class="history-item">
                            <strong style="color: #64ffda;">{title}</strong><br>
                            <span style="color: #666; font-size: 0.8rem;">{url}</span><br>
                            <span style="color: #888; font-size: 0.75rem;">{created_at}</span>
                        </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
