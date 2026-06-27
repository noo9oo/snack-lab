import streamlit as st
import time
import base64
import pathlib
import requests
import json
import plotly.graph_objects as go

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

# 아이콘 미리 로드 (f-string 내 따옴표 충돌 방지 및 깔끔한 코드 유지)
svg_astroid = load_svg("astroid.svg")
svg_badge = load_svg("badge.svg")
svg_dot = load_svg("dot.svg")
svg_sparkles = load_svg("sparkles.svg")
svg_megaphones = load_svg("megaphones.svg")
svg_candy = load_svg("candy.svg")
svg_cup_soda = load_svg("cup-soda.svg")
svg_chart = load_svg("file-chart-column-increasing.svg")
svg_thumbs_up = load_svg("thumbs-up.svg")
svg_user_key = load_svg("user-round-key.svg")
svg_clip_pen = load_svg("clipboard-pen.svg")
svg_clip_check = load_svg("clipboard-check.svg")
# ※ 기존에 "📌.svg" 처럼 이모지 문자로 된 파일명은 GitHub/서버 환경에 따라
#   인코딩이 깨질 수 있어서 영문 파일명으로 변경했습니다.
#   assets 폴더에 pin.svg / search.svg / lock.svg 로 업로드해 주세요.
svg_pin = load_svg("pin.svg")
svg_search = load_svg("search.svg")
svg_lock = load_svg("lock.svg")

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

/* 전체 웹 배경색 및 기본 굵기 300 통일 */
html, body {{ 
    font-family: 'NanumGothicLocal', sans-serif; 
    background-color: #fdfdfa; 
}}
* {{ font-weight: 300 !important; }}

.block-container {{ max-width: 520px; padding: 0 1rem 4rem; }}

/* ── 헤더: 투명 처리 + 클릭 통과시키기 ──
   주의: top padding이 0이라 페이지 맨 위 콘텐츠(HOME/MANAGEMENT)가
   투명 헤더와 같은 자리에 겹치는데, background만 투명하게 하면 헤더가
   여전히 그 자리에서 클릭을 가로챕니다. pointer-events: none으로
   헤더가 클릭을 통과시키게 해서 바로 아래 버튼이 눌리게 합니다.
   (사이드바를 쓰지 않으므로 헤더의 메뉴 버튼이 막혀도 영향 없음) */
header[data-testid="stHeader"] {{ background: transparent; pointer-events: none; }}

/* ── 네비게이션 탭 (HOME / MANAGEMENT) ──
   기존 .nav-block 클래스는 실제 DOM에 존재하지 않는 죽은 선택자였습니다.
   key가 있는 위젯에는 Streamlit이 자동으로 st-key-<key> 클래스를 붙여주므로
   그걸 직접 타게팅합니다. */
[class*="st-key-btn_nav_"] button {{
    font-size: 10px !important; padding: 2px 8px !important;
    min-height: 24px !important; height: 24px !important; line-height: 24px !important;
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #475569 !important; border-radius: 0 !important;
}}
[class*="st-key-btn_nav_"] button:hover {{ text-decoration: underline !important; }}
[class*="st-key-btn_nav_"] button:active {{ transform: none !important; }}

