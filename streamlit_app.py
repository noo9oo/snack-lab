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
# Custom CSS (캔디 질감 로고, 컬러풀 UI)
# ─────────────────────────────────────────────
_font_path = pathlib.Path(__file__).parent / "fonts" / "Super Funtime.ttf"
_font_b64 = base64.b64encode(_font_path.read_bytes()).decode() if _font_path.exists() else ""

_font_css = f"""@font-face {{
    font-family: 'SuperFuntime';
    src: url(data:font/truetype;base64,{_font_b64}) format('truetype');
    font-weight: normal; font-style: normal;
}}""" if _font_b64 else ""

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css');
html, body, [class*="st-"] { font-family: 'Pretendard', -apple-system, sans-serif; }
.block-container { max-width: 520px; padding: 0 1rem 4rem; }
header[data-testid="stHeader"] { background: transparent; }

/* 로고 배너 */
.logo-banner {
    text-align: center; padding: 14px 16px 12px;
    background: radial-gradient(ellipse at center, #f0f7c4 0%, #e4f5df 40%, #d8f0d2 70%, #c8e8c4 100%);
    border-radius: 0 0 16px 16px; margin: -1rem -1rem 1rem;
}
.logo-sub { font-size: 10px; color: #6a9a5b; letter-spacing: 1px; margin-bottom: 0; }
.logo-main {
    display: flex; align-items: center; justify-content: center; gap: 3px;
    padding: 4px 0 2px; margin: 0 auto; width: 100%;
}
.glass-letter {
    display: inline-block; position: relative;
    font-size: 50px; font-weight: normal;
    font-family: 'SuperFuntime', 'Pretendard', sans-serif;
    color: rgba(240,128,162,0.9);
    padding: 2px 1px;
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.3) 0%,
        rgba(240,128,162,0.06) 40%,
        rgba(255,255,255,0.15) 100%
    );
    -webkit-background-clip: padding-box; background-clip: padding-box;
    text-shadow:
        0 1px 2px rgba(255,255,255,0.6),
        0 -1px 1px rgba(240,128,162,0.12),
        0 2px 8px rgba(240,128,162,0.18);
    filter: drop-shadow(0 2px 5px rgba(240,128,162,0.2));
    -webkit-text-stroke: 0.5px rgba(240,128,162,0.25);
    transition: transform 0.3s ease;
    cursor: default;
    line-height: 1;
}
.glass-letter::after {
    content: attr(data-char);
    position: absolute; top: 0; left: 0; right: 0;
    color: transparent;
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.65) 0%,
        rgba(255,255,255,0) 45%
    );
    -webkit-background-clip: text; background-clip: text;
    pointer-events: none;
}
.glass-letter:hover {
    transform: translateY(-3px) scale(1.06);
    filter: drop-shadow(0 6px 12px rgba(240,128,162,0.3));
    color: rgba(240,128,162,1);
}
.glass-letter:nth-child(1) { animation: letterFloat 3s ease-in-out 0.0s infinite; }
.glass-letter:nth-child(2) { animation: letterFloat 3s ease-in-out 0.12s infinite; }
.glass-letter:nth-child(3) { animation: letterFloat 3s ease-in-out 0.24s infinite; }
.glass-letter:nth-child(4) { animation: letterFloat 3s ease-in-out 0.36s infinite; }
.glass-letter:nth-child(5) { animation: letterFloat 3s ease-in-out 0.48s infinite; }
.glass-space { width: 14px; }
.glass-letter:nth-child(7) { animation: letterFloat 3s ease-in-out 0.6s infinite; }
.glass-letter:nth-child(8) { animation: letterFloat 3s ease-in-out 0.72s infinite; }
.glass-letter:nth-child(9) { animation: letterFloat 3s ease-in-out 0.84s infinite; }
@keyframes letterFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
}
.logo-reflect {
    display: flex; gap: 2px; justify-content: center;
    font-size: 50px; font-weight: normal; line-height: 1;
    font-family: 'SuperFuntime', 'Pretendard', sans-serif;
    color: transparent;
    background: linear-gradient(180deg, rgba(240,128,162,0.2) 0%, rgba(255,255,255,0) 60%);
    -webkit-background-clip: text; background-clip: text;
    transform: scaleY(-0.3); transform-origin: top;
    opacity: 0.25; pointer-events: none;
    margin-top: -2px;
    filter: blur(1px);
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

/* 섹션 타이틀 */
.sec-title {
    font-size: 18px; font-weight: 700; margin: 1.5rem 0 0.8rem;
    display: flex; align-items: center; gap: 8px;
}

/* 카드 */
.card {
    background: #fff; border-radius: 16px; padding: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #E8E8EE;
    margin-bottom: 10px;
}

/* 태그 */
.tag {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 600; color: #fff;
}
.tag-단맛 { background: #D94F4F; } .tag-짠맛 { background: #EDBE9A; color: #7A5C2E; }
.tag-칩 { background: #3B9B8E; } .tag-쿠키 { background: #F08E76; }
.tag-젤리 { background: #9DC8D6; color: #2C6E7A; } .tag-견과류 { background: #C4A46C; }
.tag-음료 { background: #6BB5C5; } .tag-매운맛 { background: #D94F4F; }

/* 트렌드 캐러셀 */
.trend-scroll { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; }
.trend-scroll::-webkit-scrollbar { display: none; }
.trend-card {
    flex: 0 0 180px; background: #fff; border-radius: 16px; padding: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #E8E8EE;
}
.trend-card h4 { font-size: 14px; font-weight: 700; margin: 6px 0 2px; }
.trend-card p { font-size: 11px; color: #6B6B80; margin: 0; }

/* 스낵 그리드 */
.snack-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.snack-card {
    background: #fff; border-radius: 16px; padding: 14px; text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #E8E8EE;
}
.snack-card img { width: 64px; height: 64px; border-radius: 12px; object-fit: cover; }
.snack-card .name { font-size: 13px; font-weight: 600; margin: 6px 0 2px; }
.snack-card .price { font-size: 11px; color: #6B6B80; }

/* 요청 카드 */
.req-card {
    background: #fff; border-radius: 14px; padding: 12px 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #E8E8EE;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px;
}
.req-card .info h4 { font-size: 13px; font-weight: 600; margin: 0; }
.req-card .info .meta { font-size: 11px; color: #6B6B80; }

/* 쿠팡 결과 */
.cpg-item {
    display: flex; align-items: center; gap: 10px; padding: 10px;
    background: #F7F7F9; border-radius: 10px; margin-bottom: 6px; cursor: pointer;
}
.cpg-item img { width: 52px; height: 52px; border-radius: 8px; object-fit: cover; }
.cpg-item .cpg-name { font-size: 13px; font-weight: 600; }
.cpg-item .cpg-price { font-size: 12px; color: #6B6B80; }

/* AI 결과 */
.ai-result {
    background: linear-gradient(135deg, #F5F2E8, #E8F2F4);
    border-radius: 16px; padding: 18px; border: 1px solid #EDBE9A;
    font-size: 13px; line-height: 1.8; white-space: pre-wrap;
}

/* Streamlit 기본 요소 커스텀 */
div[data-testid="stHorizontalBlock"] { gap: 8px; }
.stButton > button {
    border-radius: 12px; font-weight: 600; transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

if _font_css:
    st.markdown(f"<style>{_font_css}</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State 초기화
# ─────────────────────────────────────────────
def init_state():
    if "snacks" not in st.session_state:
        st.session_state.snacks = [
            {"id": 1, "name": "허니버터칩", "category": "짠맛", "image": "https://placehold.co/120x120/FFD700/333?text=HBC", "price": 2500, "likes": 14},
            {"id": 2, "name": "초코파이", "category": "단맛", "image": "https://placehold.co/120x120/8B4513/fff?text=CP", "price": 4800, "likes": 22},
            {"id": 3, "name": "새우깡", "category": "짠맛", "image": "https://placehold.co/120x120/FF6347/fff?text=SU", "price": 1800, "likes": 9},
            {"id": 4, "name": "빼빼로", "category": "단맛", "image": "https://placehold.co/120x120/DC143C/fff?text=PP", "price": 1500, "likes": 18},
            {"id": 5, "name": "하리보 골드베렌", "category": "젤리", "image": "https://placehold.co/120x120/FF69B4/fff?text=HB", "price": 3200, "likes": 11},
            {"id": 6, "name": "프링글스 오리지널", "category": "칩", "image": "https://placehold.co/120x120/228B22/fff?text=PR", "price": 3500, "likes": 16},
            {"id": 7, "name": "오레오", "category": "쿠키", "image": "https://placehold.co/120x120/1a1a2e/fff?text=OR", "price": 2800, "likes": 13},
            {"id": 8, "name": "칸쵸", "category": "쿠키", "image": "https://placehold.co/120x120/D2691E/fff?text=KC", "price": 1600, "likes": 7},
        ]
    if "requests" not in st.session_state:
        st.session_state.requests = [
            {"id": 1, "name": "포카칩 어니언", "category": "칩", "votes": 5},
            {"id": 2, "name": "마이쮸 딸기", "category": "젤리", "votes": 3},
            {"id": 3, "name": "꼬북칩 콘스프맛", "category": "칩", "votes": 8},
        ]
    if "cat_votes" not in st.session_state:
        st.session_state.cat_votes = {"단맛": 35, "짠맛": 28, "칩": 22, "쿠키": 15, "젤리": 12, "견과류": 5, "음료": 8}
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "ai_result" not in st.session_state:
        st.session_state.ai_result = ""
    if "naver_results" not in st.session_state:
        st.session_state.naver_results = []

init_state()

CAT_COLORS = {"단맛": "#D94F4F", "짠맛": "#EDBE9A", "칩": "#3B9B8E", "쿠키": "#F08E76",
              "젤리": "#9DC8D6", "견과류": "#C4A46C", "음료": "#6BB5C5", "매운맛": "#D94F4F"}
CATEGORIES = list(CAT_COLORS.keys())

TREND_SNACKS = [
    {"name": "두바이 초콜릿", "desc": "SNS 대란! 피스타치오 카다이프", "tag": "단맛"},
    {"name": "탕후루 젤리", "desc": "바삭 코팅 과일젤리 신상", "tag": "젤리"},
    {"name": "먹태깡", "desc": "품절대란 먹태 과자의 귀환", "tag": "짠맛"},
    {"name": "치토스 플레이밍 핫", "desc": "매운맛 트렌드 최강자", "tag": "매운맛"},
]


# ─────────────────────────────────────────────
# 네이버 쇼핑 검색 API
# ─────────────────────────────────────────────
def search_naver_shopping(keyword, display=5):
    try:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
    except Exception:
        return None, "네이버 API 키가 설정되지 않았습니다. .streamlit/secrets.toml을 확인해주세요."

    if client_id.startswith("여기에"):
        return None, "네이버 API 키를 실제 키로 교체해주세요. (https://developers.naver.com)"

    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": keyword, "display": display, "sort": "sim"}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            results = []
            for item in data.get("items", [])[:display]:
                name = item.get("title", "").replace("<b>", "").replace("</b>", "")
                results.append({
                    "name": name,
                    "price": int(item.get("lprice", 0)),
                    "image": item.get("image", ""),
                    "link": item.get("link", ""),
                    "mall": item.get("mallName", ""),
                })
            return results, None
        elif res.status_code == 401:
            return None, "API 인증 실패 — Client ID/Secret을 확인해주세요."
        else:
            return None, f"API 오류 (HTTP {res.status_code})"
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 오류: {str(e)}"


# ─────────────────────────────────────────────
# Google Gemini API
# ─────────────────────────────────────────────
def call_gemini(prompt_text):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return "Gemini API 키가 설정되지 않았습니다. .streamlit/secrets.toml을 확인해주세요."

    if api_key.startswith("여기에"):
        return "Gemini API 키를 실제 키로 교체해주세요. (https://aistudio.google.com/apikey)"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500},
    }
    try:
        res = requests.post(url, json=body, timeout=30)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
            return f"API 오류: {err}"
    except Exception as e:
        return f"요청 실패: {str(e)}"


# ─────────────────────────────────────────────
# 네비게이션
# ─────────────────────────────────────────────
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🏠 홈", use_container_width=True, type="primary" if st.session_state.page == "main" else "secondary"):
        st.session_state.page = "main"
        st.rerun()
with col_nav2:
    if st.button("⚙️ 관리자", use_container_width=True, type="primary" if st.session_state.page == "admin" else "secondary"):
        st.session_state.page = "admin"
        st.rerun()


# ═════════════════════════════════════════════
# 메인 페이지
# ═════════════════════════════════════════════
if st.session_state.page == "main":

    # ── 로고 배너 ──
    st.markdown("""
    <div class="logo-banner">
        <div class="logo-sub">정책기획팀</div>
        <div class="logo-main"><span class="glass-letter" data-char="S">S</span><span class="glass-letter" data-char="n">n</span><span class="glass-letter" data-char="a">a</span><span class="glass-letter" data-char="c">c</span><span class="glass-letter" data-char="k">k</span><span class="glass-space"></span><span class="glass-letter" data-char="L">L</span><span class="glass-letter" data-char="a">a</span><span class="glass-letter" data-char="b">b</span></div>
        <div class="logo-reflect">Snack Lab</div>
        <p style="font-size:10px;color:#6a9a5b;margin-top:2px">🍪 최적의 간식조합 찾기</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: 트렌드 ──
    st.markdown('<div class="sec-title">🔥 이번 주 핫한 신상 과자</div>', unsafe_allow_html=True)
    trend_html = '<div class="trend-scroll">'
    for t in TREND_SNACKS:
        color = CAT_COLORS.get(t["tag"], "#6B7280")
        trend_html += f'''<div class="trend-card">
            <span class="tag" style="background:{color}">#{t["tag"]}</span>
            <h4>{t["name"]}</h4><p>{t["desc"]}</p>
        </div>'''
    trend_html += '</div>'
    st.markdown(trend_html, unsafe_allow_html=True)

    # ── Section 2: 대시보드 ──
    st.markdown('<div class="sec-title">📊 직원 취향 분석</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        cats = st.session_state.cat_votes
        fig_donut = go.Figure(data=[go.Pie(
            labels=list(cats.keys()), values=list(cats.values()),
            hole=0.6, marker=dict(colors=[CAT_COLORS.get(k, "#6B7280") for k in cats]),
            textinfo="label+percent", textfont_size=11,
        )])
        fig_donut.update_layout(
            showlegend=False, margin=dict(t=20, b=20, l=10, r=10), height=220,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_c2:
        sorted_snacks = sorted(st.session_state.snacks, key=lambda x: x["likes"], reverse=True)[:5]
        fig_bar = go.Figure(data=[go.Bar(
            x=[s["name"][:5] for s in sorted_snacks],
            y=[s["likes"] for s in sorted_snacks],
            marker_color=[CAT_COLORS.get(s["category"], "#6B7280") for s in sorted_snacks],
            marker_cornerradius=6,
        )])
        fig_bar.update_layout(
            showlegend=False, margin=dict(t=20, b=20, l=10, r=10), height=220,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont_size=10), yaxis=dict(tickfont_size=10, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ── Section 3: 이달의 다과 피드백 ──
    st.markdown('<div class="sec-title">👍 이달의 다과 피드백</div>', unsafe_allow_html=True)

    snack_cols = st.columns(2)
    for i, s in enumerate(st.session_state.snacks):
        with snack_cols[i % 2]:
            tag_color = CAT_COLORS.get(s["category"], "#6B7280")
            st.markdown(f"""<div class="snack-card">
                <img src="{s['image']}" onerror="this.src='https://placehold.co/120x120/ccc/666?text=Snack'">
                <div class="name">{s['name']}</div>
                <div class="price">{s['price']:,}원</div>
                <span class="tag" style="background:{tag_color}">{s['category']}</span>
            </div>""", unsafe_allow_html=True)
            if st.button(f"👍 재구매 ({s['likes']})", key=f"like_{s['id']}", use_container_width=True):
                s["likes"] += 1
                cat = s["category"]
                st.session_state.cat_votes[cat] = st.session_state.cat_votes.get(cat, 0) + 1
                st.rerun()

    # ── Section 4: 간식 요청하기 ──
    st.markdown('<div class="sec-title">🙋 간식 요청하기</div>', unsafe_allow_html=True)

    sorted_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)
    for r in sorted_reqs:
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            tag_color = CAT_COLORS.get(r["category"], "#6B7280")
            st.markdown(f"""<div class="req-card"><div class="info">
                <h4>{r['name']} <span class="tag" style="background:{tag_color}">{r['category']}</span></h4>
                <div class="meta">{r['votes']}명 요청</div>
            </div></div>""", unsafe_allow_html=True)
        with col_r2:
            if st.button(f"나도 +1", key=f"vote_{r['id']}", use_container_width=True):
                r["votes"] += 1
                st.toast("요청에 +1 했어요! 🙌")
                st.rerun()

    # ── 새 간식 요청 ──
    st.markdown("---")
    st.markdown("#### 🆕 새 간식 요청")

    req_name = st.text_input("원하는 과자 이름 입력 (선택)", placeholder="예: 포카칩 어니언", key="req_name_input")

    # 네이버 쇼핑 검색
    col_s1, col_s2 = st.columns([3, 1])
    with col_s2:
        search_clicked = st.button("🔍 네이버검색", use_container_width=True)

    if search_clicked:
        if not req_name:
            st.warning("검색할 과자 이름을 먼저 입력해주세요.")
        else:
            with st.spinner("네이버 쇼핑에서 검색 중..."):
                results, err = search_naver_shopping(req_name)
            if err:
                st.warning(err)
            elif results:
                st.session_state.naver_results = results
            else:
                st.info("검색 결과가 없습니다.")

    if st.session_state.get("naver_results"):
        st.markdown("**검색 결과** (클릭하여 선택)")
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
                    st.session_state.naver_results = []
                    st.toast(f"'{item['name'][:20]}' 선택됨!")
                    st.rerun()

    # 카테고리 태그
    st.markdown("**카테고리 선택**")
    tag_cols = st.columns(4)
    selected_cat = st.session_state.get("selected_cat", "")
    for ci, cat in enumerate(CATEGORIES):
        with tag_cols[ci % 4]:
            btn_type = "primary" if selected_cat == cat else "secondary"
            if st.button(f"#{cat}", key=f"cat_{cat}", use_container_width=True, type=btn_type):
                st.session_state.selected_cat = cat
                st.rerun()

    if st.button("🚀 요청하기", use_container_width=True, type="primary"):
        sel_item = st.session_state.get("selected_naver")
        name = sel_item["name"] if sel_item else req_name
        cat = st.session_state.get("selected_cat", "")

        if not name and not cat:
            st.warning("과자명 또는 카테고리를 선택해주세요.")
        else:
            display_name = name or f"{cat} 카테고리 요청"
            display_cat = cat or "기타"
            existing = next((r for r in st.session_state.requests if r["name"] == display_name), None)
            if existing:
                existing["votes"] += 1
                st.toast("이미 있는 요청이에요! +1 했습니다")
            else:
                st.session_state.requests.append({
                    "id": int(time.time() * 1000),
                    "name": display_name, "category": display_cat, "votes": 1,
                })
                st.session_state.cat_votes[display_cat] = st.session_state.cat_votes.get(display_cat, 0) + 1
                st.toast("새 요청이 등록되었어요! 🎉")
            st.session_state.selected_naver = None
            st.session_state.selected_cat = ""
            st.session_state.naver_results = []
            st.rerun()


# ═════════════════════════════════════════════
# 관리자 페이지
# ═════════════════════════════════════════════
elif st.session_state.page == "admin":

    st.markdown("""
    <div class="logo-banner" style="padding:20px">
        <div class="logo-sub">관리자 모드</div>
        <div class="logo-main" style="font-size:28px">Snack Lab</div>
    </div>
    """, unsafe_allow_html=True)

    # 인증
    if not st.session_state.admin_auth:
        st.markdown("### 🔐 관리자 인증")
        admin_pw = st.text_input("비밀번호 입력", type="password", key="admin_pw_input")
        if st.button("확인", use_container_width=True, type="primary"):
            try:
                correct_pw = st.secrets["ADMIN_PASSWORD"]
            except Exception:
                correct_pw = "1234"
            if admin_pw == correct_pw:
                st.session_state.admin_auth = True
                st.toast("관리자 모드 진입 🔓")
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    else:
        # ── 피드백 리스트 관리 ──
        st.markdown("#### 📋 현재 피드백 리스트")
        for s in st.session_state.snacks:
            tag_color = CAT_COLORS.get(s["category"], "#6B7280")
            st.markdown(f"""<div class="req-card"><div class="info">
                <h4>{s['name']} <span class="tag" style="background:{tag_color}">{s['category']}</span></h4>
                <div class="meta">👍 {s['likes']}표 · {s['price']:,}원</div>
            </div></div>""", unsafe_allow_html=True)

        # ── 신규 요청 → 메인 등록 ──
        st.markdown("---")
        st.markdown("#### 🙋 신규 요청 → 메인 등록")
        reqs_to_add = []
        for r in sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True):
            if st.checkbox(f"{r['name']} ({r['category']}) - {r['votes']}명 요청", key=f"add_{r['id']}"):
                reqs_to_add.append(r)

        if st.button("✅ 선택 항목 메인에 추가", use_container_width=True, type="primary"):
            count = 0
            for r in reqs_to_add:
                if not any(s["name"] == r["name"] for s in st.session_state.snacks):
                    tag_color = CAT_COLORS.get(r["category"], "6B7280").lstrip("#")
                    st.session_state.snacks.append({
                        "id": int(time.time() * 1000) + count,
                        "name": r["name"], "category": r["category"],
                        "image": f"https://placehold.co/120x120/{tag_color}/fff?text={r['name'][:2]}",
                        "price": 0, "likes": r["votes"],
                    })
                    count += 1
            if count:
                st.toast(f"{count}개 상품이 추가되었어요!")
                st.rerun()
            else:
                st.warning("추가할 항목을 선택해주세요.")

        # ── AI 10만원 장바구니 ──
        st.markdown("---")
        st.markdown("#### 🤖 AI 10만원 장바구니 생성기")
        st.caption("Google Gemini AI가 직원 데이터를 분석하여 예산 10만원 맞춤 추천을 생성합니다.")

        if st.button("🤖 AI 10만원 조합 생성", use_container_width=True, type="primary"):
            cats = st.session_state.cat_votes
            top_snacks = sorted(st.session_state.snacks, key=lambda x: x["likes"], reverse=True)
            top_reqs = sorted(st.session_state.requests, key=lambda x: x["votes"], reverse=True)

            prompt = f"""당신은 회사 탕비실 간식 구매를 돕는 AI 어시스턴트입니다.
아래 데이터를 분석하여 예산 10만원(100,000원) 이내로 최적의 과자 장바구니를 구성해주세요.

[직원 카테고리 선호도]
{chr(10).join(f'- {k}: {v}표' for k, v in sorted(cats.items(), key=lambda x: x[1], reverse=True))}

[현재 탕비실 과자 재구매 투표]
{chr(10).join(f'- {s["name"]} ({s["category"]}, {s["price"]:,}원): 👍 {s["likes"]}표' for s in top_snacks)}

[직원 신규 요청]
{chr(10).join(f'- {r["name"]} ({r["category"]}): {r["votes"]}명 요청' for r in top_reqs)}

다음 형식으로 답변해주세요:
1. 📊 직원 취향 분석 요약 (3줄 이내)
2. 🛒 추천 장바구니 (상품명, 카테고리, 예상 가격, 수량, 소계를 표로 정리)
3. 💰 총액 / 잔액
4. 📝 추천 사유 (왜 이 조합이 최적인지 3줄 이내)

실제 한국 편의점/마트에서 구매 가능한 과자 위주로 현실적인 가격을 반영해주세요.
총액이 100,000원을 넘지 않아야 합니다."""

            with st.spinner("🤖 Gemini AI가 분석 중입니다..."):
                result = call_gemini(prompt)
            st.session_state.ai_result = result

        if st.session_state.ai_result:
            st.markdown(f'<div class="ai-result">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

        # ── 로그아웃 ──
        st.markdown("---")
        if st.button("🔒 로그아웃", use_container_width=True):
            st.session_state.admin_auth = False
            st.rerun()
