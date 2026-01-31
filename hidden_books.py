import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import re

# ===============================
# 기본 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저")

st.title("📚 오늘의 숨은 명저")
st.caption("베스트셀러는 아니지만, 읽을 이유가 분명한 한 권")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ===============================
# 검색 키워드 풀
# ===============================
SEARCH_KEYWORDS = [
    "인문학",
    "사유",
    "철학 에세이",
    "삶의 태도",
    "문장",
    "생각"
]

# ===============================
# 교보문고 검색
# ===============================
def search_kyobo(keyword):
    url = f"https://search.kyobobook.co.kr/search?keyword={keyword}"
    res = requests.get(url, headers=HEADERS, timeout=5)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

# ===============================
# 책 추출
# ===============================
def extract_books(soup):
    books = []
    items = soup.select("li.prod_item")

    for item in items[:20]:
        title = item.select_one("span.prod_name")
        desc = item.select_one("p.prod_introduction")
        review = item.select_one("span.review_klover_text")

        if not title:
            continue

        books.append({
            "title": title.get_text(strip=True),
            "desc": desc.get_text(strip=True) if desc else "",
            "reviews": review.get_text(strip=True) if review else ""
        })

    return books

# ===============================
# 필터
# ===============================
BLOCK_KEYWORDS = [
    "베스트셀러", "유튜브", "부자", "성공", "힐링"
]

def is_overexposed(book):
    text = book["title"] + book["desc"]
    return any(k in text for k in BLOCK_KEYWORDS)

# ===============================
# 점수
# ===============================
KEYWORDS_SCORE = ["사유", "문장", "태도", "관점", "생각"]

def score_book(book):
    score = 0
    for k in KEYWORDS_SCORE:
        if k in book["desc"]:
            score += 1

    nums = re.findall(r"\d+", book["reviews"])
    review_count = int(nums[0]) if nums else 0

    if review_count < 500:
        score += 1

    return score

# ===============================
# 숨은 명저 찾기 (절대 None 안 됨)
# ===============================
def find_hidden_book():
    keyword = random.choice(SEARCH_KEYWORDS)
    soup = search_kyobo(keyword)
    books = extract_books(soup)

    if not books:
        return None

    # 1단계: 필터 + 점수
    filtered = []
    for b in books:
        if not is_overexposed(b):
            b["score"] = score_book(b)
            filtered.append(b)

    # 2단계: 점수 기준 상위
    if filtered:
        filtered.sort(key=lambda x: x["score"], reverse=True)
        return random.choice(filtered[:5])

    # 3단계: 필터 실패 시 전체 중 랜덤
    return random.choice(books)

# ===============================
# 설명 문구
# ===============================
def make_reason():
    return (
        "이 책은 크게 주목받지는 않았지만,\n"
        "삶을 다루는 문장이 조용히 이어집니다.\n\n"
        "답을 주기보다,\n"
        "생각이 머무는 시간을 허락하는 책입니다."
    )

# ===============================
# UI
# ===============================
if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("조용히 책장을 넘기는 중..."):
        try:
            book = find_hidden_book()
        except Exception:
            st.error("검색 중 문제가 발생했습니다.")
            st.stop()

    st.divider()

    if book:
        st.subheader(book["title"])
        st.write(make_reason())
        st.caption("※ 교보문고 검색 결과 기반 자동 추천")
    else:
        st.write("오늘은 조용히 쉬어가는 날입니다.")