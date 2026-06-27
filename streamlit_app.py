import streamlit as st
import time
import base64
import pathlib
import re
import json
import requests
from urllib.parse import quote
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="정책기획팀 Snack Lab",
    page_icon="🍪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# 로컬 폰트 및 SVG Assets 로딩 헬퍼
# ─────────────────────────────────────────────
def get_file_base64(folder_name, file_name):
    path = pathlib.Path(__file__).parent / folder_name / file_name
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def load_svg(file_name):
    b64 = get_file_base64("assets", file_name)
    if b64:
        return f"data:image/svg+xml;base64,{b64}"
    return "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="

nanum_gothic_b64 = get_file_base64("fonts", "NanumGothic.otf")
funtime_b64 = get_file_base64("fonts", "Super Funtime.ttf")

svg_astroid = load_svg("astroid.svg")
svg_badge = load_svg("badge.svg")
svg_dot = load_svg("dot.svg")
svg_sparkles = load_svg("sparkles.svg")
svg_megaphone = load_svg("megaphone.svg")
svg_candy = load_svg("candy.svg")
svg_cup_soda = load_svg("cup-soda.svg")
svg_thumbs_up = load_svg("thumbs-up.svg")
svg_user_key = load_svg("user-round-key.svg")
svg_clip_pen = load_svg("clipboard-pen.svg")
svg_clip_check = load_svg("clipboard-check.svg")
svg_pin = load_svg("pin.svg")
svg_search = load_svg("search.svg")
svg_lock = load_svg("lock.svg")
svg_heart = load_svg("heart.svg")

# ─────────────────────────────────────────────
# 로고 글자를 한 글자씩 스큐어모피즘 + 플로팅 적용해서 만드는 헬퍼
# ─────────────────────────────────────────────
def build_skeuo_letters(text):
    spans = []
    i = 0
    for ch in text:
        if ch == " ":
            spans.append('<span class="logo-space"></span>')
        else:
            delay = (i % 6) * 0.18
            spans.append(f'<span class="logo-letter" style="animation-delay:{delay:.2f}s;">{ch}</span>')
            i += 1
    return "".join(spans)

LOGO_LETTERS_HTML = build_skeuo_letters("Snack Lab")

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@font-face {{
    font-family: 'NanumGothicLocal';
    src: url(data:font/opentype;base64,{nanum_gothic_b64}) format('opentype');
    font-weight: 300; font-style: normal;
}}
@font-face {{
    font-family: 'SuperFuntime';
    src: url(data:font/truetype;base64,{funtime_b64}) format('truetype');
    font-weight: 300; font-style: normal;
}}

html, body {{ 
    font-family: 'NanumGothicLocal', sans-serif; 
    background-color: #fdfdfa; 
}}
* {{ font-weight: 300 !important; }}

.block-container {{ max-width: 520px; padding: 0.5rem 1rem 4rem; }}

header[data-testid="stHeader"] {{
    background: transparent;
    height: 0 !important;
    min-height: 0 !important;
    pointer-events: none;
}}
div[data-testid="stToolbar"] {{ display: none !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}

/* ── 모바일(640px 미만)에서 st.columns가 자동으로 세로 스택되는 Streamlit 기본
   동작을 강제로 끈다. 이게 날짜 드롭다운/카드 그리드/고정 체크박스 등이
   모바일에서 다 한 줄씩 무너져 보이던 공통 원인이었음. ── */
div[data-testid="stHorizontalBlock"] {{
    flex-direction: row !important;
    flex-wrap: nowrap !important;
}}
div[data-testid="stHorizontalBlock"] > div {{
    min-width: 0 !important;
}}

/* ── 네비게이션 탭 ── */
[class*="st-key-btn_nav_"] {{ overflow: visible !important; min-width: 0 !important; }}
[class*="st-key-btn_nav_"] button {{
    font-size: 9px !important; padding: 1px 5px !important;
    min-height: 22px !important; height: 22px !important; line-height: 22px !important;
    background: transparent !important; border: none !important; outline: none !important;
    box-shadow: none !important; color: #475569 !important; border-radius: 0 !important;
    white-space: nowrap !important; width: auto !important; min-width: 0 !important;
}}
[class*="st-key-btn_nav_"] button:hover {{ text-decoration: underline !important; }}
[class*="st-key-btn_nav_"] button:focus {{ outline: none !important; box-shadow: none !important; border: none !important; }}
[class*="st-key-btn_nav_"] button:active {{ transform: none !important; }}
@media (max-width: 380px) {{
    [class*="st-key-btn_nav_"] button {{ font-size: 7.5px !important; padding: 1px 3px !important; }}
}}

/* ── 메인 로고: 글자별 스큐어모피즘 + 플로팅 ── */
.logo-banner {{
    position: relative; text-align: center; padding: 30px 20px;
    background: rgba(255, 255, 255, 0.6); 
    border: none;
    border-radius: 20px; margin: 0 -1rem 1.2rem;
    overflow: hidden;
}}
.logo-sub {{ font-size: 12px; font-weight: 300 !important; color: #888888; margin-bottom: 6px; }}
.logo-main-wrapper {{ display: inline-block; padding: 10px 25px; margin-bottom: 6px; }}

.logo-letter {{
    display: inline-block;
    font-size: 52px; font-family: 'SuperFuntime', sans-serif; font-weight: 400 !important;
    color: rgba(253, 210, 98, 1);
    line-height: 1;
    margin: 0 5px;
    text-shadow:
        -1px -1px 1px rgba(255,255,255,0.85),
        1px 2px 2px rgba(180,130,20,0.4),
        0 4px 8px rgba(251,192,45,0.3);
    animation: letterFloat 3s ease-in-out infinite;
}}
.logo-space {{ display: inline-block; width: 20px; }}
@keyframes letterFloat {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-5px) rotate(2deg); }}
}}

