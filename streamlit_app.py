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
# Custom CSS (라이트 옐로우 테마, 나눔고딕 폰트 적용, 글래스모피즘)
# ─────────────────────────────────────────────
_font_path = pathlib.Path(__file__).parent / "fonts" / "Super Funtime.ttf"

_font_path_2 = pathlib.Path(__file__).parent / "fonts" / "NanumGothic.ttf"

@st.cache_data
def _load_font_base64(path: pathlib.Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")

_font_base64 = _load_font_base64(_font_path_2)

_font_b64 = base64.b64encode(_font_path.read_bytes()).decode() if _font_path.exists() else ""

_font_css = f"""@font-face {{
    font-family: 'SuperFuntime';
    src: url(data:font/truetype;base64,{_font_b64}) format('truetype');
    font-weight: normal; font-style: normal;
}}""" if _font_b64 else ""

st.markdown("""
<style>
@font-face {{
    font-family: 'NanumGothic';
    src: url(data:font/ttf;base64,{_font_base64}) format('truetype');
    font-weight: 400;
    font-style: normal;
}}
html, body {{ font-family: 'NanumGothic', -apple-system, sans-serif; background-color: #fdfdfa; }}
.block-container {{ max-width: 520px; padding: 0 1rem 4rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}


/* 상단 좌측 미니멀 네비게이션 탭 */
.nav-wrapper { display: flex; justify-content: flex-start; margin-bottom: 12px; }
div[data-testid="stHorizontalBlock"].nav-block { gap: 4px !important; width: auto !important; }
.nav-block .stButton > button {
    font-size: 11.5px !important; padding: 2px 10px !important;
    min-height: 26px !important; height: 26px !important; line-height: 26px !important;
    border-radius: 8px !important; background: rgba(255, 255, 255, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important; color: #475569 !important;
}

/* 3D 플로팅 메인 로고 배너 & 별사탕 에셋 (테두리 제거) */
.logo-banner {
    position: relative; text-align: center; padding: 25px 20px;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    border-radius: 20px; margin: 0 -1rem 1.2rem;
    border: none; /* 테두리 제거 */
    box-shadow: 0 8px 32px 0 rgba(251, 192, 45, 0.05);
    overflow: hidden;
}

/* 별사탕 글래스 & 플로팅 효과 (라이트 옐로우) */
.star-candy {
    position: absolute;
    filter: drop-shadow(0 3px 5px rgba(251, 192, 45, 0.3));
    user-select: none;
}
.star-left { top: 20%; left: 8%; animation: floatStar 3.5s ease-in-out infinite; }
.star-right { bottom: 25%; right: 8%; animation: floatStar 4s ease-in-out infinite reverse; }
@keyframes floatStar {
    0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
    50% { transform: translateY(-10px) rotate(15deg) scale(1.1); }
}

.logo-sub { font-size: 12px; font-weight: 500; color: #F57F17; letter-spacing: 1px; margin-bottom: 4px; }
.logo-main { display: flex; align-items: center; justify-content: center; gap: 4px; z-index: 2; position: relative; }

/* 글래스 & 플로팅 효과가 적용된 글자 */
@keyframes floatLetter {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px) scale(1.02); }
}
.glass-letter {
    display: inline-block; position: relative;
    font-size: 52px; font-weight: normal; font-family: 'SuperFuntime', 'Nanum Gothic', sans-serif;
    color: rgba(251, 192, 45, 0.3);
    padding: 0px 4px;
    background: linear-gradient(180deg,
        rgba(255,255,255,0.85) 0%,
        rgba(255,255,255,0.85) 10%,
        rgba(251,192,45,0.08) 15%,
        rgba(251,192,45,0.04) 50%,
        rgba(255,255,255,0.35) 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-stroke: 1px rgba(255,255,255,0.65);
    text-shadow:
        0 1px 0 rgba(255,255,255,0.8),
        0 3px 8px rgba(251,192,45,0.3);
    filter: drop-shadow(0 4px 6px rgba(251,192,45,0.2));
    cursor: default; line-height: 1;
    animation: floatLetter 3s ease-in-out infinite;
}
.glass-letter:nth-child(1) { animation-delay: 0.0s; }
.glass-letter:nth-child(2) { animation-delay: 0.1s; }
.glass-letter:nth-child(3) { animation-delay: 0.2s; }
.glass-letter:nth-child(4) { animation-delay: 0.3s; }
.glass-letter:nth-child(5) { animation-delay: 0.4s; }
.glass-letter:nth-child(7) { animation-delay: 0.5s; }
.glass-letter:nth-child(8) { animation-delay: 0.6s; }
.glass-letter:nth-child(9) { animation-delay: 0.7s; }

.glass-space { width: 14px; }
.logo-bottom-text { font-size: 13px; font-weight: 500; color: #8D6E63; margin-top: 8px; margin-bottom: 0; z-index: 2; position: relative; }

/* 공지 알림판 */
.notice-box {
    padding: 14px 18px; margin: 0 -0.5rem 1.8rem;
    background: rgba(255, 253, 231, 0.65);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(251, 192, 45, 0.3);
    border-radius: 14px; font-size: 13.5px; font-weight: 700; color: #F57F17;
    display: flex; align-items: center; gap: 8px;
    box-shadow: 0 4px 12px rgba(251, 192, 45, 0.05);
}

/* 섹션 타이틀 */
.sec-title { font-size: 16px; font-weight: 800; margin: 1.8rem 0 0.8rem; display: flex; align-items: center; gap: 6px; color: #4E342E; }

/* 카드 공통 글래스 */
.snack-card, .req-card, .cpg-item {
    background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.9); box-shadow: 0 4px 14px rgba(251, 192, 45, 0.06);
}
.snack-card { border-radius: 16px; padding: 14px; text-align: center; margin-bottom: 8px; }
.snack-card img { width: 64px; height: 64px; border-radius: 12px; object-fit: cover; background: #fff; }
.snack-card .name { font-size: 13px; font-weight: 700; margin: 6px 0 2px; color: #4E342E; }
.snack-card .price { font-size: 11px; color: #8D6E63; margin-bottom: 6px; font-weight: 700; }

/* 카테고리 태그 폰트 크기 축소 및 줄바꿈 방지 */
.tag-container { display: flex; flex-wrap: nowrap; justify-content: center; gap: 3px; margin-bottom: 6px; overflow: hidden; }
.tag {
    display: inline-block; padding: 2px 5px; border-radius: 6px;
    font-size: 8px; font-weight: 800; color: #5D4037; background: #FFF59D;
    white-space: nowrap;
}
/* 라이트 옐로우 / 웜톤 컬러 팔레트 매핑 */
.tag-단맛 { background: #FFD54F; } .tag-짠맛 { background: #FFCC80; }
.tag-매운맛 { background: #FFAB91; } .tag-쿠키_비스킷 { background: #FFE082; }
.tag-스낵_칩 { background: #FFF59D; } .tag-젤리_사탕 { background: #C5E1A5; color: #33691E; }
.tag-견과류 { background: #BCAAA4; color: #4E342E; } .tag-탄산음료 { background: #81D4FA; color: #01579B; }
.tag-커피_차 { background: #D7CCC8; } .tag-주스_드링크 { background: #FFE082; color: #F57F17; }

.req-card { border-radius: 14px; padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.req-card .info h4 { font-size: 13px; font-weight: 700; margin: 0 0 4px 0; color: #4E342E; }
.req-card .info .meta { font-size: 11px; color: #8D6E63; font-weight: 700;}

.cpg-item { border-radius: 10px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; padding: 10px; }
.cpg-item img { width: 52px; height: 52px; border-radius: 8px; object-fit: cover; }
.cpg-item .cpg-name { font-size: 12px; font-weight: 700; color: #4E342E; }
.cpg-item .cpg-price { font-size: 11px; color: #8D6E63; font-weight: 700; }

.ai-result {
    background: rgba(255, 253, 231, 0.5); border-radius: 16px; padding: 18px; border: 1px solid rgba(251, 192, 45, 0.3);
    font-size: 12.5px; line-height: 1.7; white-space: pre-wrap; color: #4E342E; font-weight: 700;
}
.empty-zone { border: 1px dashed #FBC02D; border-radius: 16px; padding: 35px 20px; text-align: center; color: #BCAAA4; font-size: 12.5px; font-weight: 700; }

/* 버튼 공통 & 프라이머리(제출) 버튼 옐로우 톤 커스텀 */
div[data-testid="stHorizontalBlock"] { gap: 6px; }
.stButton > button {
    border-radius: 10px !important; font-weight: 800 !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
.stButton > button:hover { transform: translateY(-1px) scale(1.01); box-shadow: 0 4px 12px rgba(251, 192, 45, 0.15) !important; }
.stButton > button:active { transform: translateY(1px) scale(0.98); }

/* Primary 속성을 가진 버튼 색상 오버라이드 (옐로우 그라데이션) */
button[kind="primary"] {
    background: linear-gradient(135deg, #FDE68A, #FBBF24) !important;
    border: none !important; color: #4E342E !important;
    box-shadow: 0 4px 10px rgba(251, 192, 45, 0.2) !important;
}
button[kind="primary"]:hover { background: linear-gradient(135deg, #FBBF24, #F59E0B) !important; }
button[kind="primary"] p { color: #4E342E !important; }
</style>
""", unsafe_allow_html=True)

if _font_css:
    st.markdown(f"<style>{_font_css}</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 네이버 제품 이미지 크롤러 캐시
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_snack_image(name):
    try:
        client_id = st.secrets.get("NAVER_CLIENT_ID", "")
        client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
        if not client_id or client_id.startswith("여기에"):
            return ""
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        res = requests.get(url, headers=headers, params={"query": name, "display": 1}, timeout=5)
        if res.status_code == 200:
            items = res.json().get("items", [])
            if items:
                return items[0].get("image", "")
    except Exception:
        pass
    return ""


# ─────────────────────────────────────────────
# Session State 초기화 
# ─────────────────────────────────────────────
def init_state():
    if "snacks" not in st.session_state:
        st.session_state.snacks = []
    if "history_likes" not in st.session_state:
        st.session_state.history_likes = {}
    if "pinned_snacks" not in st.session_state:
        st.session_state.pinned_snacks = set()
    if "requests" not in st.session_state:
        st.session_state.requests = [
            {"id": 1, "name": "포카칩 어니언", "categories": ["짠맛", "스낵/칩"], "votes": 5},
            {"id": 2, "name": "마이쮸 딸기", "categories": ["단맛", "젤리/사탕"], "votes": 3},
            {"id": 3, "name": "칠성사이다 제로", "categories": ["단맛", "탄산음료"], "votes": 8},
        ]
    if "cat_votes" not in st.session_state:
        st.session_state.cat_votes = {
            "단맛": 35, "짠맛": 28, "매운맛": 4, "쿠키/비스킷": 15, "스낵/칩": 22,
            "젤리/사탕": 12, "견과류": 5, "탄산음료": 14, "커피/차": 9, "주스/드링크": 6
        }
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "ai_result" not in st.session_state:
        st.session_state.ai_result = ""
    if "naver_results" not in st.session_state:
        st.session_state.naver_results = []
    if "search_input_val" not in st.session_state:
        st.session_state.search_input_val = ""
        
    if "user_likes" not in st.session_state:
        st.session_state.user_likes = set()
    if "user_votes" not in st.session_state:
        st.session_state.user_votes = set()
    if "selected_cats" not in st.session_state:
        st.session_state.selected_cats = [] 

CATEGORIES = [
    "단맛", "짠맛", "매운맛", "쿠키/비스킷", "스낵/칩", 
    "젤리/사탕", "견과류", "탄산음료", "커피/차", "주스/드링크"
]

init_state()

# ─────────────────────────────────────────────
# API 연동 파트 (네이버 쇼핑 / Gemini)
# ─────────────────────────────────────────────
def search_naver_shopping(keyword, display=5):
    try:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
    except Exception:
        return None, "네이버 API 키가 설정되지 않았습니다."
    if client_id.startswith("여기에"):
        return None, "네이버 API 키를 실제 키로 교체해주세요."
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params = {"query": keyword, "display": display, "sort": "sim"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            results = []
            for item in data.get("items", [])[:display]:
                name = item.get("title", "").replace("<b>", "").replace("</b>", "")
                results.append({
                    "name": name, "price": int(item.get("lprice", 0)),
                    "image": item.get("image", ""), "mall": item.get("mallName", ""),
                })
            return results, None
        else:
            return None, f"API 오류 (HTTP {res.status_code})"
    except Exception as e:
        return None, f"네트워크 오류: {str(e)}"

def call_gemini(prompt_text):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return "Gemini API 키가 설정되지 않았습니다."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500},
    }
    try:
        res = requests.post(url, json=body, timeout=30)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"API 오류: {res.status_code}"
    except Exception as e:
        return f"요청 실패: {str(e)}"

# ═════════════════════════════════════════════
# 레이아웃 렌더링 파트
# ═════════════════════════════════════════════

# 좌측 상단 탭
col_nav, col_empty = st.columns([2, 3])
with col_nav:
    nav_cols = st.columns(2)
    with nav_cols[0]:
        if st.button("홈", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
    with nav_cols[1]:
        if st.button("관리자", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()


if st.session_state.page == "main":

    # ── 커스텀 라이트 옐로우 3D 별사탕 SVG 정의 ──
   star_svg = """
     <svg viewBox="0 0 24 24" width="28" height="28">
         <path fill="#FFF59D" stroke="#FBC02D" stroke-width="1.5" stroke-linejoin="round"
         d="M12 1 L13.72 7.84 L19.78 4.22 L16.16 10.28 L23 12 L16.16 13.72 L19.78 19.78 L13.72 16.16 L12 23 L10.28 16.16 L4.22 19.78 L7.84 13.72 L1 12 L7.84 10.28 L4.22 4.22 L10.28 7.84 Z"/>
     </svg>
     """

    # ── 로고 배너 ──
    st.markdown(f"""
    <div class="logo-banner">
        <div class="star-candy star-left">{star_svg}</div>
        <div class="star-candy star-right">{star_svg}</div>
        <div class="logo-sub">정책기획팀</div>
        <div class="logo-main">
            <span class="glass-letter" data-char="S">S</span>
            <span class="glass-letter" data-char="n">n</span>
            <span class="glass-letter" data-char="a">a</span>
            <span class="glass-letter" data-char="c">c</span>
            <span class="glass-letter" data-char="k">k</span>
            <span class="glass-space"></span>
            <span class="glass-letter" data-char="L">L</span>
            <span class="glass-letter" data-char="a">a</span>
            <span class="glass-letter" data-char="b">b</span>
        </div>
        <p class="logo-bottom-text">최적의 간식조합 찾기</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 공지 알림판 ──
    st.markdown("""
    <div class="notice-box">
        <span>☕</span> 다음 다과 입고 예정일은 7월 1일입니다. 필요한 간식은 아래에 요청해 주세요.
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: 이달의 다과 피드백 ──
    st.markdown('<div class="sec-title">🍬 이달의 다과 피드백</div>', unsafe_allow_html=True)

    if not st.session_state.snacks:
        st.markdown('<div class="empty-zone">현재 비치된 다과 항목이 없습니다.<br>관리자 페이지에서 리스트를 업데이트해 주세요.</div>', unsafe_allow_html=True)
    else:
        snack_cols = st.columns(2)
        for i, s in enumerate(st.session_state.snacks):
            with snack_cols[i % 2]:
                pin_icon = "📌 " if s["id"] in st.session_state.pinned_snacks else ""
                
                tag_html = '<div class="tag-container">'
                for c in s["categories"]:
                    safe_class = c.replace("/", "_")
                    tag_html += f'<span class="tag tag-{safe_class}">#{c}</span>'
                tag_html += '</div>'
                
                st.markdown(f"""<div class="snack-card">
                    <img src="{s['image']}" onerror="this.src='https://placehold.co/120x120/FFF9C4/FBC02D?text=Snack'">
                    <div class="name">{pin_icon}{s['name']}</div>
                    <div class="price">{s['price']:,}원</div>
                    {tag_html}
                </div>""", unsafe_allow_html=True)
                
                has_liked = s["id"] in st.session_state.user_likes
                btn_label = f"🍬 추천함 ({s['likes']})" if has_liked else f"👍 재구매 ({s['likes']})"
                btn_type = "primary" if has_liked else "secondary"
                
                if st.button(btn_label, key=f"like_{s['id']}", use_container_width=True, type=btn_type):
                    if has_liked:
                        s["likes"] -= 1
                        st.session_state.user_likes.remove(s["id"])
                        st.session_state.history_likes[s["name"]] = max(0, st.session_state.history_likes.get(s["name"], 1) - 1)
                        for c in s["categories"]:
                            st.session_state.cat_votes[c] = max(0, st.session_state.cat_votes.get(c, 1) - 1)
                        st.toast("재구매 추천을 취소했습니다.")
                    else:
                        s["likes"] += 1
                        st.session_state.user_likes.add(s["id"])
                        st.session_state.history_likes[s["name"]] = st.session_state.history_likes.get(s["name"], 0) + 1
                        for c in s["categories"]:
                            st.session_state.cat_votes[c] = st.session_state.cat_votes.get(c, 0) + 1
                        st.toast("재구매 투표가 반영되었습니다.")
                    st.rerun()

    # ── Section 2: 간식 요청하기 ──
    st.markdown('<div class="sec-title">🍬 신규 간식 요청</div>', unsafe_allow_html=True)

    sorted_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)
    for r in sorted_reqs:
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            tag_html = ""
            for c in r["categories"]:
                safe_class = c.replace("/", "_")
                tag_html += f'<span class="tag tag-{safe_class}" style="margin-right:3px;">#{c}</span>'
            st.markdown(f"""<div class="req-card"><div class="info">
                <h4>{r['name']}</h4>
                <div class="meta">{tag_html} · {r['votes']}명 요청</div>
            </div></div>""", unsafe_allow_html=True)
        with col_r2:
            has_voted = r["id"] in st.session_state.user_votes
            v_label = "취소" if has_voted else "나도 +1"
            v_type = "primary" if has_voted else "secondary"
            
            if st.button(v_label, key=f"vote_{r['id']}", use_container_width=True, type=v_type):
                if has_voted:
                    r["votes"] -= 1
                    st.session_state.user_votes.remove(r["id"])
                    st.toast("요청을 취소했습니다.")
                else:
                    r["votes"] += 1
                    st.session_state.user_votes.add(r["id"])
                    st.toast("요청 목록에 등록을 보탰습니다.")
                st.rerun()

    # ── 새 간식 요청 폼 ──
    st.markdown("---")
    st.markdown("#### ☕ 새 간식 요청 등록")

    with st.form(key="search_form", clear_on_submit=False):
        req_name = st.text_input("원하는 다과/음료명을 입력하세요", placeholder="예: 코카콜라 제로", key="req_name_input")
        search_clicked = st.form_submit_button("🔍 제품명 검색", use_container_width=True)

    if search_clicked:
        st.session_state.naver_results = [] # 검색 시 기존 결과 초기화
        if not req_name:
            st.warning("제품명을 입력한 뒤 검색해 주세요.")
        else:
            st.session_state.search_input_val = req_name
            with st.spinner("상품 데이터를 검색 중입니다..."):
                results, err = search_naver_shopping(req_name)
                if err: st.error(err)
                elif results: st.session_state.naver_results = results
                else: st.info("매칭되는 검색 결과가 없습니다.")

    if st.session_state.get("naver_results"):
        st.markdown("**검색된 마켓 라인업** (선택 시 자동 매핑)")
        for ci, item in enumerate(st.session_state.naver_results):
            col_i1, col_i2 = st.columns([4, 1])
            with col_i1:
                mall = f' · {item["mall"]}' if item.get("mall") else ""
                st.markdown(f"""<div class="cpg-item">
                    <img src="{item['image']}" onerror="this.style.display='none'">
                    <div><div class="cpg-name">{item['name'][:35]}</div>
                    <div class="cpg-price">{item['price']:,}원{mall}</div></div>
                </div>""", unsafe_allow_html=True)
            with col_i2:
                if st.button("선택", key=f"nv_{ci}"):
                    st.session_state.selected_naver = item
                    st.session_state.search_input_val = item["name"]
                    st.session_state.naver_results = [] # 선택 시 검색 결과 초기화
                    st.toast("상품 정보가 입력창에 세팅되었습니다.")
                    st.rerun()

    st.markdown("**카테고리 태그 지정 (중복 선택 가능 / 선택 안함 가능)**")
    cat_cols = st.columns(5)
    for ci, cat in enumerate(CATEGORIES):
        with cat_cols[ci % 5]:
            is_sel = cat in st.session_state.selected_cats
            b_type = "primary" if is_sel else "secondary"
            if st.button(f"#{cat}", key=f"form_cat_{cat}", use_container_width=True, type=b_type):
                if is_sel: st.session_state.selected_cats.remove(cat)
                else: st.session_state.selected_cats.append(cat)
                st.rerun()

    st.write("") 
    
    col_btn1, col_btn2, col_btn3 = st.columns([1.5, 2, 1.5])
    with col_btn2:
        if st.button("제출!", use_container_width=True, type="primary"):
            sel_item = st.session_state.get("selected_naver")
            name = sel_item["name"] if sel_item else st.session_state.search_input_val
            cats_to_assign = list(st.session_state.selected_cats)

            if not name:
                st.warning("다과명을 명시해 주세요.")
            else:
                existing = next((r for r in st.session_state.requests if r["name"] == name), None)
                if existing:
                    existing["votes"] += 1
                    st.toast("이미 리스트에 존재하여 요청 카운트가 추가되었습니다.")
                else:
                    st.session_state.requests.append({
                        "id": int(time.time() * 1000),
                        "name": name,
                        "categories": cats_to_assign,
                        "votes": 1
                    })
                    for c in cats_to_assign:
                        st.session_state.cat_votes[c] = st.session_state.cat_votes.get(c, 0) + 1
                    st.toast("신규 간식 요청서가 성공적으로 업로드되었습니다.")
                    
                st.session_state.selected_naver = None
                st.session_state.selected_cats = []
                st.session_state.search_input_val = ""
                st.session_state.naver_results = [] # 제출 후 검색 결과 초기화
                st.rerun()

    # ── 대시보드 그래프 컬러 옐로우 테마로 교체 ──
    st.markdown('<div class="sec-title">📊 직원 취향 분석 대시보드</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        cvotes = st.session_state.cat_votes
        pie_colors = ["#FFD54F", "#FFCC80", "#FFAB91", "#FFE082", "#FFF59D", "#C5E1A5", "#BCAAA4", "#81D4FA", "#D7CCC8", "#FFF176"]
        fig_donut = go.Figure(data=[go.Pie(
            labels=list(cvotes.keys()), values=list(cvotes.values()),
            hole=0.6, marker=dict(colors=pie_colors),
            textinfo="percent", textfont_size=10,
        )])
        fig_donut.update_layout(
            showlegend=False, margin=dict(t=5, b=5, l=5, r=5), height=180,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_c2:
        chart_data = dict(st.session_state.history_likes)
        for s in st.session_state.snacks:
            chart_data[s["name"]] = max(s["likes"], chart_data.get(s["name"], 0))
            
        sorted_chart = sorted(chart_data.items(), key=lambda x: x[1], reverse=True)[:5]
        
        fig_bar = go.Figure(data=[go.Bar(
            x=[item[0][:4] for item in sorted_chart],
            y=[item[1] for item in sorted_chart],
            marker_color="rgba(251, 192, 45, 0.85)",
            marker_cornerradius=10,
        )])
        fig_bar.update_layout(
            showlegend=False, margin=dict(t=5, b=5, l=5, r=5), height=180,
            bargap=0.55,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont_size=9), yaxis=dict(tickfont_size=9, gridcolor="rgba(251,192,45,0.08)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# ═════════════════════════════════════════════
# 관리자 페이지
# ═════════════════════════════════════════════
elif st.session_state.page == "admin":

    st.markdown("""
    <div class="logo-banner" style="padding:20px">
        <div class="logo-sub" style="color:#F57F17">인프라 관리 시스템</div>
        <div class="logo-main" style="font-size:24px; font-family:'Nanum Gothic'; font-weight:800; color:'#4E342E';">Snack Lab Admin</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.admin_auth:
        st.markdown("### 🔐 관리자 모드 개방")
        admin_pw = st.text_input("액세스 패스워드", type="password", key="admin_pw_input")
        
        col_a1, col_a2, col_a3 = st.columns([1.5, 2, 1.5])
        with col_a2:
            if st.button("인증 실행", use_container_width=True, type="primary"):
                correct_pw = st.secrets.get("ADMIN_PASSWORD", "1234")
                if admin_pw == correct_pw:
                    st.session_state.admin_auth = True
                    st.toast("보안 스크린 해제 완료.")
                    st.rerun()
                else:
                    st.error("액세스 권한 암호가 올바르지 않습니다.")
    else:
        st.markdown("#### 📋 실시간 탕비실 비치 품목 제어")
        if not st.session_state.snacks:
            st.caption("현재 비치된 다과 인프라가 전무합니다.")
        else:
            for s in st.session_state.snacks:
                col_m1, col_m2 = st.columns([3, 1])
                with col_m1:
                    tags_str = " ".join([f"#{c}" for c in s["categories"]])
                    st.markdown(f"""<div class="req-card" style="margin-bottom:0;"><div class="info">
                        <h4>{s['name']}</h4>
                        <div class="meta">{tags_str} · 👍 {s['likes']}표</div>
                    </div></div>""", unsafe_allow_html=True)
                with col_m2:
                    is_pinned = s["id"] in st.session_state.pinned_snacks
                    if st.checkbox("📌 고정", value=is_pinned, key=f"pin_chk_{s['id']}"):
                        st.session_state.pinned_snacks.add(s["id"])
                    else:
                        st.session_state.pinned_snacks.discard(s["id"])

        if st.button("🔄 비치 명단 업데이트", use_container_width=True):
            for s in st.session_state.snacks:
                st.session_state.history_likes[s["name"]] = max(
                    s["likes"], st.session_state.history_likes.get(s["name"], 0)
                )
            # 고정된 스낵만 유지
            st.session_state.snacks = [s for s in st.session_state.snacks if s["id"] in st.session_state.pinned_snacks]
            st.toast("비치 명단이 업데이트되었습니다.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🙋 신규 요청 항목 심사 및 입고 처리")
        reqs_to_add = []
        for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True):
            cat_str = "/".join(r['categories']) if r['categories'] else "카테고리 없음"
            if st.checkbox(f"{r['name']} [{cat_str}] - {r['votes']}명 동의", key=f"add_{r['id']}"):
                reqs_to_add.append(r)

        if st.button("✅ 선택 다과 입고", use_container_width=True, type="primary"):
            count = 0
            for r in reqs_to_add:
                if not any(s["name"] == r["name"] for s in st.session_state.snacks):
                    img = fetch_snack_image(r["name"])
                    st.session_state.snacks.append({
                        "id": int(time.time() * 1000) + count,
                        "name": r["name"],
                        "categories": r["categories"],
                        "image": img,
                        "price": 2000, 
                        "likes": 0  # 메인화면 재구매 투표는 0으로 초기화
                    })
                    count += 1
            
            # 입고 처리된 다과는 요청 명단에서 삭제
            req_ids_to_add = [r["id"] for r in reqs_to_add]
            st.session_state.requests = [r for r in st.session_state.requests if r["id"] not in req_ids_to_add]
            
            st.toast("선택한 다과가 입고 처리되어 명단에서 삭제되었습니다.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### ☕ AI 10만원 최적 장바구니 자동 빌더")
        st.caption("네이버 쇼핑 대량 묶음 내의 쿠팡 도매 단가를 타겟팅하여 장바구니를 시뮬레이션합니다.")

        if st.button("🔮 추천 조합 시뮬레이션 시작", use_container_width=True, type="primary"):
            cats = st.session_state.cat_votes
            top_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)

            prompt = f"""당신은 회사 탕비실 간식 구매를 돕는 AI 어시스턴트입니다.
아래 데이터를 분석하여 예산 10만원(100,000원) 이내로 최적의 과자 장바구니를 구성해주세요.

★중요 가격 조건★: 
장바구니 품목의 예상 가격은 반드시 [네이버 쇼핑 검색결과 내의 쿠팡 판매가(로켓배송 대량 번들팩 가격 포함)]를 기준으로 현실적이고 저렴하게 계산해야 합니다. 예: 단품 가격이 아닌 대용량 박스/묶음 상품 단가 반영.

[직원 카테고리 선호도]
{chr(10).join(f'- {k}: {v}표' for k, v in sorted(cats.items(), key=lambda x: x[1], reverse=True))}

[과자 히스토리 선호 데이터]
{chr(10).join(f'- {k}: {v}표' for k, v in st.session_state.history_likes.items())}

[직원 신규 요청]
{chr(10).join(f'- {r["name"]} (카테고리: {", ".join(r["categories"])}): {r["votes"]}명 요청' for r in top_reqs)}

다음 형식으로 답변해주세요:
1. 📊 직원 취향 분석 요약 (3줄 이내)
2. 🛒 추천 장바구니 (상품명, 카테고리 태그, 네이버 검색-쿠팡최저가 기준가, 수량, 소계를 표로 정리)
3. 💰 총액 / 잔액 (100,000원 절대 초과 금지)
4. 📝 추천 사유 (왜 이 조합이 최적인지 3줄 이내)"""

            with st.spinner("AI 엔진 분석 구동 중..."):
                result = call_gemini(prompt)
            st.session_state.ai_result = result

        if st.session_state.ai_result:
            st.markdown(f'<div class="ai-result">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

        st.markdown("---")
        col_l1, col_l2, col_l3 = st.columns([1.5, 2, 1.5])
        with col_l2:
            if st.button("🔒 세션 로그아웃", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()
