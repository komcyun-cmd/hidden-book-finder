import streamlit as st
import requests
import random
import datetime
import hashlib

# ===============================
# 🔐 알라딘 TTBKey (줄바꿈/공백 제거)
# ===============================
TTB_KEY = st.secrets["ALADIN_TTB_KEY"].strip().replace("\n", "")

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저", layout="centered")
st.title("📚 오늘의 숨은 명저")
st.caption("알라딘 공식 Open API · 오늘의 책 + 다른 선택지")

# ===============================
# 기분 → 키워드
# ===============================
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
        if len(desc) < 40:
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
        items = search_aladin(kw)
        books = filter_books(items)
        if books:
            return books
    return []

# ===============================
# 선정 이유
# ===============================
REASONS = {
    "생각이 깊어지는 책": [
        "답을 주기보다 질문을 남기는 책입니다.",
        "사고의 속도를 자연스럽게 늦춰줍니다."
    ],
    "조용히 읽히는 책": [
        "의미를 밀어붙이지 않는 문장들입니다.",
        "하루의 끝에 잘 어울립니다."
    ],
    "관점이 흔들리는 책": [
        "익숙한 생각을 다른 각도에서 보게 합니다.",
        "단정하지 않고 여백을 남깁니다."
    ],
    "마음이 정리되는 책": [
        "감정을 자극하기보다 가라앉힙니다.",
        "지금 상태를 그대로 받아들이게 합니다."
    ]
}

def pick_reason(mood, extra=""):
    today = datetime.date.today().isoformat()
    return pick_with_seed(REASONS[mood], today + mood + extra)

# ===============================
# UI
# ===============================
mood = st.radio(
    "오늘의 독서 기분",
    list(MOOD_KEYWORDS.keys())
)

# 상태 저장
if "retry" not in st.session_state:
    st.session_state.retry = 0

if st.button("오늘의 숨은 명저 찾기"):
    st.session_state.retry = 0

if st.button("🔁 다른 책 보기"):
    st.session_state.retry += 1

if st.session_state.retry >= 0:
    with st.spinner("알라딘 서가를 검색 중입니다…"):
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

    st.markdown("### 📖 책을 고른 이유")
    st.write(pick_reason(mood, str(st.session_state.retry)))

    with st.expander("📘 책 소개"):
        st.write(book["desc"])

    st.caption("※ 기본은 오늘의 책 고정 · 버튼 클릭 시 다른 후보")