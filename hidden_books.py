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
st.caption("조용히 남아 있는 책 한 권")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ===============================
# 검색 키워드 풀 (랜덤)
# ===============================
SEARCH_KEYWORDS = [
    "인문학",
    "사유",
    "철학 에세이",
    "삶의 태도",
    "문장",
    "생각",
    "일상 철학"
]

# ===============================
# 교보문고 검색
# ===============================
def search_kyobo(keyword: str):
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

    for item in items[:15]:
        title_tag = item.select_one("span.prod_name")
        desc_tag = item.select_one("p.prod_introduction")
        review_tag = item.select_one("span.review_klover_text")

        if not title_tag:
            continue

        books.append({
            "title": title_tag.get_text(strip=True),
            "desc": desc_tag.get_text(strip=True) if desc_tag else "",
            "reviews": review_tag.get_text(strip=True) if review_tag else ""
        })

    return books

# ===============================
# 과다 노출 필터
# ===============================
BLOCK_KEYWORDS = [
    "베스트셀러", "유튜브", "tv", "셀럽",
    "성공", "부자", "힐링"
]

def is_overexposed(book):
    text = book["title"] + book["desc"]
    return any(k in text for k in BLOCK_KEYWORDS)

# ===============================
# 리뷰 수
# ===============================
def parse_review_count(text):
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else 0

# ===============================
# 점수
# ===============================
KEYWORDS_SCORE = ["사유", "문장", "태도", "관점", "생각"]

def score_book(book):
    score = 0
    for k in KEYWORDS_SCORE:
        if k in book["desc"]:
            score += 1

    if parse_review_count(book["reviews"]) < 500:
        score += 1

    return score

# ===============================
# 숨은 명저 찾기 (랜덤성 포함)
# ===============================
def find_hidden_book():
    keyword = random.choice(SEARCH_KEYWORDS)
    soup = search_kyobo(keyword)
    books = extract_books(soup)

    if not books:
        return None

    scored = []
    for b in books:
        if not is_overexposed(b):
            b["score"] = score_book(b)
            scored.append(b)

    if not scored:
        scored = books

    scored = sorted(scored, key=lambda x: x.get("score", 0), reverse=True)

    top_candidates = scored[:5] if len(scored) >= 5 else scored
    return random.choice(top_candidates)

# ===============================
# 설명 문구
# ===============================
def make_reason():
    return (
        "이 책은 크게 주목받지는 않았지만,\n"
        "생각을 서두르지 않는 문장으로 이루어져 있습니다.\n\n"
        "요즘 책들이 답을 제시하려 할 때,\n"
        "이 책은 질문이 머무를 자리를 남깁니다."
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
        # 🔥 제목: Streamlit 기본 컴포넌트 (안 안 보임)
        st.subheader(book["title"])
        st.write(make_reason())
        st.caption("※ 교보문고 검색 결과 기반")
    else:
        st.write("오늘은 고를 수 있는 책이 없었습니다.")