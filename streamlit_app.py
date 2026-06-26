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
    page_icon="🍬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# 로컬 폰트 로딩 (SuperFuntime & NanumGothic)
# ─────────────────────────────────────────────
def load_local_font(file_name):
    font_path = pathlib.Path(__file__).parent / "fonts" / file_name
    if font_path.exists():
        return base64.b64encode(font_path.read_bytes()).decode()
    return ""

_font_b64_funtime = load_local_font("Super Funtime.ttf")
_font_b64_nanum = load_local_font("NanumGothic.otf")  # otf 또는 ttf

_font_css = ""
if _font_b64_funtime:
    _font_css += f"""
    @font-face {{
        font-family: 'SuperFuntime';
        src: url(data:font/truetype;base64,{_font_b64_funtime}) format('truetype');
        font-weight: normal; font-style: normal;
    }}
    """
if _font_b64_nanum:
    _font_css += f"""
    @font-face {{
        font-family: 'NanumGothicLocal';
        src: url(data:font/opentype;base64,{_font_b64_nanum}) format('opentype');
        font-weight: normal; font-style: normal;
    }}
    """

# ─────────────────────────────────────────────
# Custom CSS 및 Lucide 아이콘 렌더링 스크립트
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
{_font_css}

html, body {{ 
    font-family: 'NanumGothicLocal', 'Pretendard', sans-serif; 
    background-color: #fdfcf9; 
    font-weight: normal;
}}
.block-container {{ max-width: 520px; padding: 0 1rem 4rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}

* {{ font-weight: normal !important; }}

/* Lucide 아이콘 CSS 정렬 */
.lucide {{ width: 1.2em; height: 1.2em; vertical-align: text-bottom; margin-right: 4px; }}
.lucide-small {{ width: 1em; height: 1em; vertical-align: middle; margin-right: 2px; }}

.nav-wrapper {{ display: flex; justify-content: flex-start; margin-bottom: 12px; }}
div[data-testid="stHorizontalBlock"].nav-block {{ gap: 4px !important; width: auto !important; }}
.nav-block .stButton > button {{
    font-size: 11.5px !important; padding: 2px 10px !important;
    min-height: 26px !important; height: 26px !important; line-height: 26px !important;
    border-radius: 8px !important; background: rgba(255, 255, 255, 0.3) !important;
    border: 0.5px solid rgba(200, 200, 200, 0.3) !important; color: #555 !important;
}}

/* 로고 배너 */
.logo-banner {{
    position: relative; text-align: center; padding: 25px 20px;
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
    border-radius: 20px; margin: 0 -1rem 1.2rem;
    border: none;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    overflow: hidden;
}}

.star-candy {{
    position: absolute; font-size: 24px; color: rgba(251, 192, 45, 0.6); user-select: none;
}}
.star-left {{ top: 20%; left: 10%; animation: floatStar 3.5s ease-in-out infinite; }}
.star-right {{ bottom: 25%; right: 10%; animation: floatStar 4s ease-in-out infinite reverse; }}
@keyframes floatStar {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-8px) rotate(10deg); }}
}}