/* 모바일: 'Snack Lab' 줄바꿈 방지를 위해 글자 크기/간격 축소, 하단 문구도 축소 */
@media (max-width: 480px) {{
    .logo-letter {{ font-size: 36px; margin: 0 2px; }}
    .logo-space {{ width: 10px; }}
    .logo-bottom-text {{ font-size: 9px; letter-spacing: 1.5px; }}
}}

.logo-bottom-text {{ font-size: 11px; font-weight: 350 !important; color: #8D6E63; margin-top: 4px; letter-spacing: 2.5px; margin-bottom: 0; }}

/* 플로팅 에셋 SVG */
.float-asset {{ position: absolute; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }}
.f-l-1 {{ top: 15%; left: 5%; width: 15px; animation: floatAnim 4s ease-in-out infinite; }}
.f-l-2 {{ top: 40%; left: 12%; width: 22px; animation: floatAnim 3s ease-in-out infinite reverse; }}
.f-l-3 {{ bottom: 25%; left: 4%; width: 18px; animation: floatAnim 5s ease-in-out infinite; }}
.f-l-4 {{ bottom: 10%; left: 18%; width: 12px; animation: floatAnim 3.5s ease-in-out infinite reverse; }}
.f-r-1 {{ top: 20%; right: 8%; width: 20px; animation: floatAnim 4.5s ease-in-out infinite; }}
.f-r-2 {{ top: 50%; right: 15%; width: 14px; animation: floatAnim 3.5s ease-in-out infinite reverse; }}
.f-r-3 {{ bottom: 30%; right: 5%; width: 25px; animation: floatAnim 5.5s ease-in-out infinite; }}
.f-r-4 {{ bottom: 15%; right: 12%; width: 16px; animation: floatAnim 4s ease-in-out infinite reverse; }}

@keyframes floatAnim {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-8px) rotate(10deg); }}
}}

/* ── 공지 알림판 ── */
.notice-box {{
    padding: 11px 16px; margin: 0 -0.5rem 0.8rem;
    background: rgba(138, 221, 234, 0.12);
    border: 1px solid rgba(37, 189, 212, 0.5);
    border-radius: 12px; font-size: 12px; color: #333333;
    display: flex; align-items: center; gap: 8px;
}}
.notice-box img {{ width: 16px; height: 16px; }}

/* ── 섹션 타이틀 ── */
.sec-title {{ 
    font-size: 15px !important; 
    font-weight: 400 !important; 
    margin: 1.8rem 0 0.8rem; display: flex; align-items: center; gap: 6px; color: #8D6E63; 
}}
.sec-title img {{ width: 20px; height: 20px; }}

