import streamlit as st
import time
import base64
import pathlib
import requests
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 폰트 로드 유틸리티
# ─────────────────────────────────────────────
def get_font_css(font_name, file_name):
    font_path = pathlib.Path(__file__).parent / "fonts" / file_name
    if font_path.exists():
        b64 = base64.b64encode(font_path.read_bytes()).decode()
        return f"""@font-face {{ font-family: '{font_name}'; src: url(data:font/truetype;base64,{b64}); }}"""
    return ""

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="Snack Lab", page_icon="🍬", layout="centered")

st.markdown(f"""
<style>
{get_font_css('SuperFuntime', 'Super Funtime.ttf')}
{get_font_css('NanumGothic', 'NanumGothic.otf')}

html, body {{ font-family: 'NanumGothic', sans-serif; background-color: #fcfcfc; }}
.block-container {{ max-width: 520px; padding: 1rem; }}

/* 투명한 유리 질감 패널 */
.glass-box {{
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(15px);
    border: 0.5px solid rgba(240, 128, 162, 0.2);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
}}

/* 로고 배너 */
.logo-banner {{ text-align: center; padding: 20px; margin-bottom: 20px; }}
.star-symbol {{ color: #F080A2; font-size: 24px; animation: float 3s infinite; display: inline-block; }}
@keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}

/* 로고 글씨 */
.glass-letter {{
    display: inline-block; position: relative; font-size: 50px;
    font-family: 'SuperFuntime', sans-serif; color: rgba(240,128,162,0.9);
    padding: 2px 1px; transition: transform 0.3s ease;
    text-shadow: 0 1px 2px rgba(255,255,255,0.6);
    filter: drop-shadow(0 2px 5px rgba(240,128,162,0.2));
}}

/* 폰트 및 태그 크기 조정 */
.sec-title {{ font-size: 14px; font-weight: normal; margin: 1rem 0; color: #555; }}
.tag {{ font-size: 8px; padding: 2px 6px; border-radius: 4px; background: #eee; margin-right: 3px; }}
.stButton > button {{ border-radius: 6px; border: 0.5px solid #ddd; background: white; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 나머지 로직은 이전과 동일하게 유지하되,
# 메인 화면 가격 표시 삭제 및 등록 로직 수정
# ─────────────────────────────────────────────

# (중략 - init_state 및 기타 API 함수는 이전과 동일)

# 메인 페이지 카드 렌더링 예시 (가격 표시 삭제)
# st.markdown(f"""
# <div class="glass-box">
#     <div class="name">{s['name']}</div>
#     <div class="tag-container">{tag_html}</div>
# </div>
# """, unsafe_allow_html=True)
