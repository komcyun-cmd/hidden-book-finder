import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time

st.set_page_config(page_title="오늘의 숨은 명저")

st.title("📚 오늘의 숨은 명저")
st.caption("교보문고 검색 결과 중, 조용히 남아 있는 책 한 권")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

SEARCH_KEYWORDS = [
    "인문학",
    "철학",
    "에세이",
    "사유",
    "문장",
    "삶",
    "생각",
    "고전",
    "사회",
    "역사"
]

BLOCK_WORDS = ["베스트셀러", "유튜브", "성공", "부자"]

# -----------------------------
# 교보 검색
# -----------------------------
def search_kyobo(keyword):
    url = f"https://search.kyobobook.co.kr/search?keyword={keyword}"
    r = requests.get(url, headers=HEADERS, timeout=7)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def extract_books(soup):
    books = []

    # 교보가 자주 쓰는 두 가지 구조 모두 시도
    items = soup.select("li.prod_item")
    if not items:
        items = soup.select("div.prod_area")

    for item in items:
        title = item.select_one(".prod_name")
        desc = item.select_one(".prod_introduction")

        if not title:
            continue

        title_text = title.get_text(strip=True)
        desc_text = desc.get_text(strip=True) if desc else ""

        # 너무 노골적인 베스트셀러 제거
        if any(w in title_text for w in BLOCK_WORDS):
            continue

        books.append({
            "title": title_text,
            "desc": desc_text
        })

    return books

# -----------------------------
# 반드시 책 하나 반환
# -----------------------------
def find_book_guaranteed():
    random.shuffle(SEARCH_KEYWORDS)

    for keyword in SEARCH_KEYWORDS:
        try:
            soup = search_kyobo(keyword)
            books = extract_books(soup)

            if books:
                return random.choice(books)

            time.sleep(0.5)  # 너무 빠른 요청 방지

        except Exception:
            continue

    # 여기까지 오면 "교보 자체 접근 실패"
    raise RuntimeError("교보문고 검색 실패")

# -----------------------------
# UI
# -----------------------------
if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("교보문고 서가를 뒤지는 중..."):
        try:
            book = find_book_guaranteed()
        except Exception:
            st.error("교보문고 검색에 실패했습니다. 네트워크를 확인해주세요.")
            st.stop()

    st.divider()

    st.markdown(
        f"""
        <h2 style="color:white; margin-bottom:1rem;">
        {book["title"]}
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "이 책은 검색 결과 상위에 자주 등장하지 않지만,\n"
        "주제와 문장이 분명해 끝까지 읽을 이유가 있습니다.\n\n"
        "지금 읽기엔 오히려 이런 책이 더 적당합니다."
    )

    st.caption("※ 교보문고 실시간 검색 결과 기반")