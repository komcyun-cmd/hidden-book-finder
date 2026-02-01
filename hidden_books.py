import streamlit as st
import requests
import random
import datetime
import hashlib

# ===============================
# 🔐 알라딘 TTBKey
# ===============================
TTB_KEY = st.secrets["ALADIN_TTB_KEY"].strip().replace("\n", "")

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저", layout="centered")
st.title("📚 오늘의 숨은 명저")
st.caption("알라딘 Open API 기반 · 근거 있는 개인 독서 추천")

# ===============================
# 기분 → 탐색 의도
# ===============================
MOOD_PROFILE = {
    "생각이 깊어지는 책": {
        "intent": "개념과 사유 중심의 독서",
        "focus": "사고 확장, 개념 정리, 관점 성찰"
    },
    "조용히 읽히는 책": {
        "intent": "문장 밀도 중심의 독서",
        "focus": "문체, 호흡, 정서적 안정"
    },
    "관점이 흔들리는 책": {
        "intent": "기존 인식에 대한 재검토",
        "focus": "사회 구조, 역사적 맥락, 문제 제기"
    },
    "마음이 정리되는 책": {
        "intent": "내면 정돈을 위한 독서",
        "focus": "삶의 태도, 감정 수용, 자기 인식"
    }
}

MOOD_KEYWORDS = {
    "생각이 깊어지는 책": ["철학", "사유", "존재"],
    "조용히 읽히는 책": ["에세이", "문장"],
    "관점이 흔들리는 책": ["사회", "역사"],
    "마음이 정리되는 책": ["삶", "태도"]
}

BLOCK_WORDS = ["성공", "부자", "재테크", "주식", "유튜브"]

# ===============================
# 알라딘 API
# ===============================
def search_aladin(keyword):
    url = "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTB_KEY,
        "Query": keyword,
        "QueryType": "Keyword",
        "MaxResults": 30,
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }
    r = requests.get(url, params=params, timeout=7)
    r.raise_for_status()
    return r.json().get("item", [])

def filter_books(items):
    results = []
    for b in items:
        title = b.get("title", "")
        desc = b.get("description", "")

        if any(w in title for w in BLOCK_WORDS):
            continue
        if len(desc) < 60:
            continue

        results.append({
            "title": title,
            "desc": desc,
            "link": b.get("link")
        })
    return results

# ===============================
# 고정 랜덤
# ===============================
def pick_with_seed(items, seed):
    seed_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    random.seed(seed_val)
    return random.choice(items)

# ===============================
# 책 찾기
# ===============================
def find_books(mood):
    keywords = MOOD_KEYWORDS[mood][:]
    random.shuffle(keywords)

    for kw in keywords:
        books = filter_books(search_aladin(kw))
        if books:
            return books
    return []

# ===============================
# 🧠 전문적 책 선정 이유 생성
# ===============================
def build_reason(book, mood):
    profile = MOOD_PROFILE[mood]
    desc = book["desc"]

    return f"""
이 책은 **{profile['intent']}**에 적합한 텍스트입니다.

소개 글을 보면, 단순한 정보 전달보다는  
**{profile['focus']}**에 초점을 두고 서술되어 있으며,  
주제를 빠르게 결론으로 몰아가기보다 독자가 생각을 이어가도록 구성되어 있습니다.

특히 이 책은 유행하는 메시지나 즉각적인 해답을 제시하기보다,  
맥락과 흐름을 따라가며 독자의 사고를 점진적으로 확장시키는 방식이 특징입니다.

그래서 오늘 같은 독서 기분에  
**가볍게 소비되지 않고, 읽은 뒤 생각이 남는 책**으로 추천할 만합니다.
""".strip()

# ===============================
# UI
# ===============================
mood = st.radio(
    "오늘의 독서 방향",
    list(MOOD_KEYWORDS.keys())
)

if "retry" not in st.session_state:
    st.session_state.retry = 0

if st.button("오늘의 숨은 명저 찾기"):
    st.session_state.retry = 0

if st.button("🔁 다른 책 보기"):
    st.session_state.retry += 1

with st.spinner("알라딘 서가를 탐색 중입니다…"):
    books = find_books(mood)

if not books:
    st.warning("오늘은 조건에 맞는 책을 찾지 못했습니다.")
    st.stop()

today = datetime.date.today().isoformat()
seed = f"{today}{mood}{st.session_state.retry}"
book = pick_with_seed(books, seed)

st.divider()

st.markdown(
    f"<h2><a href='{book['link']}' target='_blank'>{book['title']}</a></h2>",
    unsafe_allow_html=True
)

st.markdown("### 📖 이 책을 고른 이유")
st.write(build_reason(book, mood))

with st.expander("📘 책 소개"):
    st.write(book["desc"])

st.caption("※ 알라딘 Open API · 추천 이유는 책 소개 기반으로 생성됩니다.")