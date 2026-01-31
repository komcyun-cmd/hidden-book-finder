import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저")

st.title("📚 오늘의 숨은 명저")
st.caption("알라딘 검색 결과 중, 조용히 남아 있는 책 한 권")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# ===============================
# 검색 키워드 풀
# ===============================
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

BLOCK_WORDS = [
    "베스트셀러",
    "성공",
    "부자",
    "유튜브",
    "재테크",
    "주식"
]

# ===============================
# 알라딘 검색
# ===============================
def search_aladin(keyword):
    url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={keyword}"
    res = requests.get(url, headers=HEADERS, timeout=7)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

def extract_books(soup):
    books = []
    items = soup.select("div.ss_book_box")

    for item in items:
        title_tag = item.select_one("a.bo3")
        desc_tag = item.select_one("span.ss_p2")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        desc = desc_tag.get_text(strip=True) if desc_tag else ""

        if any(word in title for word in BLOCK_WORDS):
            continue

        books.append({
            "title": title,
            "desc": desc
        })

    return books

# ===============================
# 반드시 검색 결과 반환
# ===============================
def find_book_guaranteed():
    random.shuffle(SEARCH_KEYWORDS)

    for keyword in SEARCH_KEYWORDS:
        try:
            soup = search_aladin(keyword)
            books = extract_books(soup)

            if books:
                return random.choice(books)

            time.sleep(0.4)

        except Exception:
            continue

    # 여기까지 오면 진짜 네트워크 문제
    raise RuntimeError("알라딘 검색 실패")

# ===============================
# UI
# ===============================
if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("알라딘 서가를 조용히 훑는 중..."):
        try:
            book = find_book_guaranteed()
        except Exception:
            st.error("알라딘 검색에 실패했습니다. 잠시 후 다시 시도해주세요.")
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
        "이 책은 검색 결과 상단에 자주 보이지 않지만,\n"
        "주제와 문장이 분명해 천천히 읽을 가치가 있습니다.\n\n"
        "요즘 같은 때에는 이런 책이 오히려 오래 남습니다."
    )

    st.caption("※ 알라딘 실시간 검색 결과 기반")