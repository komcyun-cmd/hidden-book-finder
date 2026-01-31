import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# ===============================
# 기본 설정
# ===============================
st.set_page_config(
    page_title="숨은 명저",
    layout="centered"
)

st.title("📚 오늘의 숨은 명저")
st.caption("베스트셀러가 아닌, 읽을 이유가 분명한 한 권")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ===============================
# 교보문고 검색
# ===============================
def search_kyobo(keyword: str):
    url = f"https://search.kyobobook.co.kr/search?keyword={keyword}"
    res = requests.get(url, headers=HEADERS, timeout=5)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

# ===============================
# 검색 결과에서 책 추출
# ===============================
def extract_books(soup):
    books = []

    items = soup.select("li.prod_item")
    for item in items[:10]:  # 상위 10개만 사용
        title_tag = item.select_one("span.prod_name")
        desc_tag = item.select_one("p.prod_introduction")
        review_tag = item.select_one("span.review_klover_text")

        title = title_tag.get_text(strip=True) if title_tag else ""
        desc = desc_tag.get_text(strip=True) if desc_tag else ""
        reviews = review_tag.get_text(strip=True) if review_tag else ""

        books.append({
            "title": title,
            "desc": desc,
            "reviews": reviews
        })

    return books

# ===============================
# 과다 노출 필터
# ===============================
BLOCK_KEYWORDS = [
    "베스트셀러", "힐링", "성공",
    "유튜브", "tv", "추천",
    "에세이스트", "셀럽"
]

def is_overexposed(book):
    text = book["title"] + book["desc"]
    return any(kw in text for kw in BLOCK_KEYWORDS)

# ===============================
# 리뷰 수 파싱
# ===============================
def parse_review_count(text):
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else 0

# ===============================
# 숨은 명저 점수 계산
# ===============================
DENSITY_KEYWORDS = {
    "사유": 2,
    "문장": 2,
    "태도": 1,
    "관점": 1,
    "일상": 1,
    "침묵": 1
}

def score_book(book):
    score = 0

    for k, v in DENSITY_KEYWORDS.items():
        if k in book["desc"]:
            score += v

    review_count = parse_review_count(book["reviews"])
    if review_count < 500:
        score += 1

    return score

# ===============================
# 최종 1권 선택 (항상 반환)
# ===============================
def find_hidden_book():
    soup = search_kyobo("인문학 사유")
    books = extract_books(soup)

    if not books:
        return None

    scored = []
    for b in books:
        b["score"] = score_book(b)
        if not is_overexposed(b):
            scored.append(b)

    # 1차: 필터 통과자 중 최고점
    if scored:
        return sorted(scored, key=lambda x: x["score"], reverse=True)[0]

    # 2차: 필터 무시하고 최고점
    return sorted(books, key=lambda x: x["score"], reverse=True)[0]

# ===============================
# 설명 문구 생성
# ===============================
def make_reason(book):
    return f"""
이 책은 크게 주목받지 않았지만,
삶을 다루는 문장이 비교적 조용하게 이어진다.

요즘 책들이 해답이나 메시지를 전면에 내세울 때,
이 책은 생각이 머무는 시간을 허용한다.

읽고 나면 무엇을 얻었다기보다,
하루를 대하는 태도가 조금 달라진다.
"""

# ===============================
# UI
# ===============================
if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("조용히 찾는 중..."):
        try:
            book = find_hidden_book()
        except Exception:
            st.error("검색 중 문제가 발생했습니다.")
            st.stop()

    if book:
        st.subheader(book["title"])
        st.write(make_reason(book))
        st.caption("※ 교보문고 검색 결과를 기반으로 자동 선별되었습니다.")
    else:
        st.write("오늘은 조건에 가장 가까운 한 권을 골랐습니다.")