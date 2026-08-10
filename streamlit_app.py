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

svg_astroid  = load_svg("astroid.svg")
svg_badge    = load_svg("badge.svg")
svg_dot      = load_svg("dot.svg")
svg_sparkles = load_svg("sparkles.svg")
svg_megaphone = load_svg("megaphone.svg")
svg_candy    = load_svg("candy.svg")
svg_cup_soda = load_svg("cup-soda.svg")
svg_thumbs_up = load_svg("thumbs-up.svg")
svg_user_key = load_svg("user-round-key.svg")
svg_clip_pen = load_svg("clipboard-pen.svg")
svg_clip_check = load_svg("clipboard-check.svg")
svg_pin      = load_svg("pin.svg")
svg_search   = load_svg("search.svg")
svg_lock     = load_svg("lock.svg")

# ─────────────────────────────────────────────
# 로고 글자별 스큐어모피즘 + 플로팅
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
    background: transparent; height: 0 !important;
    min-height: 0 !important; pointer-events: none;
}}
div[data-testid="stToolbar"] {{ display: none !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}

div[data-testid="stHorizontalBlock"] {{
    flex-direction: row !important; flex-wrap: nowrap !important;
}}
div[data-testid="stHorizontalBlock"] > div {{ min-width: 0 !important; }}

/* ── 네비게이션 ── */
[class*="st-key-btn_nav_"][class*="st-key-btn_nav_"] {{
    overflow: visible !important; min-width: 0 !important;
}}
[class*="st-key-btn_nav_"][class*="st-key-btn_nav_"] button {{
    font-size: 9px !important; padding: 1px 5px !important;
    min-height: 22px !important; height: 22px !important; line-height: 22px !important;
    background: transparent !important; border: none !important; outline: none !important;
    box-shadow: none !important; color: #475569 !important; border-radius: 0 !important;
    white-space: nowrap !important; width: auto !important; min-width: 0 !important;
}}
[class*="st-key-btn_nav_"][class*="st-key-btn_nav_"] button:hover {{ text-decoration: underline !important; }}
[class*="st-key-btn_nav_"][class*="st-key-btn_nav_"] button:focus {{ outline: none !important; box-shadow: none !important; border: none !important; }}
[class*="st-key-btn_nav_"][class*="st-key-btn_nav_"] button:active {{ transform: none !important; }}
@media (max-width: 380px) {{
    [class*="st-key-btn_nav_"][class*="st-key-btn_nav_"] button {{ font-size: 7.5px !important; padding: 1px 3px !important; }}
}}
[class*="st-key-nav_row"][class*="st-key-nav_row"] div[data-testid="stHorizontalBlock"] {{
    gap: 4px !important; justify-content: center !important;
}}

/* ── 로고 ── */
.logo-banner {{
    position: relative; text-align: center; padding: 30px 20px;
    background: rgba(255,255,255,0.6); border: none;
    border-radius: 20px; margin: 0 -1rem 1.2rem; overflow: hidden;
}}
.logo-sub {{ font-size: 12px; font-weight: 300 !important; color: #888888; margin-bottom: 6px; }}
.logo-main-wrapper {{ display: inline-block; padding: 10px 25px; margin-bottom: 6px; }}
.logo-letter {{
    display: inline-block;
    font-size: 52px; font-family: 'SuperFuntime', sans-serif; font-weight: 400 !important;
    color: rgba(253, 210, 98, 1); line-height: 1; margin: 0 5px;
    text-shadow: -1px -1px 1px rgba(255,255,255,0.85), 1px 2px 2px rgba(180,130,20,0.4), 0 4px 8px rgba(251,192,45,0.3);
    animation: letterFloat 3s ease-in-out infinite;
}}
.logo-space {{ display: inline-block; width: 20px; }}
@keyframes letterFloat {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-5px) rotate(2deg); }}
}}
@media (max-width: 480px) {{
    .logo-letter {{ font-size: 36px; margin: 0 2px; }}
    .logo-space {{ width: 10px; }}
    .logo-bottom-text {{ font-size: 9px; letter-spacing: 1.5px; }}
}}
.logo-bottom-text {{ font-size: 11px; font-weight: 300 !important; color: #8D6E63; margin-top: 4px; letter-spacing: 2.5px; margin-bottom: 0; }}

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
    display: flex; align-items: flex-start; gap: 8px;
}}
.notice-box img {{ width: 16px; height: 16px; flex-shrink: 0; margin-top: 1px; }}
.notice-text {{ white-space: pre-wrap; line-height: 1.6; }}

