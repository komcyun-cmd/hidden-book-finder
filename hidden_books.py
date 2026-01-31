import streamlit as st
import requests
import random
import datetime
import hashlib

# ===============================
# 🔑 알라딘 TTBKey
# ===============================
TTB_KEY = "YOUR_TTB_KEY_HERE"

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저")
st.title("📚 오늘의 숨은 명저")
st.caption("알라딘 공식 API 기반 · 반드시 검색되는 추천")

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
# 알라딘 API 검색
# ===============================
def search_aladin_api(keyword):
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
# 날짜 고정 랜덤
# ===============================
def daily_pick(items, seed_key):
    seed = int(hashlib.md5(seed_key.encode()).hexdigest(), 16)
    random.seed(seed)
    return random.choice(items)

# ===============================
# 책 찾기 (반드시 API)
# ===============================
def find_book(mood):
    keywords = MOOD_KEYWORDS[mood]
    random.shuffle(keywords)

    for kw in keywords:
        items = search_aladin_api(kw)
        books = filter_books(items)

        if books:
            today = datetime.date.today().isoformat()
            return daily_pick(books, today + mood)

    raise RuntimeError("검색 실패")

# ===============================
# 선정 이유
# ===============================
REASONS = {
    "생각이 깊어지는 책": [
        "답보다 질문을 오래 남기는 책입니다.",
        "사고의 속도를 늦추며 읽히는 구조입니다."
    ],
    "조용히 읽히는 책": [
        "문장이 과하지 않아 하루의 끝에 어울립니다.",
        "의미를 밀어붙이지 않아 편안합니다."
    ],
    "관점이 흔들리는 책": [
        "익숙한 생각을 다른 각도에서 보게 만듭니다.",
        "한 방향으로 단정하지 않습니다."
    ],
    "마음이 정리되는 책": [
        "감정을 자극하기보다 가라앉힙니다.",
        "지금 상태를 그대로 받아들이게 합니다."
    ]
}

def pick_reason(mood):
    today = datetime.date.today().isoformat()
    return daily_pick(REASONS[mood], today + mood + "reason")

# ===============================
# UI
# ===============================
st.subheader("오늘의 독서 기분")

mood = st.radio(
    "기분 선택",
    list(MOOD_KEYWORDS.keys()),
    label_visibility="collapsed"
)

if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("알라딘 서가를 검색 중입니다…"):
        try:
            book = find_book(mood)
        except Exception:
            st.error("알라딘 검색에 실패했습니다. TTBKey를 확인해주세요.")
            st.stop()

    st.divider()

    st.markdown(
        f"<h2><a href='{book['link']}' target='_blank'>{book['title']}</a></h2>",
        unsafe_allow_html=True
    )

    st.markdown("### 📖 책 선정 이유")
    st.write(pick_reason(mood))

    with st.expander("📘 책 소개"):
        st.write(book["desc"])

    st.caption("※ 알라딘 공식 Open API 기반 · 하루 1회 고정 추천")