.logo-sub {{ font-size: 11.5px; color: #E86A92; letter-spacing: 1px; margin-bottom: 4px; }}
.logo-main {{ display: flex; align-items: center; justify-content: center; gap: 4px; z-index: 2; position: relative; }}

.glass-letter {{
    display: inline-block; position: relative;
    font-size: 50px; font-weight: normal !important;
    font-family: 'SuperFuntime', 'Pretendard', sans-serif;
    color: rgba(240,128,162,0.9);
    padding: 2px 1px;
    background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, rgba(240,128,162,0.06) 40%, rgba(255,255,255,0.15) 100%);
    -webkit-background-clip: padding-box; background-clip: padding-box;
    text-shadow: 0 1px 2px rgba(255,255,255,0.6), 0 -1px 1px rgba(240,128,162,0.12), 0 2px 8px rgba(240,128,162,0.18);
    filter: drop-shadow(0 2px 5px rgba(240,128,162,0.2));
    -webkit-text-stroke: 0.5px rgba(240,128,162,0.25);
    transition: transform 0.3s ease;
    cursor: default; line-height: 1;
}}
.glass-space {{ width: 14px; }}
.logo-bottom-text {{ font-size: 12.5px; color: #888; margin-top: 8px; margin-bottom: 0; z-index: 2; position: relative; }}

/* 공지 알림판 */
.notice-box {{
    padding: 12px 16px; margin: 0 -0.5rem 1.8rem;
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 0.5px solid rgba(220, 210, 190, 0.5);
    border-radius: 12px; font-size: 13px; color: #666;
    display: flex; align-items: center; gap: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}}

/* 섹션 타이틀 */
.sec-title {{ font-size: 15px; margin: 1.5rem 0 0.8rem; display: flex; align-items: center; gap: 6px; color: #444; }}

/* 카드 공통 글래스 */
.snack-card, .req-card, .cpg-item {{
    background: rgba(255, 255, 255, 0.4); 
    backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
    border: 0.5px solid rgba(200, 200, 200, 0.4); 
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}}
.snack-card {{ border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 8px; }}
.snack-card img {{ width: 64px; height: 64px; border-radius: 12px; object-fit: cover; background: transparent; }}
.snack-card .name {{ font-size: 13px; margin: 6px 0 6px; color: #444; }}

.tag-container {{ display: flex; flex-wrap: nowrap; justify-content: center; gap: 3px; margin-bottom: 6px; overflow: hidden; }}
.tag {{
    display: inline-block; padding: 2px 5px; border-radius: 6px;
    font-size: 8px; color: #666; background: rgba(255,255,255,0.6);
    border: 0.5px solid rgba(200, 200, 200, 0.3);
    white-space: nowrap;
}}

.req-card {{ border-radius: 12px; padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
.req-card .info h4 {{ font-size: 13px; margin: 0 0 4px 0; color: #444; }}
.req-card .info .meta {{ font-size: 11px; color: #888; }}

.cpg-item {{ border-radius: 10px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; padding: 10px; }}
.cpg-item img {{ width: 52px; height: 52px; border-radius: 8px; object-fit: cover; }}
.cpg-item .cpg-name {{ font-size: 12px; color: #444; }}
.cpg-item .cpg-price {{ font-size: 11px; color: #888; }}

.ai-result {{
    background: rgba(255, 255, 255, 0.4); border-radius: 14px; padding: 16px; 
    border: 0.5px solid rgba(200, 200, 200, 0.4);
    font-size: 12.5px; line-height: 1.7; white-space: pre-wrap; color: #555;
}}
.empty-zone {{ border: 0.5px dashed rgba(200, 200, 200, 0.6); border-radius: 14px; padding: 30px 20px; text-align: center; color: #999; font-size: 12.5px; }}

div[data-testid="stHorizontalBlock"] {{ gap: 6px; }}
.stButton > button {{
    border-radius: 10px !important; transition: all 0.3s ease !important;
    background: rgba(255, 255, 255, 0.4) !important; backdrop-filter: blur(10px) !important;
    border: 0.5px solid rgba(200, 200, 200, 0.5) !important;
    color: #555 !important; font-size: 12.5px !important;
}}
.stButton > button:hover {{ background: rgba(255, 255, 255, 0.6) !important; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03) !important; }}
.stButton > button:active {{ transform: translateY(1px); }}

button[kind="primary"] {{
    background: rgba(240, 128, 162, 0.15) !important; border: 0.5px solid rgba(240, 128, 162, 0.3) !important; color: #D8567F !important;
}}
button[kind="primary"]:hover {{ background: rgba(240, 128, 162, 0.25) !important; }}
button[kind="primary"] p {{ color: #D8567F !important; }}
</style>

<!-- Lucide CDN 스크립트 및 렌더링 옵저버 -->
<script src="https://unpkg.com/lucide@latest"></script>
<script>
    function renderLucideIcons() {{
        if(window.lucide) {{ window.lucide.createIcons(); }}
    }}
    setTimeout(renderLucideIcons, 100);
    const observer = new MutationObserver(renderLucideIcons);
    observer.observe(document.body, {{ childList: true, subtree: true }});
</script>
""", unsafe_allow_html=True)


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
            "젤리/사탕": 12, "건강한 맛": 5, "탄산음료": 14, "커피/차": 9, "주스/드링크": 6
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
    "젤리/사탕", "건강한 맛", "탄산음료", "커피/차", "주스/드링크"
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

    # ── 로고 배너 ──
    st.markdown("""
    <div class="logo-banner">
        <div class="star-candy star-left">✹</div>
        <div class="star-candy star-right">✹</div>
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
        <i data-lucide="bell" style="color:#BE185D;"></i> 다음 다과 입고 예정일은 7월 1일입니다. 필요한 간식은 아래에 요청해 주세요.
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: 이달의 다과 피드백 ──
    st.markdown('<div class="sec-title"><i data-lucide="cookie"></i> 이달의 다과 피드백</div>', unsafe_allow_html=True)

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
                    {tag_html}
                </div>""", unsafe_allow_html=True)
                
                has_liked = s["id"] in st.session_state.user_likes
                btn_label = f"추천 완료 ({s['likes']})" if has_liked else f"재구매 추천 ({s['likes']})"
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
    st.markdown('<div class="sec-title"><i data-lucide="candy"></i> 신규 간식 요청</div>', unsafe_allow_html=True)

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
                <div class="meta">{tag_html} · <i class="lucide-small" data-lucide="thumbs-up"></i> {r['votes']}명 요청</div>
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
    st.markdown('<div class="sec-title"><i data-lucide="cup-soda"></i> 새 간식 요청 등록</div>', unsafe_allow_html=True)

    st.markdown("**카테고리 태그 지정 (중복 선택 가능)**")
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

    with st.form(key="search_form", clear_on_submit=False):
        req_name = st.text_input("원하는 다과/음료명을 입력하세요", placeholder="예: 코카콜라 제로", key="req_name_input")
        search_clicked = st.form_submit_button("검색하기", use_container_width=True)

    if search_clicked:
        st.session_state.naver_results = []
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
        st.markdown("**검색된 마켓 라인업** (제출 시 즉시 등록)")
        for ci, item in enumerate(st.session_state.naver_results):
            col_i1, col_i2 = st.columns([4, 1.2])
            with col_i1:
                st.markdown(f"""<div class="cpg-item">
                    <img src="{item['image']}" onerror="this.style.display='none'">
                    <div><div class="cpg-name">{item['name'][:35]}</div></div>
                </div>""", unsafe_allow_html=True)
            with col_i2:
                if st.button("제출!", key=f"nv_{ci}", type="primary"):
                    cats_to_assign = list(st.session_state.selected_cats)
                    existing = next((r for r in st.session_state.requests if r["name"] == item['name']), None)
                    
                    if existing:
                        existing["votes"] += 1
                        st.toast("이미 리스트에 존재하여 요청 카운트가 추가되었습니다.")
                    else:
                        st.session_state.requests.append({
                            "id": int(time.time() * 1000),
                            "name": item['name'],
                            "categories": cats_to_assign,
                            "votes": 1
                        })
                        for c in cats_to_assign:
                            st.session_state.cat_votes[c] = st.session_state.cat_votes.get(c, 0) + 1
                        st.toast("신규 간식 요청서가 성공적으로 업로드되었습니다.")
                    
                    st.session_state.naver_results = []
                    st.session_state.search_input_val = ""
                    st.session_state.selected_cats = []
                    st.rerun()

    # ── 대시보드 ──
    st.markdown('<div class="sec-title"><i data-lucide="file-chart-column-increasing"></i> 취향 분석 대시보드</div>', unsafe_allow_html=True)
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
            marker_color="rgba(251, 192, 45, 0.4)",
            marker_cornerradius=10,
        )])
        fig_bar.update_layout(
            showlegend=False, margin=dict(t=5, b=5, l=5, r=5), height=180,
            bargap=0.55,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont_size=9), yaxis=dict(tickfont_size=9, gridcolor="rgba(200,200,200,0.1)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# ═════════════════════════════════════════════
# 관리자 페이지
# ═════════════════════════════════════════════
elif st.session_state.page == "admin":

    st.markdown("""
    <div class="logo-banner">
        <div class="logo-sub">인프라 관리 시스템</div>
        <div class="logo-main" style="font-size:24px; color:'#444';">Snack Lab Admin</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.admin_auth:
        st.markdown('<div class="sec-title"><i data-lucide="lock"></i> 관리자 모드 개방</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="sec-title"><i data-lucide="clipboard-list"></i> 실시간 탕비실 비치 품목 제어</div>', unsafe_allow_html=True)
        if not st.session_state.snacks:
            st.caption("현재 비치된 다과 인프라가 전무합니다.")
        else:
            for s in st.session_state.snacks:
                col_m1, col_m2 = st.columns([3, 1])
                with col_m1:
                    tags_str = " ".join([f"#{c}" for c in s["categories"]])
                    st.markdown(f"""<div class="req-card" style="margin-bottom:0;"><div class="info">
                        <h4>{s['name']}</h4>
                        <div class="meta">{tags_str} · <i class="lucide-small" data-lucide="thumbs-up"></i> {s['likes']}표 · {s['price']:,}원</div>
                    </div></div>""", unsafe_allow_html=True)
                with col_m2:
                    is_pinned = s["id"] in st.session_state.pinned_snacks
                    if st.checkbox("📌 고정", value=is_pinned, key=f"pin_chk_{s['id']}"):
                        st.session_state.pinned_snacks.add(s["id"])
                    else:
                        st.session_state.pinned_snacks.discard(s["id"])

        if st.button("비치 명단 업데이트", use_container_width=True):
            for s in st.session_state.snacks:
                st.session_state.history_likes[s["name"]] = max(
                    s["likes"], st.session_state.history_likes.get(s["name"], 0)
                )
            st.session_state.snacks = [s for s in st.session_state.snacks if s["id"] in st.session_state.pinned_snacks]
            st.toast("비치 명단이 업데이트되었습니다.")
            st.rerun()

        st.markdown("---")
        st.markdown('<div class="sec-title"><i data-lucide="message-square-plus"></i> 신규 요청 항목 심사 및 입고 처리</div>', unsafe_allow_html=True)
        reqs_to_add = []
        for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True):
            cat_str = "/".join(r['categories']) if r['categories'] else "카테고리 없음"
            if st.checkbox(f"{r['name']} [{cat_str}] - {r['votes']}명 동의", key=f"add_{r['id']}"):
                reqs_to_add.append(r)

        if st.button("선택 다과 입고", use_container_width=True, type="primary"):
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
                        "likes": 0
                    })
                    count += 1
            
            req_ids_to_add = [r["id"] for r in reqs_to_add]
            st.session_state.requests = [r for r in st.session_state.requests if r["id"] not in req_ids_to_add]
            
            st.toast("선택한 다과가 입고 처리되어 명단에서 삭제되었습니다.")
            st.rerun()

        st.markdown("---")
        st.markdown('<div class="sec-title"><i data-lucide="package"></i> AI 10만원 최적 장바구니 자동 빌더</div>', unsafe_allow_html=True)
        st.caption("네이버 쇼핑 대량 묶음 내의 쿠팡 도매 단가를 타겟팅하여 장바구니를 시뮬레이션합니다.")

        if st.button("추천 조합 시뮬레이션 시작", use_container_width=True, type="primary"):
            cats = st.session_state.cat_votes
            top_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)

            prompt = f"""당신은 회사 탕비실 간식 구매를 돕는 AI 어시스턴트입니다.
아래 데이터를 분석하여 예산 10만원(100,000원) 이내로 최적의 과자 장바구니를 구성해주세요.

★중요 가격 조건★: 
장바구니 품목의 예상 가격은 반드시 [네이버 쇼핑 검색결과 내의 쿠팡 판매가(로켓배송 대량 번들팩 가격 포함)]를 기준으로 현실적이고 저렴하게 계산해야 합니다.

[직원 카테고리 선호도]
{chr(10).join(f'- {k}: {v}표' for k, v in sorted(cats.items(), key=lambda x: x[1], reverse=True))}

[과자 히스토리 선호 데이터]
{chr(10).join(f'- {k}: {v}표' for k, v in st.session_state.history_likes.items())}

[직원 신규 요청]
{chr(10).join(f'- {r["name"]} (카테고리: {", ".join(r["categories"])}): {r["votes"]}명 요청' for r in top_reqs)}

다음 형식으로 답변해주세요:
1. 📊 직원 취향 분석 요약 (3줄 이내)
2. 🛒 추천 장바구니 (상품명, 카테고리 태그, 쿠팡최저가 기준가, 수량, 소계를 표로 정리)
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
            if st.button("세션 로그아웃", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()