/* ── 카드 스타일 ── */
.snack-card, .req-card, .cpg-item, .hot-trend-box {{
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    box-shadow: none;
}}
.snack-card {{ padding: 14px; text-align: center; margin-bottom: 8px; }}
.snack-card img.snack-img {{ width: 64px; height: 64px; border-radius: 12px; object-fit: cover; background: transparent; }}
.snack-card .name {{ font-size: 13px; color: #4E342E; margin: 6px 0 2px; overflow-wrap: break-word; word-break: break-word; }}
.snack-card .price {{ font-size: 11px; color: #8D6E63; margin-bottom: 6px; }}

.req-card {{ padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
.req-card .info h4 {{ font-size: 13px; margin: 0 0 4px 0; color: #4E342E; overflow-wrap: break-word; word-break: break-word; }}
.req-card .info .meta {{ font-size: 11px; color: #8D6E63; display: flex; align-items: center; gap:4px; flex-wrap: wrap; }}

/* 비치 명단 '고정' 체크박스: 줄바꿈 없이 한 줄로 */
[class*="st-key-pin_chk_"] label {{ white-space: nowrap !important; }}
[class*="st-key-pin_chk_"] label p {{ font-size: 12px !important; white-space: nowrap !important; }}

/* 신규 간식 요청 2열 그리드 카드 */
.req-card-grid {{
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    padding: 10px 12px; margin-bottom: 6px;
}}
.req-card-grid h4 {{
    font-size: 12.5px; margin: 0 0 4px 0; color: #4E342E;
    overflow-wrap: break-word; word-break: break-word;
}}
.req-card-grid .meta {{
    font-size: 10.5px; color: #8D6E63; display: flex; align-items: center;
    flex-wrap: wrap; gap: 3px;
}}

/* '좋아요' 버튼(snack-card) / '나도' 버튼(req-card) — 모서리 더 둥글게, 폰트는 다과 이름 크기와 동일하게 */
[class*="st-key-like_"] button {{
    font-size: 13px !important;
    padding: 3px 14px !important;
    min-height: 26px !important;
    height: 26px !important;
    border-radius: 20px !important;
    width: auto !important;
}}
[class*="st-key-like_"] {{ display: flex; justify-content: center; }}
[class*="st-key-vote_"] button {{
    padding: 2px 12px !important;
    font-size: 12.5px !important;
    min-height: 24px !important;
    height: 24px !important;
    border-radius: 20px !important;
    width: auto !important;
    margin-top: 5px !important;
}}
[class*="st-key-vote_"] {{ display: flex; justify-content: center; }}

/* ── 카테고리 태그 (뱃지) ── */
.tag-container {{ display: flex; flex-wrap: nowrap; justify-content: center; gap: 3px; margin-bottom: 6px; overflow: hidden; }}
.tag {{
    display: inline-block; padding: 2px 5px; border-radius: 6px;
    font-size: 8px; font-weight: 800 !important; color: #5D4037; 
    background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(200, 200, 200, 0.3);
    white-space: nowrap;
}}

/* ── 빈 공간 ── */
.empty-zone {{ border: 1px dashed gray; border-radius: 14px; padding: 30px 20px; text-align: center; color: #999; font-size: 12.5px; background: none; }}

/* ── AI 결과 박스 ── */
.ai-result {{
    background: rgba(255, 253, 231, 0.5); border-radius: 14px; padding: 16px; margin-bottom: 10px;
    border: 1px solid rgba(251, 192, 45, 0.3);
    font-size: 12.5px; line-height: 1.7; white-space: pre-wrap; color: #4E342E;
}}
.combo-title {{ font-size: 13px; color: #4E342E; margin-bottom: 6px; }}
.combo-row {{ display: flex; justify-content: space-between; font-size: 12px; padding: 3px 0; }}
.combo-row a {{ color: #4E342E; text-decoration: underline; }}
.combo-reason {{ margin-top: 8px; color: #8D6E63; font-size: 11.5px; white-space: normal; }}

/* ── 버튼 공통 ── */
div[data-testid="stHorizontalBlock"] {{ gap: 6px; }}
.stButton > button {{
    border-radius: 8px !important; 
    background: #ffffff !important; 
    border: 1px solid rgba(0,0,0,0.12) !important;
    box-shadow: none !important;
    color: #4E342E !important; font-size: inherit !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{ background: #f8f9fa !important; }}
.stButton > button:active {{ transform: translateY(1px); }}

button[kind="primary"] {{
    background: #ffffff !important; 
    border: 1px solid rgba(0,0,0,0.12) !important;
    color: #4E342E !important;
}}
button[kind="primary"] p {{ color: #4E342E !important; }}

/* 카테고리 선택: st.pills 네이티브 위젯 사용 (자체적으로 줄바꿈/흐름 처리됨) — 살짜 더 촘촘하게만 조정 */
div[data-testid="stPills"] {{
    gap: 4px !important;
}}
div[data-testid="stPills"] button {{
    font-size: 11px !important;
    padding: 3px 12px !important;
    min-height: unset !important;
}}
div[data-testid="stPills"] button[aria-checked="true"] {{
    background: #8D6E63 !important;
    border-color: #8D6E63 !important;
    color: #ffffff !important;
}}

.form-tag-label {{
    font-size: 15px; color: #8D6E63; margin: 10px 0 5px; font-weight: 400 !important;
}}

/* 텍스트 입력창에 아주 옅은 회색 테두리 — 입력 가능한 칸이라는 걸 알 수 있게 */
div[data-baseweb="input"], div[data-baseweb="base-input"] {{
    border: 1px solid rgba(0,0,0,0.15) !important;
    border-radius: 8px !important;
}}

.field-hint {{
    display: flex; align-items: center; gap: 4px;
    font-size: 11px; color: #8D6E63; margin: 0 0 4px;
}}
.field-hint img {{ width: 13px; height: 13px; }}

/* ── HOT 다과 트렌드 큐레이션 박스 ── */
.hot-trend-box {{ padding: 12px 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }}
.hot-img {{ width: 46px; height: 46px; border-radius: 10px; object-fit: cover; flex-shrink: 0; background: #f5f5f0; }}
.hot-trend-box .hot-name {{ font-size: 14px; color: #4E342E; font-weight: 400 !important; margin-right: 6px; }}
.hot-trend-box .hot-tag {{ font-size: 11px; color: #8D6E63; }}
.hot-trend-box .hot-desc {{ font-size: 12.5px; color: #555; margin-top: 4px; }}

/* ── 월/일 선택 select box: 가로 폭 대폭 축소 (전역 row 고정과 함께 한 줄에 들어오게) ── */
[class*="st-key-notice_month_sel"], [class*="st-key-notice_day_sel"] {{
    font-size: 13px;
    max-width: 78px;
}}
[class*="st-key-notice_month_sel"] div[data-baseweb="select"],
[class*="st-key-notice_day_sel"] div[data-baseweb="select"] {{
    min-width: 0 !important;
}}

/* 신규 요청 항목 심사: 카테고리 전용 요청 줄 + 일반 제품명 체크박스 줄 폰트를 13px로 통일 */
.tag-only-req {{ font-size: 13px; color: #4E342E; padding: 6px 0; overflow-wrap: break-word; word-break: break-word; }}
.tag-only-req .hint {{ color: #999; font-size: 10.5px; margin-left: 4px; }}
[class*="st-key-del_req_"] button {{
    font-size: 10px !important;
    padding: 2px 8px !important;
    min-height: 22px !important;
    height: 22px !important;
    width: auto !important;
}}
[class*="st-key-del_req_"] {{ display: flex; justify-content: flex-end; }}
[class*="st-key-add_"] p {{ font-size: 13px !important; color: #4E342E !important; }}

.icon-inline {{ width: 14px; height: 14px; vertical-align: middle; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# API 연동
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_snack_image(name):
    try:
        client_id = st.secrets.get("NAVER_CLIENT_ID", "")
        client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
        if not client_id or client_id.startswith("여기에"): return ""
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        res = requests.get(url, headers=headers, params={"query": name, "display": 1}, timeout=5)
        if res.status_code == 200:
            items = res.json().get("items", [])
            if items: return items[0].get("image", "")
    except Exception: pass
    return ""

def search_naver_shopping(keyword, display=5):
    try:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
    except Exception:
        return None, "네이버 API 키가 설정되지 않았습니다."
    
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params = {"query": keyword, "display": display, "sort": "sim"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            results = [{
                "name": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                "price": int(item.get("lprice", 0)) if item.get("lprice") else 0,
                "image": item.get("image", ""),
                "mall": item.get("mallName", ""),
                "link": item.get("link", ""),
            } for item in data.get("items", [])[:display]]
            return results, None
        return None, f"API 오류 (HTTP {res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {str(e)}"

def naver_search_link(query):
    """개별 상품의 정확한 구매 링크 대신, 그 이름으로 네이버 쇼핑을 검색한 결과창 링크.
    Naver API의 item.link보다 안정적이고, 굳이 정확한 구매 페이지일 필요는 없다는
    요청에 따라 이 방식으로 충분함."""
    return f"https://search.shopping.naver.com/search/all?query={quote(query)}"

def call_gemini(prompt_text, mode="cart"):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return "⚠️ GEMINI_API_KEY가 설정되지 않았습니다. Streamlit Secrets를 확인해 주세요."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    try:
        res = requests.post(url, json=body, timeout=20)
    except Exception as e:
        return f"⚠️ 네트워크 오류: {str(e)}"

    if res.status_code == 429:
        return "API 오류: 3분 후 다시 시도해주세요"

    if res.status_code != 200:
        try:
            err_detail = res.json().get("error", {}).get("message", res.text[:200])
        except Exception:
            err_detail = res.text[:200]
        return f"⚠️ API 오류 (HTTP {res.status_code}): {err_detail}"

    try:
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "⚠️ 응답 형식을 해석할 수 없습니다."

def is_error_text(text):
    return text.startswith("API 오류") or text.startswith("⚠️")

# ─────────────────────────────────────────────
# Google Sheets 영구 저장소
# st.session_state는 그 브라우저 탭이 서버와 맺은 연결에서만 사는 임시 메모리라
# 앱이 재시작되거나 다른 브라우저로 접속하면 공유가 안 됨. 공지일/비치목록처럼
# "모두가 같이 보고, 재시작해도 남아있어야 하는" 데이터는 구글 시트에 저장한다.
# 시트에는 key, value 두 컬럼만 두고, value에는 JSON으로 직렬화한 값을 넣는다.
# ─────────────────────────────────────────────
PERSISTENT_KEYS = ["notice_date", "snacks", "requests", "hot_trends", "pinned_snacks", "cat_votes", "history_likes"]

@st.cache_resource
def _get_gsheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(st.secrets["GSHEET_ID"]).sheet1
        return sheet
    except Exception:
        return None

@st.cache_data(ttl=10)
def load_persistent_state():
    """구글 시트에서 모든 키를 읽어온다. 10초 캐시라서 누가 값을 바꿔도
    다른 사람 화면에는 최대 10초 정도 후에 반영된다. 시트 연결이 안 되면
    빈 딕셔너리를 반환하고, 그 경우 코드 쪽 기본값으로 동작한다."""
    sheet = _get_gsheet()
    if sheet is None:
        return {}
    try:
        rows = sheet.get_all_records()
        data = {}
        for row in rows:
            k, v = row.get("key"), row.get("value")
            if k and v:
                try:
                    data[k] = json.loads(v)
                except Exception:
                    pass
        return data
    except Exception:
        return {}

def save_persistent_key(key, value):
    """딱 한 개의 키만 구글 시트에 업데이트(있으면 갱신, 없으면 새 행 추가)하고
    캐시를 비워서 다음 읽기부터 최신값이 반영되게 한다. 실패하면 False를
    반환할 뿐 예외를 던지지 않음 — 시트 연결이 잠깐 끊겨도 앱 자체는 멈추지 않게."""
    sheet = _get_gsheet()
    if sheet is None:
        return False
    try:
        value_json = json.dumps(value, ensure_ascii=False)
        cell = sheet.find(key, in_column=1)
        if cell:
            sheet.update_cell(cell.row, 2, value_json)
        else:
            sheet.append_row([key, value_json])
        load_persistent_state.clear()
        return True
    except Exception:
        return False

def persist(key):
    """st.session_state[key]의 현재 값을 구글 시트에 저장. set은 JSON이
    안 되니 리스트로 바꿔서 저장한다."""
    value = st.session_state[key]
    if isinstance(value, set):
        value = list(value)
    ok = save_persistent_key(key, value)
    if not ok:
        st.toast("⚠️ 구글 시트 저장 실패 — 이번 변경사항이 영구 저장되지 않았어요.", icon="⚠️")

TARGET_BUDGET = 90000
MAX_BUDGET = 100000
MAX_QTY_PER_ITEM = 5

def build_cart_combos(cats, top_reqs):
    """AI에게는 '후보 상품명'만 받는다 (가격은 AI가 추측하면 늘 어긋나므로 맡기지 않음).
    실제 가격은 네이버 실검색으로 받아오고, 9만원에 최대한 가깝게(10만원은 절대 안 넘게)
    채우는 계산은 파이썬에서 직접 한다 — 그래야 산수가 항상 정확하다."""
    prompt = (
        f"탕비실에 채울 과자/음료 후보 상품명을 추천해줘. 가격이나 수량은 신경쓰지 말고 "
        f"상품명만 골라줘 (가격은 따로 실제 데이터로 확인할 거라 추측하지 않아도 됨).\n"
        f"선호도(카테고리:득표수): {cats}\n"
        f"요청 많은 품목: {top_reqs}\n"
        f"서로 다른 컨셉의 3가지 묶음으로, 각 묶음마다 후보 상품명 6~8개와 묶음 컨셉을 짧게 설명해줘.\n"
        f"다른 설명 없이 아래 JSON 형식으로만 답해:\n"
        '{"combos":[{"theme":"묶음 컨셉 한 문장","candidates":["상품명1","상품명2"]}]}\n'
        f"combos는 정확히 3개."
    )
    raw = call_gemini(prompt, mode="cart")
    if is_error_text(raw):
        return raw, None

    cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        combos_raw = data.get("combos", [])
    except Exception:
        return raw, None

    enriched = []
    for combo in combos_raw[:3]:
        # 후보별 실제 네이버 가격 조회
        priced = []
        for name in combo.get("candidates", []):
            results, _ = search_naver_shopping(name, display=1)
            if results and results[0]["price"]:
                priced.append({"name": name, "price": results[0]["price"]})
        priced.sort(key=lambda x: x["price"])

        # 1차: 싼 것부터 1개씩 담아서 10만원 안 넘게
        items_out = []
        total = 0
        for c in priced:
            if total + c["price"] <= MAX_BUDGET:
                items_out.append({"name": c["name"], "qty": 1, "price": c["price"]})
                total += c["price"]

        # 2차: 9만원에 가까워질 때까지 기존 아이템 수량을 늘려서 채움 (최대 10만원, 1개당 최대 5개)
        changed = True
        while total < TARGET_BUDGET and changed:
            changed = False
            for it in items_out:
                if it["qty"] < MAX_QTY_PER_ITEM and total + it["price"] <= MAX_BUDGET:
                    it["qty"] += 1
                    total += it["price"]
                    changed = True
                    if total >= TARGET_BUDGET:
                        break

        for it in items_out:
            it["link"] = naver_search_link(it["name"])

        enriched.append({"items": items_out, "reason": combo.get("theme", ""), "total": total})
    return None, enriched


# ─────────────────────────────────────────────
# Session State 초기화 
# ─────────────────────────────────────────────
def init_state():
    persisted = load_persistent_state()

    if "snacks" not in st.session_state:
        st.session_state.snacks = persisted.get("snacks", [])
    if "history_likes" not in st.session_state:
        st.session_state.history_likes = persisted.get("history_likes", {})
    if "pinned_snacks" not in st.session_state:
        st.session_state.pinned_snacks = set(persisted.get("pinned_snacks", []))
    if "requests" not in st.session_state:
        st.session_state.requests = persisted.get("requests", [
            {"id": 1, "name": "포카칩 어니언", "categories": ["짠맛", "스낵/칩"], "votes": 5},
            {"id": 2, "name": "마이쮸 딸기", "categories": ["단맛", "젤리/사탕"], "votes": 3},
        ])
    if "cat_votes" not in st.session_state:
        st.session_state.cat_votes = persisted.get("cat_votes", {"단맛": 35, "짠맛": 28, "매운맛": 4, "쿠키/비스킷": 15, "스낵/칩": 22, "젤리/사탕": 12, "건강한 맛": 5, "탄산음료": 14, "커피/차": 9, "주스/드링크": 6})
    if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
    if "page" not in st.session_state: st.session_state.page = "main"
    if "ai_result" not in st.session_state: st.session_state.ai_result = ""
    if "ai_combos" not in st.session_state: st.session_state.ai_combos = None
    if "naver_results" not in st.session_state: st.session_state.naver_results = []
    if "admin_naver_results" not in st.session_state: st.session_state.admin_naver_results = []
    if "search_input_val" not in st.session_state: st.session_state.search_input_val = ""
    if "user_likes" not in st.session_state: st.session_state.user_likes = set()
    if "user_votes" not in st.session_state: st.session_state.user_votes = set()
    if "selected_cats" not in st.session_state: st.session_state.selected_cats = [] 
    if "cat_pills" not in st.session_state: st.session_state.cat_pills = []
    
    if "notice_date" not in st.session_state:
        st.session_state.notice_date = persisted.get("notice_date", "7월 1일")
    if "hot_trends" not in st.session_state:
        st.session_state.hot_trends = persisted.get("hot_trends", [])
    if "hot_preview" not in st.session_state: st.session_state.hot_preview = None

CATEGORIES = ["단맛", "짠맛", "매운맛", "쿠키/비스킷", "스낵/칩", "젤리/사탕", "건강한 맛", "탄산음료", "커피/차", "주스/드링크"]

init_state()

# ═════════════════════════════════════════════
# 레이아웃 렌더링 파트
# ═════════════════════════════════════════════

col_nav, col_empty = st.columns([3, 2])
with col_nav:
    nav_cols = st.columns(2)
    with nav_cols[0]:
        if st.button("HOME", key="btn_nav_home", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
    with nav_cols[1]:
        if st.button("MANAGEMENT", key="btn_nav_admin", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()

if st.session_state.page == "main":

    html_banner = f"""<div class="logo-banner">
<img class="float-asset f-l-1" src="{svg_astroid}">
<img class="float-asset f-l-2" src="{svg_badge}">
<img class="float-asset f-l-3" src="{svg_dot}">
<img class="float-asset f-l-4" src="{svg_sparkles}">
<img class="float-asset f-r-1" src="{svg_sparkles}">
<img class="float-asset f-r-2" src="{svg_astroid}">
<img class="float-asset f-r-3" src="{svg_badge}">
<img class="float-asset f-r-4" src="{svg_dot}">
<div class="logo-sub">정책기획팀</div>
<div class="logo-main-wrapper">{LOGO_LETTERS_HTML}</div>
<p class="logo-bottom-text">최적의 간식조합 찾기</p>
</div>"""
    st.markdown(html_banner, unsafe_allow_html=True)

    html_notice = f"""<div class="notice-box">
<img src="{svg_megaphone}"> 다음 다과 입고 예정일은 {st.session_state.notice_date}입니다. 필요한 간식은 아래에 요청해 주세요.
</div>"""
    st.markdown(html_notice, unsafe_allow_html=True)

    if st.session_state.hot_trends:
        st.markdown(f'<div class="sec-title"><img src="{svg_heart}"> HOT 다과 트렌드 큐레이션</div>', unsafe_allow_html=True)
        for ht in st.session_state.hot_trends:
            img_html = f'<img class="hot-img" src="{ht["image"]}">' if ht.get("image") else ""
            st.markdown(f"""
            <div class="hot-trend-box">
                {img_html}
                <div>
                    <span class="hot-name">{ht['name']}</span>
                    <span class="hot-tag">{ht['tag']}</span>
                    <div class="hot-desc">{ht['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Section 1: 이달의 다과 피드백 ──
    st.markdown(f'<div class="sec-title"><img src="{svg_candy}"> 이달의 다과 피드백</div>', unsafe_allow_html=True)

    if not st.session_state.snacks:
        st.markdown('<div class="empty-zone">현재 비치된 다과 항목이 없습니다.<br>관리자 페이지에서 리스트를 업데이트해 주세요.</div>', unsafe_allow_html=True)
    else:
        snack_cols = st.columns(2)
        for i, s in enumerate(st.session_state.snacks):
            with snack_cols[i % 2]:
                pin_icon = f'<img class="icon-inline" src="{svg_pin}">' if s["id"] in st.session_state.pinned_snacks else ""
                tag_html = '<div class="tag-container">' + "".join([f'<span class="tag">#{c}</span>' for c in s["categories"]]) + '</div>'
                
                st.markdown(f"""<div class="snack-card">
                    <img class="snack-img" src="{s['image']}" onerror="this.src='https://placehold.co/120x120/FFF9C4/FBC02D?text=Snack'">
                    <div class="name">{pin_icon} {s['name']}</div>
                    <div class="price">{s['price']:,}원</div>
                    <div class="price"><img class="icon-inline" src="{svg_thumbs_up}"> {s['likes']}명이 좋아요</div>
                    {tag_html}
                </div>""", unsafe_allow_html=True)
                
                has_liked = s["id"] in st.session_state.user_likes
                # '나도' 버튼처럼 카운트는 카드 쪽에 따로 표시하고, 버튼 라벨은 단순하게
                if st.button("좋아요 취소" if has_liked else "좋아요", key=f"like_{s['id']}"):
                    if has_liked:
                        s["likes"] -= 1
                        st.session_state.user_likes.remove(s["id"])
                    else:
                        s["likes"] += 1
                        st.session_state.user_likes.add(s["id"])
                    persist("snacks")
                    st.rerun()

    # ── Section 2: 신규 간식 요청 (이달의 다과 피드백처럼 2열 그리드) ──
    st.markdown(f'<div class="sec-title"><img src="{svg_candy}"> 신규 간식 요청</div>', unsafe_allow_html=True)

    sorted_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)
    req_cols = st.columns(2)
    for i, r in enumerate(sorted_reqs):
        with req_cols[i % 2]:
            tag_html = "".join([f'<span class="tag" style="margin-right:3px;">#{c}</span>' for c in r["categories"]])
            st.markdown(f"""<div class="req-card-grid">
                <h4>{r['name']}</h4>
                <div class="meta">{tag_html} · <img class="icon-inline" src="{svg_thumbs_up}"> {r['votes']}명 요청</div>
            </div>""", unsafe_allow_html=True)
            has_voted = r["id"] in st.session_state.user_votes
            if st.button("취소" if has_voted else "나도", key=f"vote_{r['id']}"):
                if has_voted:
                    r["votes"] -= 1
                    st.session_state.user_votes.remove(r["id"])
                else:
                    r["votes"] += 1
                    st.session_state.user_votes.add(r["id"])
                persist("requests")
                st.rerun()

    # ── 새 간식 요청 등록 폼 ──
    st.markdown("---")
    st.markdown(f'<div class="sec-title"><img src="{svg_cup_soda}"> 새 간식 요청 등록</div>', unsafe_allow_html=True)

    with st.form(key="search_form", clear_on_submit=False):
        req_name = st.text_input("원하는 다과/음료명을 입력하세요", placeholder="예: 코카콜라 제로", key="req_name_input")
        search_clicked = st.form_submit_button("🔍 검색하기", use_container_width=True)

    if search_clicked:
        st.session_state.naver_results = [] 
        if not req_name: st.warning("제품명을 입력한 뒤 검색해 주세요.")
        else:
            st.session_state.search_input_val = req_name
            with st.spinner("상품 데이터를 검색 중입니다..."):
                results, err = search_naver_shopping(req_name)
                if err: st.error(err)
                elif results: st.session_state.naver_results = results

    st.markdown('<div class="form-tag-label"># 카테고리 태그 지정 (중복 선택 가능)</div>', unsafe_allow_html=True)
    pills_selection = st.pills(
        "카테고리 선택",
        CATEGORIES,
        selection_mode="multi",
        format_func=lambda c: f"#{c}",
        label_visibility="collapsed",
        key="cat_pills",
    )
    st.session_state.selected_cats = list(pills_selection) if pills_selection else []

    if st.session_state.get("naver_results"):
        st.caption("선택하면 바로 신규 간식 요청에 등록됩니다.")
        for ci, item in enumerate(st.session_state.naver_results):
            col_i1, col_i2 = st.columns([4, 1])
            with col_i1:
                st.markdown(f"""<div class="req-card" style="margin-bottom:4px;">
                    <img src="{item['image']}" width="40" style="border-radius:6px; margin-right:10px;">
                    <div style="font-size:12px;">{item['name'][:30]}</div>
                </div>""", unsafe_allow_html=True)
            with col_i2:
                if st.button("선택", key=f"nv_{ci}"):
                    existing = next((r for r in st.session_state.requests if r["name"] == item["name"]), None)
                    cats_now = list(st.session_state.selected_cats)
                    if existing:
                        existing["votes"] += 1
                    else:
                        st.session_state.requests.append({"id": int(time.time() * 1000), "name": item["name"], "categories": cats_now, "votes": 1})
                    persist("requests")
                    st.session_state.selected_naver = None
                    st.session_state.selected_cats = []
                    st.session_state.cat_pills = []
                    st.session_state.search_input_val = ""
                    st.session_state.naver_results = []
                    st.toast(f"'{item['name']}' 요청이 등록되었습니다.")
                    st.rerun()

    st.write("") 
    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 2, 1.5])
    with col_btn2:
        if st.button("제출!", use_container_width=True, type="primary"):
            sel_item = st.session_state.get("selected_naver")
            name = sel_item["name"] if sel_item else st.session_state.search_input_val
            cats_selected = list(st.session_state.selected_cats)
            if not name and not cats_selected:
                st.warning("다과명을 입력하거나 카테고리를 하나 이상 선택해 주세요.")
            else:
                if not name:
                    name = " ".join(f"#{c}" for c in cats_selected)
                existing = next((r for r in st.session_state.requests if r["name"] == name), None)
                if existing: existing["votes"] += 1
                else:
                    st.session_state.requests.append({"id": int(time.time() * 1000), "name": name, "categories": cats_selected, "votes": 1})
                persist("requests")
                st.session_state.selected_naver = None
                st.session_state.selected_cats = []
                st.session_state.cat_pills = []
                st.session_state.search_input_val = ""
                st.session_state.naver_results = []
                st.rerun()

# ═════════════════════════════════════════════
# 관리자 페이지
# ═════════════════════════════════════════════
elif st.session_state.page == "admin":

    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <div class="logo-sub">인프라 관리 시스템</div>
        <div style="font-size:24px; color:#4E342E;">Snack Lab Admin</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.admin_auth:
        st.markdown(f'<div class="sec-title"><img src="{svg_user_key}"> 관리자 모드 개방</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-hint"><img src="{svg_lock}"> 보안 접속</div>', unsafe_allow_html=True)
        admin_pw = st.text_input("액세스 패스워드", type="password", key="admin_pw_input")
        col_a1, col_a2, col_a3 = st.columns([1.5, 2, 1.5])
        with col_a2:
            if st.button("인증 실행", use_container_width=True, type="primary"):
                if admin_pw == st.secrets.get("ADMIN_PASSWORD", "1234"):
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("액세스 권한 암호가 올바르지 않습니다.")
    else:
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_pen}"> 홈 화면 공지 및 트렌드 설정</div>', unsafe_allow_html=True)

        m = re.match(r"(\d+)월\s*(\d+)일", st.session_state.notice_date)
        default_month = int(m.group(1)) if m else 7
        default_day = int(m.group(2)) if m else 1
        col_d1, col_d2, col_d_empty = st.columns([1, 1, 3])
        with col_d1:
            sel_month = st.selectbox("월", list(range(1, 13)), index=default_month - 1, key="notice_month_sel")
        with col_d2:
            sel_day = st.selectbox("일", list(range(1, 32)), index=default_day - 1, key="notice_day_sel")
        if st.button("예정일 업데이트"):
            st.session_state.notice_date = f"{sel_month}월 {sel_day}일"
            persist("notice_date")
            st.toast("입고 예정일이 수정되었습니다.")

        st.markdown(f'<div class="sec-title"><img src="{svg_heart}"> HOT 다과 트렌드 큐레이션 추가</div>', unsafe_allow_html=True)
        hot_name = st.text_input("다과 이름 입력 (자동생성 트리거)")

        if st.button("미리보기 생성", use_container_width=True):
            if not hot_name:
                st.warning("다과 이름을 입력해 주세요.")
            else:
                with st.spinner("AI 멘트 작성 및 이미지 검색 중..."):
                    prompt = f"회사 탕비실 다과 '{hot_name}'을/를 직원들에게 추천하는 해시태그 1개와 짧은 홍보 문구(25자 이내)를 작성해줘. 형식은 반드시 '태그|문구' 기호로 구분지어 대답해."
                    result = call_gemini(prompt, mode="trend")
                    if is_error_text(result):
                        st.error(result)
                        st.session_state.hot_preview = None
                    else:
                        try:
                            t_tag, t_desc = result.split("|", 1)
                        except Exception:
                            t_tag, t_desc = "#요즘대세", result
                        img_url = fetch_snack_image(hot_name)
                        st.session_state.hot_preview = {"name": hot_name, "tag": t_tag.strip(), "desc": t_desc.strip(), "image": img_url}

        # 홈 화면에 바로 올리기 전에, 검색이 잘 됐는지(특히 이미지) 미리 확인하는 단계
        if st.session_state.get("hot_preview"):
            p = st.session_state.hot_preview
            st.caption("아래는 홈 화면에 실제로 표시될 미리보기입니다. 확인 후 추가해 주세요.")
            if p.get("image"):
                img_html = f'<img class="hot-img" src="{p["image"]}">'
            else:
                img_html = '<div class="hot-img" style="display:flex;align-items:center;justify-content:center;color:#bbb;font-size:9px;">이미지 없음</div>'
            st.markdown(f"""
            <div class="hot-trend-box">
                {img_html}
                <div>
                    <span class="hot-name">{p['name']}</span>
                    <span class="hot-tag">{p['tag']}</span>
                    <div class="hot-desc">{p['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if not p.get("image"):
                st.warning("이미지 검색 결과가 없습니다. 이름을 다르게 입력해서 다시 미리보기 해보시거나, 이미지 없이 추가할 수 있습니다.")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("✅ 홈에 추가", use_container_width=True, type="primary"):
                    st.session_state.hot_trends.append(p)
                    persist("hot_trends")
                    st.session_state.hot_preview = None
                    st.toast("트렌드 큐레이션이 홈에 추가되었습니다.")
                    st.rerun()
            with col_p2:
                if st.button("취소", use_container_width=True):
                    st.session_state.hot_preview = None
                    st.rerun()

        if st.button("전체 초기화 (삭제)", use_container_width=True):
            st.session_state.hot_trends = []
            persist("hot_trends")

        st.markdown("---")
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_check}"> 실시간 탕비실 비치 품목 제어</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="field-hint"><img src="{svg_search}"> 다과 직접 검색 후 추가</div>', unsafe_allow_html=True)
        admin_search_name = st.text_input("다과/음료명 검색", key="admin_search_input", placeholder="예: 포카칩 어니언", label_visibility="collapsed")

        # 검색창을 비우면 즉시 이전 검색 결과를 초기화 (이 입력란은 폼이 아니라서 매 입력마다 rerun됨)
        if not admin_search_name:
            st.session_state.admin_naver_results = []

        if st.button("🔍 검색하기", key="admin_search_btn", use_container_width=True):
            st.session_state.admin_naver_results = []  # 이전 결과를 먼저 비워서, 검색이 실패해도 다음 재검색이 깔끔하게 되도록
            if not admin_search_name:
                st.warning("검색할 제품명을 입력해 주세요.")
            else:
                with st.spinner("상품 데이터를 검색 중입니다..."):
                    results, err = search_naver_shopping(admin_search_name)
                    if err:
                        st.error(err)
                    elif results:
                        st.session_state.admin_naver_results = results
                    else:
                        st.info("검색 결과가 없습니다. 다른 검색어로 다시 시도해 보세요.")

        if st.session_state.get("admin_naver_results"):
            for ci, item in enumerate(st.session_state.admin_naver_results):
                col_ai1, col_ai2 = st.columns([4, 1])
                with col_ai1:
                    st.markdown(f"""<div class="req-card" style="margin-bottom:4px;">
                        <img src="{item['image']}" width="40" style="border-radius:6px; margin-right:10px;">
                        <div style="font-size:12px;">{item['name'][:30]}</div>
                    </div>""", unsafe_allow_html=True)
                with col_ai2:
                    if st.button("추가", key=f"admin_nv_{ci}"):
                        if not any(s["name"] == item["name"] for s in st.session_state.snacks):
                            st.session_state.snacks.append({
                                "id": int(time.time() * 1000) + ci,
                                "name": item["name"],
                                "categories": [],
                                "image": item["image"],
                                "price": item["price"] if item["price"] else 2000,
                                "likes": 0,
                            })
                            persist("snacks")
                            st.toast(f"'{item['name']}' 비치 목록에 추가되었습니다.")
                        st.session_state.admin_naver_results = []
                        st.rerun()

        st.markdown("---")
        if not st.session_state.snacks: st.caption("현재 비치된 다과 인프라가 전무합니다.")
        else:
            for s in st.session_state.snacks:
                col_m1, col_m2 = st.columns([2.4, 1.3])
                with col_m1:
                    st.markdown(f"""<div class="req-card" style="margin-bottom:8px;"><div class="info">
                        <h4>{s['name']}</h4>
                        <div class="meta"><img class="icon-inline" src="{svg_thumbs_up}"> {s['likes']}표 · {s['price']:,}원</div>
                    </div></div>""", unsafe_allow_html=True)
                with col_m2:
                    is_pinned = s["id"] in st.session_state.pinned_snacks
                    new_pinned = st.checkbox("📌 고정", value=is_pinned, key=f"pin_chk_{s['id']}")
                    if new_pinned != is_pinned:
                        if new_pinned: st.session_state.pinned_snacks.add(s["id"])
                        else: st.session_state.pinned_snacks.discard(s["id"])
                        persist("pinned_snacks")

        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        if st.button("비치 명단 업데이트", use_container_width=True):
            for s in st.session_state.snacks: st.session_state.history_likes[s["name"]] = max(s["likes"], st.session_state.history_likes.get(s["name"], 0))
            st.session_state.snacks = [s for s in st.session_state.snacks if s["id"] in st.session_state.pinned_snacks]
            persist("history_likes")
            persist("snacks")
            st.rerun()

        st.markdown("---")
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_pen}"> 신규 요청 항목 심사 및 입고 처리</div>', unsafe_allow_html=True)
        reqs_to_add = []
        for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True):
            is_tag_only = r["name"].strip().startswith("#")
            if is_tag_only:
                col_t1, col_t2 = st.columns([4.6, 0.9])
                with col_t1:
                    st.markdown(f'<div class="tag-only-req">{r["name"]} - {r["votes"]}명 동의 <span class="hint">(카테고리 전용 요청)</span></div>', unsafe_allow_html=True)
                with col_t2:
                    if st.button("삭제", key=f"del_req_{r['id']}"):
                        st.session_state.requests = [x for x in st.session_state.requests if x["id"] != r["id"]]
                        persist("requests")
                        st.rerun()
            else:
                if st.checkbox(f"{r['name']} - {r['votes']}명 동의", key=f"add_{r['id']}"): reqs_to_add.append(r)

        if st.button("선택 다과 입고", use_container_width=True, type="primary"):
            count = 0
            for r in reqs_to_add:
                if not any(s["name"] == r["name"] for s in st.session_state.snacks):
                    st.session_state.snacks.append({"id": int(time.time() * 1000) + count, "name": r["name"], "categories": r["categories"], "image": fetch_snack_image(r["name"]), "price": 2000, "likes": 0})
                    count += 1
            st.session_state.requests = [r for r in st.session_state.requests if r["id"] not in [r_add["id"] for r_add in reqs_to_add]]
            persist("snacks")
            persist("requests")
            st.rerun()

        st.markdown("---")
        st.markdown(f'<div class="sec-title"><img src="{svg_cup_soda}"> AI 10만원 최적 장바구니 자동 빌더</div>', unsafe_allow_html=True)

        if st.button("추천 조합 시뮬레이션 시작", use_container_width=True, type="primary"):
            cats = st.session_state.cat_votes
            top_reqs = [r["name"] for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)[:5]]
            with st.spinner("AI가 후보를 추천하고, 실제 가격으로 9만원에 맞춰 채우는 중입니다..."):
                err, combos = build_cart_combos(cats, top_reqs)
            if err:
                st.session_state.ai_result = err
                st.session_state.ai_combos = None
            else:
                st.session_state.ai_combos = combos
                st.session_state.ai_result = ""

        if st.session_state.ai_result:
            if is_error_text(st.session_state.ai_result):
                st.error(st.session_state.ai_result)
            else:
                st.markdown(f'<div class="ai-result">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

        if st.session_state.ai_combos:
            for idx, combo in enumerate(st.session_state.ai_combos, start=1):
                rows = ""
                for it in combo["items"]:
                    line_price = f'{it["price"] * it["qty"]:,}원'
                    name_html = f'<a href="{it["link"]}" target="_blank">{it["name"]} ×{it["qty"]}</a>'
                    rows += f'<div class="combo-row"><span>{name_html}</span><span>{line_price}</span></div>'
                st.markdown(f"""<div class="ai-result">
                    <div class="combo-title">조합 {idx} · 총 {combo["total"]:,}원</div>
                    {rows}
                    <div class="combo-reason">{combo['reason']}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_l1, col_l2, col_l3 = st.columns([1.5, 2, 1.5])
        with col_l2:
            if st.button("세션 로그아웃", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()