/* ── 섹션 타이틀 ── */
.sec-title {{
    font-size: 15px !important; font-weight: 400 !important;
    margin: 1.8rem 0 0.8rem; display: flex; align-items: center; gap: 6px; color: #8D6E63;
}}
.sec-title img {{ width: 20px; height: 20px; }}

/* ── 카드 ── */
.snack-card, .req-card, .cpg-item {{
    background: #ffffff; border: 1px solid rgba(0,0,0,0.12);
    border-radius: 8px; box-shadow: none;
}}
.snack-card {{ padding: 14px; text-align: center; margin-bottom: 8px; }}
.snack-card img.snack-img {{ width: 64px; height: 64px; border-radius: 12px; object-fit: cover; background: transparent; }}
.snack-card .name {{ font-size: 13px; color: #4E342E; margin: 6px 0 2px; overflow-wrap: break-word; word-break: break-word; }}
.snack-card .price {{ font-size: 11px; color: #8D6E63; margin-bottom: 6px; }}

.req-card {{ padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
.req-card .info h4 {{ font-size: 13px; margin: 0 0 4px 0; color: #4E342E; overflow-wrap: break-word; word-break: break-word; }}
.req-card .info .meta {{ font-size: 11px; color: #8D6E63; display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }}

[class*="st-key-pin_chk_"][class*="st-key-pin_chk_"] label {{ white-space: nowrap !important; }}
[class*="st-key-pin_chk_"][class*="st-key-pin_chk_"] label p {{ font-size: 12px !important; white-space: nowrap !important; }}

.req-card-grid {{
    background: #ffffff; border: 1px solid rgba(0,0,0,0.12);
    border-radius: 8px; padding: 10px 12px; margin-bottom: 6px;
}}
.req-card-grid h4 {{ font-size: 12.5px; margin: 0 0 4px 0; color: #4E342E; overflow-wrap: break-word; word-break: break-word; }}
.req-card-grid .meta {{ font-size: 10.5px; color: #8D6E63; display: flex; align-items: center; flex-wrap: wrap; gap: 3px; }}

/* ── 좋아요/나도/선택 버튼 — 공통 버튼(.stButton)보다 특이도 높게 두 번 반복 ── */
[class*="st-key-like_"][class*="st-key-like_"] button {{
    font-size: 12.5px !important; padding: 3px 14px !important;
    min-height: 26px !important; height: 26px !important;
    border-radius: 6px !important; width: auto !important;
}}
[class*="st-key-like_"][class*="st-key-like_"] {{ display: flex; justify-content: center; }}
[class*="st-key-vote_"][class*="st-key-vote_"] button {{
    font-size: 12.5px !important; padding: 2px 12px !important;
    min-height: 24px !important; height: 24px !important;
    border-radius: 6px !important; width: auto !important; margin-top: 5px !important;
}}
[class*="st-key-vote_"][class*="st-key-vote_"] {{ display: flex; justify-content: center; }}
[class*="st-key-nv_"][class*="st-key-nv_"] button {{
    font-size: 12.5px !important; border-radius: 6px !important;
}}
/* 홈 요청 개별 삭제 버튼 — 작고 눈에 덜 띄게 */
[class*="st-key-del_home_req_"][class*="st-key-del_home_req_"] button {{
    font-size: 9px !important; padding: 1px 6px !important;
    min-height: 18px !important; height: 18px !important;
    border-radius: 4px !important; width: auto !important;
    color: #aaa !important; border-color: rgba(0,0,0,0.08) !important;
}}
[class*="st-key-del_home_req_"][class*="st-key-del_home_req_"] {{ display: flex; justify-content: flex-end; }}

/* ── 태그 ── */
.tag-container {{ display: flex; flex-wrap: nowrap; justify-content: center; gap: 3px; margin-bottom: 6px; overflow: hidden; }}
.tag {{
    display: inline-block; padding: 2px 5px; border-radius: 6px;
    font-size: 8px; font-weight: 800 !important; color: #5D4037;
    background: rgba(255,255,255,0.6); border: 1px solid rgba(200,200,200,0.3); white-space: nowrap;
}}

.empty-zone {{ border: 1px dashed gray; border-radius: 14px; padding: 30px 20px; text-align: center; color: #999; font-size: 12.5px; background: none; }}

/* ── 버튼 공통 ── */
div[data-testid="stHorizontalBlock"] {{ gap: 6px; }}
.stButton > button {{
    border-radius: 8px !important; background: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.12) !important; box-shadow: none !important;
    color: #4E342E !important; font-size: inherit !important; transition: all 0.2s ease !important;
}}
.stButton > button:hover {{ background: #f8f9fa !important; }}
.stButton > button:active {{ transform: translateY(1px); }}
button[kind="primary"] {{
    background: #ffffff !important; border: 1px solid rgba(0,0,0,0.12) !important; color: #4E342E !important;
}}
button[kind="primary"] p {{ color: #4E342E !important; }}

/* ── st.pills (카테고리 선택) ── */
div[data-testid="stPills"] {{ gap: 4px !important; }}
div[data-testid="stPills"] button {{ font-size: 11px !important; padding: 3px 12px !important; min-height: unset !important; }}
div[data-testid="stPills"] button[aria-checked="true"] {{
    background: #8D6E63 !important; border-color: #8D6E63 !important; color: #ffffff !important;
}}

.form-tag-label {{ font-size: 15px; color: #8D6E63; margin: 10px 0 5px; font-weight: 400 !important; }}

.or-divider {{
    display: flex; align-items: center; gap: 10px;
    margin: 16px 0 6px; color: #999; font-size: 11px;
}}
.or-divider span {{ flex: 1; height: 1px; background: rgba(0,0,0,0.12); }}

div[data-baseweb="input"], div[data-baseweb="base-input"] {{
    border: 1px solid rgba(0,0,0,0.15) !important; border-radius: 8px !important;
}}

.field-hint {{
    display: flex; align-items: center; gap: 4px;
    font-size: 11px; color: #8D6E63; margin: 0 0 4px;
}}
.field-hint img {{ width: 13px; height: 13px; }}

/* ── 월/일 selectbox ── */
[class*="st-key-notice_month_sel"][class*="st-key-notice_month_sel"],
[class*="st-key-notice_day_sel"][class*="st-key-notice_day_sel"] {{
    font-size: 13px; max-width: 78px;
}}
[class*="st-key-notice_month_sel"][class*="st-key-notice_month_sel"] div[data-baseweb="select"],
[class*="st-key-notice_day_sel"][class*="st-key-notice_day_sel"] div[data-baseweb="select"] {{
    min-width: 0 !important;
}}

/* ── 신규 요청 심사 ── */
.tag-only-req {{ font-size: 13px; color: #4E342E; padding: 6px 0; overflow-wrap: break-word; word-break: break-word; }}
.tag-only-req .hint {{ color: #999; font-size: 10.5px; margin-left: 4px; }}
[class*="st-key-del_req_"][class*="st-key-del_req_"] button {{
    font-size: 10px !important; padding: 2px 8px !important;
    min-height: 22px !important; height: 22px !important; width: auto !important;
}}
[class*="st-key-del_req_"][class*="st-key-del_req_"] {{ display: flex; justify-content: flex-end; }}
[class*="st-key-add_"][class*="st-key-add_"] p {{ font-size: 13px !important; color: #4E342E !important; }}

/* 비치 품목 개별 삭제 버튼 */
[class*="st-key-del_snack_"][class*="st-key-del_snack_"] button {{
    font-size: 10px !important; padding: 2px 8px !important;
    min-height: 22px !important; height: 22px !important;
    width: auto !important; color: #999 !important; border-color: rgba(0,0,0,0.08) !important;
}}

.icon-inline {{ width: 14px; height: 14px; vertical-align: middle; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# API 연동 (Google Custom Search)
# ─────────────────────────────────────────────
def search_naver_shopping(keyword, display=5):
    try:
        api_key = st.secrets["GOOGLE_SEARCH_API_KEY"]
        cx = st.secrets["GOOGLE_SEARCH_CX"]
    except Exception:
        return None, "Google Search API 키가 secrets에 없습니다."
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": keyword, "num": display, "searchType": "image", "imgType": "photo", "safe": "active"}
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            results = []
            for item in res.json().get("items", [])[:display]:
                results.append({
                    "name": item.get("title", keyword),
                    "image": item.get("link", ""),
                    "mall": item.get("displayLink", ""),
                    "link": item.get("image", {}).get("contextLink", ""),
                    "price": 0,
                })
            return results, None
        return None, f"API 오류 (HTTP {res.status_code}): {res.text[:300]}"
    except Exception as e:
        return None, f"네트워크 오류: {str(e)}"


# ─────────────────────────────────────────────
# Google Sheets 영구 저장소
# ─────────────────────────────────────────────
@st.cache_resource
def _get_gsheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        return gc.open_by_key(st.secrets["GSHEET_ID"]).sheet1
    except Exception as e:
        return None

def load_persistent_state():
    sheet = _get_gsheet()
    if sheet is None: return {}
    try:
        rows = sheet.get_all_records()
        data = {}
        for row in rows:
            k, v = row.get("key"), row.get("value")
            if k and v:
                try: data[k] = json.loads(v)
                except Exception: pass
        return data
    except Exception:
        return {}

def save_persistent_key(key, value):
    sheet = _get_gsheet()
    if sheet is None: return False
    try:
        value_json = json.dumps(value, ensure_ascii=False)
        cell = sheet.find(key, in_column=1)
        if cell: sheet.update_cell(cell.row, 2, value_json)
        else: sheet.append_row([key, value_json])
        load_persistent_state.clear()
        return True
    except Exception:
        return False

MAX_LIST_ENTRIES = {"requests": 200}

def persist(key):
    value = st.session_state[key]
    if isinstance(value, set):
        value = list(value)
    if key in MAX_LIST_ENTRIES and isinstance(value, list) and len(value) > MAX_LIST_ENTRIES[key]:
        cap = MAX_LIST_ENTRIES[key]
        value = sorted(value, key=lambda x: x.get("votes", 0), reverse=True)[:cap]
        st.session_state[key] = value
    ok = save_persistent_key(key, value)
    if not ok:
        st.toast("⚠️ 구글 시트 저장 실패 — 이번 변경사항이 영구 저장되지 않았어요.", icon="⚠️")


# ─────────────────────────────────────────────
# Session State 초기화
# ─────────────────────────────────────────────
def init_state():
    persisted = load_persistent_state()
    has_sheets = bool(persisted)  # Sheets에서 실제로 데이터를 가져왔는지

    # Sheets 데이터가 있으면 항상 최신 값으로 덮어쓰기, 없으면 기본값
    def _load(key, default):
        if has_sheets:
            return persisted.get(key, default)
        if key not in st.session_state:
            return default
        return st.session_state[key]

    st.session_state.snacks = _load("snacks", [])
    st.session_state.history_likes = _load("history_likes", {})
    st.session_state.pinned_snacks = set(_load("pinned_snacks", []))
    st.session_state.requests = _load("requests", [
        {"id": 1, "name": "포카칩 어니언", "categories": ["짠맛", "스낵/칩"], "votes": 5},
        {"id": 2, "name": "마이쮸 딸기", "categories": ["단맛", "젤리/사탕"], "votes": 3},
    ])
    st.session_state.cat_votes = _load("cat_votes", {
        "단맛": 35, "짠맛": 28, "매운맛": 4, "쿠키/비스킷": 15,
        "스낵/칩": 22, "젤리/사탕": 12, "건강한 맛": 5,
        "탄산음료": 14, "커피/차": 9, "주스/드링크": 6,
    })
    st.session_state.notice_date = _load("notice_date", "7월 1일")
    st.session_state.notice_extra = _load("notice_extra", "")

    if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
    if "page" not in st.session_state: st.session_state.page = "main"
    if "naver_results" not in st.session_state: st.session_state.naver_results = []
    if "admin_naver_results" not in st.session_state: st.session_state.admin_naver_results = []
    if "search_input_val" not in st.session_state: st.session_state.search_input_val = ""
    if "user_likes" not in st.session_state: st.session_state.user_likes = set()
    if "user_votes" not in st.session_state: st.session_state.user_votes = set()
    if "selected_cats" not in st.session_state: st.session_state.selected_cats = []
    if "cat_pills" not in st.session_state: st.session_state.cat_pills = []
    # cat_pills는 위젯 키라 그려진 후엔 직접 못 바꿈 — 플래그로 처리
    if st.session_state.get("_reset_cat_pills", False):
        st.session_state.cat_pills = []
        st.session_state._reset_cat_pills = False

CATEGORIES = ["단맛", "짠맛", "매운맛", "쿠키/비스킷", "스낵/칩", "젤리/사탕", "건강한 맛", "탄산음료", "커피/차", "주스/드링크"]

init_state()

if st.session_state.get("_gsheet_error"):
    st.warning(f"⚠️ Google Sheets 연결 오류: {st.session_state['_gsheet_error']}")

# ═════════════════════════════════════════════
# 레이아웃
# ═════════════════════════════════════════════
col_l, col_nav, col_r = st.columns([1, 1.4, 1])
with col_nav:
    with st.container(key="nav_row"):
        nav_cols = st.columns(2)
        with nav_cols[0]:
            if st.button("HOME", key="btn_nav_home", use_container_width=True):
                st.session_state.page = "main"
                st.rerun()
        with nav_cols[1]:
            if st.button("MANAGEMENT", key="btn_nav_admin", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()

# ─────────────────────────────────────────────
# 홈 페이지
# ─────────────────────────────────────────────
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

    # ── 공지 ──
    notice_lines = [f"다음 다과 입고 예정일은 {st.session_state.notice_date}입니다."]
    if st.session_state.notice_extra:
        notice_lines.append(st.session_state.notice_extra)
    notice_text = "\n".join(notice_lines)
    st.markdown(f"""<div class="notice-box">
<img src="{svg_megaphone}"><div class="notice-text">{notice_text}</div>
</div>""", unsafe_allow_html=True)

    # ── 이달의 다과 피드백 ──
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
                if st.button("좋아요 취소" if has_liked else "좋아요", key=f"like_{s['id']}"):
                    if has_liked:
                        s["likes"] -= 1
                        st.session_state.user_likes.remove(s["id"])
                    else:
                        s["likes"] += 1
                        st.session_state.user_likes.add(s["id"])
                    persist("snacks")
                    st.rerun()

    # ── 신규 간식 요청 ──
    st.markdown(f'<div class="sec-title"><img src="{svg_candy}"> 신규 간식 요청</div>', unsafe_allow_html=True)

    sorted_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)
    req_cols = st.columns(2)
    for i, r in enumerate(sorted_reqs):
        with req_cols[i % 2]:
            is_tag_only_req = r["name"].strip().startswith("#")
            tag_html = "" if is_tag_only_req else "".join([f'<span class="tag" style="margin-right:3px;">#{c}</span>' for c in r["categories"]])
            sep = "" if is_tag_only_req else f"{tag_html} · "
            st.markdown(f"""<div class="req-card-grid">
                <h4>{r['name']}</h4>
                <div class="meta">{sep}<img class="icon-inline" src="{svg_thumbs_up}"> {r['votes']}명 요청</div>
            </div>""", unsafe_allow_html=True)

            btn_col, del_col = st.columns([2, 1])
            with btn_col:
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
            with del_col:
                # 본인이 등록한 것을 직접 삭제 — 눈에 덜 띄게 작은 버튼
                if st.button("삭제", key=f"del_home_req_{r['id']}"):
                    st.session_state.requests = [x for x in st.session_state.requests if x["id"] != r["id"]]
                    persist("requests")
                    st.rerun()

    # ── 새 간식 요청 등록 ──
    st.markdown("---")
    st.markdown(f'<div class="sec-title"><img src="{svg_cup_soda}"> 새 간식 요청 등록</div>', unsafe_allow_html=True)

    with st.form(key="search_form", clear_on_submit=False):
        req_name = st.text_input("원하는 다과/음료명을 입력하세요", placeholder="예: 코카콜라 제로", key="req_name_input")
        search_clicked = st.form_submit_button("🔍 검색하기", use_container_width=True)

    if search_clicked:
        st.session_state.naver_results = []
        if not req_name.strip():
            st.warning("제품명을 입력한 뒤 검색해 주세요.")
        else:
            st.session_state.search_input_val = req_name.strip()
            with st.spinner("상품 데이터를 검색 중입니다..."):
                results, err = search_naver_shopping(req_name.strip())
                if err:
                    st.error(err)
                elif results:
                    st.session_state.naver_results = results

    if st.session_state.get("naver_results"):
        st.caption("선택하면 바로 신규 간식 요청에 등록됩니다.")
        for ci, item in enumerate(st.session_state.naver_results):
            col_i1, col_i2 = st.columns([4, 1])
            with col_i1:
                img_html = f'<img src="{item["image"]}" width="40" style="border-radius:6px;margin-right:10px;">' if item.get("image") else ""
                st.markdown(f"""<div class="req-card" style="margin-bottom:4px;">
                    {img_html}
                    <div style="font-size:12px;">{item['name'][:30]}</div>
                </div>""", unsafe_allow_html=True)
            with col_i2:
                if st.button("선택", key=f"nv_{ci}"):
                    existing = next((r for r in st.session_state.requests if r["name"] == item["name"]), None)
                    cats_now = list(st.session_state.get("selected_cats", []))
                    if existing:
                        existing["votes"] += 1
                    else:
                        st.session_state.requests.append({"id": int(time.time() * 1000), "name": item["name"], "categories": cats_now, "votes": 1})
                    persist("requests")
                    st.session_state.selected_naver = None
                    st.session_state.selected_cats = []
                    st.session_state._reset_cat_pills = True
                    st.session_state.search_input_val = ""
                    st.session_state.naver_results = []
                    st.toast(f"'{item['name']}' 요청이 등록되었습니다.")
                    st.rerun()

    st.markdown('<div class="or-divider"><span></span>OR<span></span></div>', unsafe_allow_html=True)

    st.markdown('<div class="form-tag-label"># 카테고리로 요청하기 (중복 선택 가능)</div>', unsafe_allow_html=True)
    pills_selection = st.pills(
        "카테고리 선택", CATEGORIES,
        selection_mode="multi", format_func=lambda c: f"#{c}",
        label_visibility="collapsed", key="cat_pills",
    )
    st.session_state.selected_cats = list(pills_selection) if pills_selection else []

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
                else: st.session_state.requests.append({"id": int(time.time() * 1000), "name": name, "categories": cats_selected, "votes": 1})
                persist("requests")
                st.session_state.selected_naver = None
                st.session_state.selected_cats = []
                st.session_state._reset_cat_pills = True
                st.session_state.search_input_val = ""
                st.session_state.naver_results = []
                st.rerun()

# ─────────────────────────────────────────────
# 관리자 페이지
# ─────────────────────────────────────────────
elif st.session_state.page == "admin":

    st.markdown("""<div style="text-align:center; margin-bottom:2rem;">
        <div class="logo-sub">인프라 관리 시스템</div>
        <div style="font-size:24px; color:#4E342E;">Snack Lab Admin</div>
    </div>""", unsafe_allow_html=True)

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
        # ── 공지 설정 ──
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_pen}"> 홈 화면 공지 설정</div>', unsafe_allow_html=True)

        m = re.match(r"(\d+)월\s*(\d+)일", st.session_state.notice_date)
        default_month = int(m.group(1)) if m else 7
        default_day = int(m.group(2)) if m else 1
        col_d1, col_d2, col_d_empty = st.columns([1, 1, 3])
        with col_d1:
            sel_month = st.selectbox("월", list(range(1, 13)), index=default_month - 1, key="notice_month_sel")
        with col_d2:
            sel_day = st.selectbox("일", list(range(1, 32)), index=default_day - 1, key="notice_day_sel")

        # 자유 공지 입력칸 — 입고일 외에 전달할 내용을 자유롭게 입력
        notice_extra_input = st.text_area(
            "추가 공지 (선택)",
            value=st.session_state.notice_extra,
            placeholder="예: 이번 주 금요일 오후에 간식 배치 예정입니다.",
            height=80, key="notice_extra_input",
        )

        if st.button("공지 업데이트"):
            st.session_state.notice_date = f"{sel_month}월 {sel_day}일"
            st.session_state.notice_extra = notice_extra_input
            persist("notice_date")
            persist("notice_extra")
            st.toast("공지가 업데이트되었습니다.")

        st.markdown("---")

        # ── 비치 품목 제어 ──
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_check}"> 실시간 탕비실 비치 품목 제어</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="field-hint"><img src="{svg_search}"> 다과 직접 검색 후 추가</div>', unsafe_allow_html=True)
        admin_search_name = st.text_input(
            "다과/음료명 검색", key="admin_search_input",
            placeholder="예: 포카칩 어니언", label_visibility="collapsed",
        )
        if not admin_search_name:
            st.session_state.admin_naver_results = []

        if st.button("🔍 검색하기", key="admin_search_btn", use_container_width=True):
            st.session_state.admin_naver_results = []
            if not admin_search_name: st.warning("검색할 제품명을 입력해 주세요.")
            else:
                with st.spinner("상품 데이터를 검색 중입니다..."):
                    results, err = search_naver_shopping(admin_search_name)
                    if err: st.error(err)
                    elif results: st.session_state.admin_naver_results = results
                    else: st.info("검색 결과가 없습니다. 다른 검색어로 다시 시도해 보세요.")

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
                                "name": item["name"], "categories": [],
                                "image": item["image"],
                                "price": item["price"] if item["price"] else 2000,
                                "likes": 0,
                            })
                            persist("snacks")
                            st.toast(f"'{item['name']}' 비치 목록에 추가되었습니다.")
                        st.session_state.admin_naver_results = []
                        st.rerun()

        st.markdown("---")

        if not st.session_state.snacks:
            st.caption("현재 비치된 다과 인프라가 전무합니다.")
        else:
            for s in st.session_state.snacks:
                col_m1, col_m2, col_m3 = st.columns([2.4, 1.1, 0.9])
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
                with col_m3:
                    # 개별 품목 삭제 — 실수로 잘못 넣었을 때 대비
                    if st.button("삭제", key=f"del_snack_{s['id']}"):
                        st.session_state.snacks = [x for x in st.session_state.snacks if x["id"] != s["id"]]
                        st.session_state.pinned_snacks.discard(s["id"])
                        persist("snacks")
                        persist("pinned_snacks")
                        st.rerun()

        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        if st.button("비치 명단 업데이트 (고정 외 삭제)", use_container_width=True):
            for s in st.session_state.snacks:
                st.session_state.history_likes[s["name"]] = max(s["likes"], st.session_state.history_likes.get(s["name"], 0))
            st.session_state.snacks = [s for s in st.session_state.snacks if s["id"] in st.session_state.pinned_snacks]
            persist("history_likes")
            persist("snacks")
            st.rerun()

        st.markdown("---")

        # ── 신규 요청 심사 ──
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
                    st.session_state.snacks.append({
                        "id": int(time.time() * 1000) + count,
                        "name": r["name"], "categories": r.get("categories", []),
                        "image": "",
                        "price": 2000, "likes": 0,
                    })
                    count += 1
            st.session_state.requests = [r for r in st.session_state.requests if r["id"] not in [ra["id"] for ra in reqs_to_add]]
            persist("snacks")
            persist("requests")
            st.rerun()

        st.markdown("---")
        col_l1, col_l2, col_l3 = st.columns([1.5, 2, 1.5])
        with col_l2:
            if st.button("세션 로그아웃", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()

        # ── 진단 패널 ──
        st.markdown("---")
        with st.expander("🔧 연동 진단 (개발자용)"):
            # Google Sheets 진단
            st.markdown("**Google Sheets**")
            try:
                creds_dict = dict(st.secrets["gcp_service_account"])
                svc_email = creds_dict.get("client_email", "이메일 없음")
                st.info(f"서비스 계정 이메일: `{svc_email}`")
                st.caption("👆 이 이메일이 Google Sheet에 편집자로 공유되어 있어야 합니다")
                from google.oauth2.service_account import Credentials as _Creds
                import gspread as _gs
                _creds = _Creds.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
                _gc = _gs.authorize(_creds)
                sheet = _gc.open_by_key(st.secrets["GSHEET_ID"]).sheet1
                st.success("연결 성공!")
            except Exception as _e:
                sheet = None
                st.error(f"연결 실패 [{type(_e).__name__}]: {repr(_e)}")
            else:
                try:
                    rows = sheet.get_all_records()
                    st.success(f"연결 성공 — 저장된 키 {len(rows)}개")
                    for r in rows:
                        st.code(f"{r.get('key')} : {str(r.get('value',''))[:80]}")
                except Exception as e:
                    st.error(f"데이터 읽기 실패: {e}")

            st.markdown("**Google Search API**")
            api_key = st.secrets.get("GOOGLE_SEARCH_API_KEY", "")
            cx = st.secrets.get("GOOGLE_SEARCH_CX", "")
            st.write(f"API Key: `{'설정됨 (' + api_key[:8] + '...)' if api_key else '없음'}`")
            st.write(f"CX: `{'설정됨 (' + cx[:8] + '...)' if cx else '없음'}`")
            if st.button("검색 API 테스트 (포카칩)"):
                results, err = search_naver_shopping("포카칩")
                if err:
                    st.error(err)
                else:
                    st.success(f"성공! 결과 {len(results)}개")
                    st.write(results[0] if results else "결과 없음")
