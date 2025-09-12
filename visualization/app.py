import re
import json
import ast
import pandas as pd
import streamlit as st


st.set_page_config(page_title="JD 추천 결과", layout="wide")

# 'Paperlogy-8ExtraBold' 폰트 추가 및 UI 스타일 정의
st.markdown("""
<style>
@font-face {
    font-family: 'Paperlogy-8ExtraBold';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-8ExtraBold.woff2') format('woff2');
    font-weight: 800;
    font-style: normal;
}

:root {
    --brand: #760023; /* 메인 브랜드 색상 (와인색) */
    --brand-light: #fdf7f9; /* 밝은 배경색 */
    --brand-border: #e9d2d9; /* 테두리 색상 */
    --bg: #f9fafb; /* 전체 배경색 */
    --text: #1f2430; /* 기본 텍스트 색상 */
    --muted: #6b7280; /* 연한 텍스트 색상 */
    --card-bg: #ffffff; /* 카드 배경색 */
    --font-family: 'Paperlogy-8ExtraBold', sans-serif; /* 폰트를 Paperlogy로 변경 */
}
html, body, [data-testid="stApp"], button, input, textarea {
    font-family: var(--font-family) !important;
}
h1, h2, h3 {
    color: var(--brand);
    font-family: var(--font-family);
}

.jd-card {
    border: 1px solid var(--brand-border);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0 20px 0;
    background: var(--card-bg);
    box-shadow: 0 6px 18px rgba(0,0,0,.03);
}
.jd-header {
    font-size: 24px;
    font-weight: 700;
    color: var(--brand);
    margin-bottom: 8px;
}

.jd-summary {
    font-size: 15px;
    color: var(--muted);
    margin-bottom: 16px; 
    padding-bottom: 0;
    line-height: 1.7;
}

button {
    background-color: var(--brand) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    width: 100%;
}
button:hover {
    opacity: 0.9 !important;
}

.cand-reason {
    background: var(--brand-light);
    border: 1px solid var(--brand-border);
    border-radius: 8px;
    padding: 16px;
    margin-top: 8px;
    font-size: 16px; 
    color: #333;
    white-space: pre-wrap;
    line-height: 1.8;
}
.cand-reason strong {
    color: var(--brand);
    font-weight: 700;
    display: block;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("AI 추천 결과")


# summary.txt 파일에서 JD 요약 정보 로드
@st.cache_data
def load_summaries(filepath="summary.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            summaries = [line.strip() for line in f if line.strip()]
        return summaries
    except FileNotFoundError:
        st.error(f"`{filepath}` 파일을 찾을 수 없습니다. 앱과 같은 경로에 파일을 위치시켜 주세요.")
        return []

# result.txt 파서
def parse_result_text(text: str):
    for pat in (r"\[\s*\{'selected'", r'\[\s*\{"selected"'):
        m = re.search(pat, text)
        if m:
            start = m.start()
            break
    else:
        raise ValueError("결과 리스트 시작([{'selected'...])을 찾지 못했습니다.")
    end = text.rfind(']')
    if end == -1 or end <= start:
        raise ValueError("결과 리스트의 닫는 대괄호가 없습니다.")
    body = text[start:end+1].strip()
    try:
        return ast.literal_eval(body)
    except Exception:
        repaired = (body
            .replace("None","null").replace("True","true").replace("False","false"))
        repaired = re.sub(r"'", '"', repaired)
        return json.loads(repaired)

st.sidebar.header("파일 업로드")
up_xlsx = st.sidebar.file_uploader("rag.xlsx 업로드", type=["xlsx"])
up_result = st.sidebar.file_uploader("result.txt 업로드", type=["txt","json"])

base = st.sidebar.radio("idx 기준", ["1-based (엑셀)","0-based (파이썬)"], index=0)
one_based = base.startswith("1-")

def load_df(filepath="./rag.xlsx"):
    if up_xlsx: return pd.read_excel(up_xlsx)
    try: return pd.read_excel(filepath)
    except: return None

def load_result(filepath="result.txt"):
    if up_result:
        text = up_result.read().decode("utf-8", errors="ignore")
    else:
        try:
            with open(filepath,"r",encoding="utf-8") as f: text = f.read()
        except: return None
    return parse_result_text(text)

df = load_df(filepath="./data/rag.xlsx")
result_data = load_result("./visualization/result.txt")
JD_SUMMARIES = load_summaries("./visualization/summary.txt")

if df is None or result_data is None:
    st.info("좌측 사이드바에서 rag.xlsx와 result.txt를 업로드하세요.")
    st.stop()

def row_by_pos(df: pd.DataFrame, pos: int, one_based: bool) -> pd.Series | None:
    try: p = int(pos)
    except: return None
    if one_based: p -= 1
    if p < 0 or p >= len(df): return None
    return df.iloc[p]

SUMMARY_COLS_MAP = {
    "성별": ["성별","gender"],
    "나이": ["나이","age"],
    "거주지역": ["거주지역", "지역"],
}

def pick(series, candidates):
    for c in candidates:
        if c in series.index and pd.notna(series[c]) and str(series[c]).strip() != "":
            return str(series[c]).strip()
    return "N/A"

if 'expanded_rows' not in st.session_state:
    st.session_state.expanded_rows = set()

def toggle_expand(jd_num, rank):
    key = f"{jd_num}_{rank}"
    if key in st.session_state.expanded_rows:
        st.session_state.expanded_rows.remove(key)
    else:
        st.session_state.expanded_rows.add(key)

st.subheader("JD 선택")
jd_num = st.number_input("결과를 볼 JD 번호", min_value=1, max_value=len(result_data),
                         value=1, step=1, label_visibility="collapsed")
selected = result_data[jd_num-1].get("selected", [])[:3]

jd_summary = JD_SUMMARIES[jd_num - 1] if jd_num <= len(JD_SUMMARIES) else "요약 정보가 없습니다."

st.markdown(f'<div class="jd-card"><div class="jd-header">JD #{jd_num} 추천 후보</div>'
            f'<div class="jd-summary">{jd_summary}</div>', 
            unsafe_allow_html=True)


if not selected:
    st.markdown('<div>추천 후보가 없습니다.</div>', unsafe_allow_html=True)
else:
    COLUMN_WIDTHS = [0.5, 0.7, 0.7, 1.5, 0.8]
    
    header_cols = st.columns(COLUMN_WIDTHS)
    header_cols[0].markdown("**번호**")
    header_cols[1].markdown("**성별**")
    header_cols[2].markdown("**나이**")
    header_cols[3].markdown("**거주 지역**")

    st.markdown("<hr style='margin: 8px 0; border-color: #e9d2d9;'>", unsafe_allow_html=True)

    for rank, item in enumerate(selected, start=1):
        idx_pos = item.get("idx")
        reason = item.get("reason", "추천 이유가 없습니다.")
        s = row_by_pos(df, idx_pos, one_based)

        row_container = st.container()
        if s is None:
            row_container.warning(f"{idx_pos}번 지원자 데이터를 찾을 수 없습니다.")
            continue

        info = {key: pick(s, cands) for key, cands in SUMMARY_COLS_MAP.items()}

        cols = row_container.columns(COLUMN_WIDTHS)
        cols[0].write(str(idx_pos))
        cols[1].write(info.get("성별", "N/A"))
        cols[2].write(info.get("나이", "N/A"))
        cols[3].write(info.get("거주지역", "N/A"))

        key = f"{jd_num}_{rank}"
        is_expanded = key in st.session_state.expanded_rows
        button_text = "닫기" if is_expanded else "열람하기"
        
        with cols[4]:
            st.button(button_text, key=f"btn_{key}", on_click=toggle_expand, args=(jd_num, rank))

        if is_expanded:
            sentences = re.split(r'(?<=[.?!])\s+', reason)
            formatted_reason = '<br>'.join(s.strip() for s in sentences if s.strip())
            
            row_container.markdown(f"<div class='cand-reason'><strong>추천 이유</strong>{formatted_reason}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1px; background: #f3f4f6; margin: 12px 0;'></div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