/* ── 메인 배너 및 로고 (오직 이곳만 Skeuomorphism 유지) ── */
.skeuo-box {{
    background: #f0d875;
    border-radius: 12px;
    box-shadow: -3px -3px 6px rgba(255, 255, 255, 0.7), 3px 3px 8px rgba(0, 0, 0, 0.2);
}}
.logo-banner {{
    position: relative; text-align: center; padding: 30px 20px;
    background: rgba(255, 255, 255, 0.6); 
    border: none;
    border-radius: 20px; margin: 0 -1rem 1.2rem;
    overflow: hidden;
}}
.logo-sub {{ font-size: 12px; font-weight: 300 !important; color: #888888; margin-bottom: 6px; }}
.logo-main-wrapper {{ display: inline-block; padding: 10px 25px; margin-bottom: 6px; }}

.logo-letters {{
    font-size: 52px; font-family: 'SuperFuntime', sans-serif; font-weight: 400 !important;
    color: rgba(251, 192, 45, 0.3);
    line-height: 1; letter-spacing: 2px;
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

/* ── 공지 알림판 (틸/시안 톤) ── */
.notice-box {{
    padding: 14px 18px; margin: 0 -0.5rem 1.8rem;
    background: rgba(138, 221, 234, 0.25);
    border: 1px solid rgba(37, 189, 212, 1);
    border-radius: 12px; font-size: 13.5px; color: #333333;
    display: flex; align-items: center; gap: 8px;
}}
.notice-box img {{ width: 18px; height: 18px; }}

/* ── 섹션 타이틀 (15px, 400 굵기 통일) ── */
.sec-title {{ 
    font-size: 15px !important; 
    font-weight: 400 !important; 
    margin: 1.8rem 0 0.8rem; display: flex; align-items: center; gap: 6px; color: #8D6E63; 
}}
.sec-title img {{ width: 20px; height: 20px; }}

/* ── 작은 보조 라벨 (검색/보안 아이콘용) ── */
.field-hint {{
    display: flex; align-items: center; gap: 4px;
    font-size: 11px; color: #8D6E63; margin: 0 0 4px;
}}
.field-hint img {{ width: 13px; height: 13px; }}

/* ── 카드 스타일 (채우기+테두리 통일, 그림자 제거) ── */
.snack-card, .req-card, .cpg-item, .hot-trend-box {{
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    box-shadow: none; /* 스큐어모피즘 제거 */
}}
.snack-card {{ padding: 14px; text-align: center; margin-bottom: 8px; }}
.snack-card img.snack-img {{ width: 64px; height: 64px; border-radius: 12px; object-fit: cover; background: transparent; }}
.snack-card .name {{ font-size: 13px; color: #4E342E; margin: 6px 0 2px; }}
.snack-card .price {{ font-size: 11px; color: #8D6E63; margin-bottom: 6px; }}

.req-card {{ padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
.req-card .info h4 {{ font-size: 13px; margin: 0 0 4px 0; color: #4E342E; }}
.req-card .info .meta {{ font-size: 11px; color: #8D6E63; display: flex; align-items: center; gap:4px; }}

/* ── 카테고리 태그 ── */
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
    background: rgba(255, 253, 231, 0.5); border-radius: 14px; padding: 16px; 
    border: 1px solid rgba(251, 192, 45, 0.3);
    font-size: 12.5px; line-height: 1.7; white-space: pre-wrap; color: #4E342E;
}}

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

/* 제출(Primary) 버튼도 서식 동일화 */
button[kind="primary"] {{
    background: #ffffff !important; 
    border: 1px solid rgba(0,0,0,0.12) !important;
    color: #4E342E !important;
}}
button[kind="primary"] p {{ color: #4E342E !important; }}

/* '+나도' / '취소' 투표 버튼 — 폭 대폭 축소 */
[class*="st-key-vote_"] button {{
    padding: 0 4px !important;
    font-size: 10.5px !important;
    min-height: 22px !important;
    height: 22px !important;
}}

/* 입력 폼 태그 텍스트 크기 */
.form-tag-label {{ font-size: 13pt; color: #4E342E; margin: 10px 0 5px; font-weight: 400 !important; }}

/* ── HOT 다과 트렌드 큐레이션 박스 ── */
.hot-trend-box {{ padding: 14px; margin-bottom: 8px; }}
.hot-trend-box .hot-name {{ font-size: 14px; color: #4E342E; font-weight: 400 !important; margin-right: 6px; }}
.hot-trend-box .hot-tag {{ font-size: 11px; color: #8D6E63; }}
.hot-trend-box .hot-desc {{ font-size: 12.5px; color: #555; margin-top: 6px; }}

.icon-inline {{ width: 14px; height: 14px; vertical-align: middle; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# API 연동 (에러 대비 Fallback 포함)
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
            results = [{"name": item.get("title", "").replace("<b>", "").replace("</b>", ""), "price": int(item.get("lprice", 0)), "image": item.get("image", ""), "mall": item.get("mallName", "")} for item in data.get("items", [])[:display]]
            return results, None
        return None, f"API 오류 (HTTP {res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {str(e)}"

# ★ call_gemini 함수 — 상태코드별로 다른 메시지를 보여주도록 수정
#   - gemini-2.0-flash 모델은 이미 서비스 종료되어 항상 실패했었음 → gemini-2.5-flash로 교체
#   - 429(쿼터 초과)일 때만 짧은 재시도 안내 문구를 보여줌
#   - 그 외 에러는 실제 상태코드/메시지를 그대로 보여줘서 원인 진단이 가능하게 함
def call_gemini(prompt_text, mode="cart"):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return "⚠️ GEMINI_API_KEY가 설정되지 않았습니다. Streamlit Secrets를 확인해 주세요."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500},
    }

    try:
        res = requests.post(url, json=body, timeout=15)
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
        return "⚠️ 응답 형식을 해석할 수 없습니다. (API 응답 구조 변경 가능성)"

def is_error_text(text):
    return text.startswith("API 오류") or text.startswith("⚠️")


# ─────────────────────────────────────────────
# Session State 초기화 
# ─────────────────────────────────────────────
def init_state():
    if "snacks" not in st.session_state: st.session_state.snacks = []
    if "history_likes" not in st.session_state: st.session_state.history_likes = {}
    if "pinned_snacks" not in st.session_state: st.session_state.pinned_snacks = set()
    if "requests" not in st.session_state:
        st.session_state.requests = [
            {"id": 1, "name": "포카칩 어니언", "categories": ["짠맛", "스낵/칩"], "votes": 5},
            {"id": 2, "name": "마이쮸 딸기", "categories": ["단맛", "젤리/사탕"], "votes": 3},
        ]
    if "cat_votes" not in st.session_state:
        st.session_state.cat_votes = {"단맛": 35, "짠맛": 28, "매운맛": 4, "쿠키/비스킷": 15, "스낵/칩": 22, "젤리/사탕": 12, "견과류": 5, "탄산음료": 14, "커피/차": 9, "주스/드링크": 6}
    if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
    if "page" not in st.session_state: st.session_state.page = "main"
    if "ai_result" not in st.session_state: st.session_state.ai_result = ""
    if "naver_results" not in st.session_state: st.session_state.naver_results = []
    if "search_input_val" not in st.session_state: st.session_state.search_input_val = ""
    if "user_likes" not in st.session_state: st.session_state.user_likes = set()
    if "user_votes" not in st.session_state: st.session_state.user_votes = set()
    if "selected_cats" not in st.session_state: st.session_state.selected_cats = [] 
    
    if "notice_date" not in st.session_state: st.session_state.notice_date = "7월 1일"
    if "hot_trends" not in st.session_state: st.session_state.hot_trends = []

CATEGORIES = ["단맛", "짠맛", "매운맛", "쿠키/비스킷", "스낵/칩", "젤리/사탕", "견과류", "탄산음료", "커피/차", "주스/드링크"]

init_state()

# ═════════════════════════════════════════════
# 레이아웃 렌더링 파트
# ═════════════════════════════════════════════

# 좌측 상단 탭
col_nav, col_empty = st.columns([2, 3])
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
<div class="logo-main-wrapper skeuo-box">
<span class="logo-letters">Snack Lab</span>
</div>
<p class="logo-bottom-text">최적의 간식조합 찾기</p>
</div>"""
    st.markdown(html_banner, unsafe_allow_html=True)

    # ── 공지 알림판 ──
    html_notice = f"""<div class="notice-box">
<img src="{svg_megaphones}"> 다음 다과 입고 예정일은 {st.session_state.notice_date}입니다. 필요한 간식은 아래에 요청해 주세요.
</div>"""
    st.markdown(html_notice, unsafe_allow_html=True)

    # ── HOT 다과 트렌드 큐레이션 ──
    if st.session_state.hot_trends:
        st.markdown(f'<div class="sec-title"><img src="{svg_sparkles}"> HOT 다과 트렌드 큐레이션</div>', unsafe_allow_html=True)
        for ht in st.session_state.hot_trends:
            st.markdown(f"""
            <div class="hot-trend-box">
                <span class="hot-name">{ht['name']}</span>
                <span class="hot-tag">{ht['tag']}</span>
                <div class="hot-desc">{ht['desc']}</div>
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
                    {tag_html}
                </div>""", unsafe_allow_html=True)
                
                has_liked = s["id"] in st.session_state.user_likes
                if st.button(f"추천함 ({s['likes']})" if has_liked else f"재구매 ({s['likes']})", key=f"like_{s['id']}", use_container_width=True):
                    if has_liked:
                        s["likes"] -= 1
                        st.session_state.user_likes.remove(s["id"])
                    else:
                        s["likes"] += 1
                        st.session_state.user_likes.add(s["id"])
                    st.rerun()

    # ── Section 2: 신규 간식 요청 ──
    st.markdown(f'<div class="sec-title"><img src="{svg_candy}"> 신규 간식 요청</div>', unsafe_allow_html=True)

    for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True):
        col_r1, col_r2 = st.columns([6.5, 1.0])  # 투표 버튼 폭 대폭 축소
        with col_r1:
            tag_html = "".join([f'<span class="tag" style="margin-right:3px;">#{c}</span>' for c in r["categories"]])
            st.markdown(f"""<div class="req-card"><div class="info">
                <h4>{r['name']}</h4>
                <div class="meta">{tag_html} · <img class="icon-inline" src="{svg_thumbs_up}"> {r['votes']}명 요청</div>
            </div></div>""", unsafe_allow_html=True)
        with col_r2:
            has_voted = r["id"] in st.session_state.user_votes
            if st.button("취소" if has_voted else "+나도", key=f"vote_{r['id']}", use_container_width=True):
                if has_voted:
                    r["votes"] -= 1
                    st.session_state.user_votes.remove(r["id"])
                else:
                    r["votes"] += 1
                    st.session_state.user_votes.add(r["id"])
                st.rerun()

    # ── 새 간식 요청 등록 폼 ──
    st.markdown("---")
    st.markdown(f'<div class="sec-title"><img src="{svg_cup_soda}"> 새 간식 요청 등록</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="field-hint"><img src="{svg_search}"> 제품명으로 검색</div>', unsafe_allow_html=True)
    with st.form(key="search_form", clear_on_submit=False):
        req_name = st.text_input("원하는 다과/음료명을 입력하세요", placeholder="예: 코카콜라 제로", key="req_name_input")
        search_clicked = st.form_submit_button("검색하기", use_container_width=True)

    if search_clicked:
        st.session_state.naver_results = [] 
        if not req_name: st.warning("제품명을 입력한 뒤 검색해 주세요.")
        else:
            st.session_state.search_input_val = req_name
            with st.spinner("상품 데이터를 검색 중입니다..."):
                results, err = search_naver_shopping(req_name)
                if err: st.error(err)
                elif results: st.session_state.naver_results = results

    if st.session_state.get("naver_results"):
        for ci, item in enumerate(st.session_state.naver_results):
            col_i1, col_i2 = st.columns([4, 1])
            with col_i1:
                st.markdown(f"""<div class="req-card" style="margin-bottom:4px;">
                    <img src="{item['image']}" width="40" style="border-radius:6px; margin-right:10px;">
                    <div style="font-size:12px;">{item['name'][:30]}</div>
                </div>""", unsafe_allow_html=True)
            with col_i2:
                if st.button("선택", key=f"nv_{ci}"):
                    st.session_state.selected_naver = item
                    st.session_state.search_input_val = item["name"]
                    st.session_state.naver_results = [] 
                    st.rerun()

    st.markdown('<div class="form-tag-label"># 카테고리 태그 지정 (중복 선택 가능 / 선택 안함 가능)</div>', unsafe_allow_html=True)
    cat_cols = st.columns(5)
    for ci, cat in enumerate(CATEGORIES):
        with cat_cols[ci % 5]:
            is_sel = cat in st.session_state.selected_cats
            if st.button(f"#{cat}", key=f"form_cat_{cat}", use_container_width=True):
                if is_sel: st.session_state.selected_cats.remove(cat)
                else: st.session_state.selected_cats.append(cat)
                st.rerun()

    st.write("") 
    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 2, 1.5])
    with col_btn2:
        if st.button("제출!", use_container_width=True, type="primary"):
            sel_item = st.session_state.get("selected_naver")
            name = sel_item["name"] if sel_item else st.session_state.search_input_val
            if not name:
                st.warning("다과명을 명시해 주세요.")
            else:
                existing = next((r for r in st.session_state.requests if r["name"] == name), None)
                if existing: existing["votes"] += 1
                else:
                    st.session_state.requests.append({"id": int(time.time() * 1000), "name": name, "categories": list(st.session_state.selected_cats), "votes": 1})
                st.session_state.selected_naver = None
                st.session_state.selected_cats = []
                st.session_state.search_input_val = ""
                st.session_state.naver_results = []
                st.rerun()

    # ── 대시보드 ──
    st.markdown(f'<div class="sec-title"><img src="{svg_chart}"> 직원 취향 분석 대시보드</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        pie_colors = ['#FFB3BA', '#D8B4E2', '#BAE1FF', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#FFC4E1', '#B4F0E5', '#E2F0CB', '#FFD8B4']
        fig_donut = go.Figure(data=[go.Pie(labels=list(st.session_state.cat_votes.keys()), values=list(st.session_state.cat_votes.values()), hole=0.6, marker=dict(colors=pie_colors), textinfo="percent", textfont_size=10)])
        fig_donut.update_layout(showlegend=False, margin=dict(t=5, b=5, l=5, r=5), height=180, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_c2:
        chart_data = dict(st.session_state.history_likes)
        for s in st.session_state.snacks: chart_data[s["name"]] = max(s["likes"], chart_data.get(s["name"], 0))
        sorted_chart = sorted(chart_data.items(), key=lambda x: x[1], reverse=True)[:5]
        fig_bar = go.Figure(data=[go.Bar(x=[item[0][:4] for item in sorted_chart], y=[item[1] for item in sorted_chart], marker_color="rgba(150, 150, 150, 0.4)", marker_cornerradius=10)])
        fig_bar.update_layout(showlegend=False, margin=dict(t=5, b=5, l=5, r=5), height=180, bargap=0.55, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(tickfont_size=9), yaxis=dict(tickfont_size=9, gridcolor="rgba(200,200,200,0.1)"))
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

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
        new_date = st.text_input("입고 예정일 (공지용)", value=st.session_state.notice_date)
        if st.button("예정일 업데이트"):
            st.session_state.notice_date = new_date
            st.toast("입고 예정일이 수정되었습니다.")

        st.markdown(f'<div class="sec-title"><img src="{svg_sparkles}"> HOT 다과 트렌드 큐레이션 추가</div>', unsafe_allow_html=True)
        hot_name = st.text_input("다과 이름 입력 (자동생성 트리거)")
        
        col_h1, col_h2 = st.columns([1, 1])
        with col_h1:
            if st.button("AI 자동 생성 및 추가", use_container_width=True):
                if hot_name:
                    with st.spinner("AI가 멘트를 작성중입니다..."):
                        prompt = f"회사 탕비실 다과 '{hot_name}'을/를 직원들에게 추천하는 해시태그 1개와 짧은 홍보 문구(25자 이내)를 작성해줘. 형식은 반드시 '태그|문구' 기호로 구분지어 대답해."
                        result = call_gemini(prompt, mode="trend")
                        if is_error_text(result):
                            st.error(result)
                        else:
                            try:
                                t_tag, t_desc = result.split("|", 1)
                            except Exception:
                                t_tag, t_desc = "#요즘대세", result
                            st.session_state.hot_trends.append({"name": hot_name, "tag": t_tag.strip(), "desc": t_desc.strip()})
                            st.toast("트렌드 큐레이션이 홈에 추가되었습니다.")
        with col_h2:
            if st.button("전체 초기화 (삭제)", use_container_width=True):
                st.session_state.hot_trends = []

        st.markdown("---")
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_check}"> 실시간 탕비실 비치 품목 제어</div>', unsafe_allow_html=True)
        if not st.session_state.snacks: st.caption("현재 비치된 다과 인프라가 전무합니다.")
        else:
            for s in st.session_state.snacks:
                col_m1, col_m2 = st.columns([3, 1])
                with col_m1:
                    st.markdown(f"""<div class="req-card" style="margin-bottom:0;"><div class="info">
                        <h4>{s['name']}</h4>
                        <div class="meta"><img class="icon-inline" src="{svg_thumbs_up}"> {s['likes']}표 · {s['price']:,}원</div>
                    </div></div>""", unsafe_allow_html=True)
                with col_m2:
                    is_pinned = s["id"] in st.session_state.pinned_snacks
                    if st.checkbox("고정", value=is_pinned, key=f"pin_chk_{s['id']}"): st.session_state.pinned_snacks.add(s["id"])
                    else: st.session_state.pinned_snacks.discard(s["id"])

        if st.button("비치 명단 업데이트", use_container_width=True):
            for s in st.session_state.snacks: st.session_state.history_likes[s["name"]] = max(s["likes"], st.session_state.history_likes.get(s["name"], 0))
            st.session_state.snacks = [s for s in st.session_state.snacks if s["id"] in st.session_state.pinned_snacks]
            st.rerun()

        st.markdown("---")
        st.markdown(f'<div class="sec-title"><img src="{svg_clip_pen}"> 신규 요청 항목 심사 및 입고 처리</div>', unsafe_allow_html=True)
        reqs_to_add = []
        for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True):
            if st.checkbox(f"{r['name']} - {r['votes']}명 동의", key=f"add_{r['id']}"): reqs_to_add.append(r)

        if st.button("선택 다과 입고", use_container_width=True, type="primary"):
            count = 0
            for r in reqs_to_add:
                if not any(s["name"] == r["name"] for s in st.session_state.snacks):
                    st.session_state.snacks.append({"id": int(time.time() * 1000) + count, "name": r["name"], "categories": r["categories"], "image": fetch_snack_image(r["name"]), "price": 2000, "likes": 0})
                    count += 1
            st.session_state.requests = [r for r in st.session_state.requests if r["id"] not in [r_add["id"] for r_add in reqs_to_add]]
            st.rerun()

        st.markdown("---")
        st.markdown(f'<div class="sec-title"><img src="{svg_cup_soda}"> AI 10만원 최적 장바구니 자동 빌더</div>', unsafe_allow_html=True)
        
        if st.button("추천 조합 시뮬레이션 시작", use_container_width=True, type="primary"):
            cats = st.session_state.cat_votes
            top_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)
            prompt = f"탕비실 예산 10만원(100,000원) 내 최적 장바구니 구성.\n선호도:{cats}\n요청:{top_reqs}\n양식: 1.직원 취향 분석 2.장바구니 표(상품,태그,단가,수량,총액) 3.총액/잔액 4.추천이유"
            with st.spinner("AI 엔진 분석 구동 중..."):
                st.session_state.ai_result = call_gemini(prompt, mode="cart")

        if st.session_state.ai_result:
            if is_error_text(st.session_state.ai_result):
                st.error(st.session_state.ai_result)
            else:
                st.markdown(f'<div class="ai-result">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

        st.markdown("---")
        col_l1, col_l2, col_l3 = st.columns([1.5, 2, 1.5])
        with col_l2:
            if st.button("세션 로그아웃", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()
