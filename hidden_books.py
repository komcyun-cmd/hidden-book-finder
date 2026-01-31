import streamlit as st
import requests
from bs4 import BeautifulSoup

# -------------------------------
# 기본 설정
# -------------------------------
st.set_page_config(
    page_title="숨은 명저",
    layout="centered"
)

st.title("📚 오늘의 숨은 명저")
st.caption("베스트셀러가 아닌, 읽을 이유가 분명한 한 권")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------------------
# 1. 교보문고 검색
# -------------------------------
def search_kyobo(keyword: str):
    url = f"https://search.kyobobook.co.kr/search?keyword={keyword}"
    res = requests.get(url, headers=HEADERS, timeout=5)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

# -------------------------------
# 2. 검색 결과에서 책 추출
# -------------------------------
def extract_books(soup):
    books = []

    items = soup.select("li.prod_item")
    for item in items[:10]:  # 상위 10개만
        title_tag = item.select_one("span.prod_name")
        desc_tag = item.select_one("p.prod_introduction")
        review_tag = item.select_one("span.review_klover_text")

        title = title_tag.get_text(strip=True) if title_tag else ""
        desc = desc_tag.get_text(strip=True) if desc_tag else ""
        reviews = review_tag.get_text(strip=True) if review_tag else "0"

        books.append({
            "title": title,
            "desc": desc,
            "reviews": reviews
        })

    return books

# -------------------------------
# 3. 과다 노출 필터
# -------------------------------
BLOCK_KEYWORDS = [
    "베스트셀러", "힐링", "성공",
    "유튜브", "tv", "추천",
    "에세이스트", "셀럽"
]

def is_overexposed(book):
    text = book["title"] + book["desc"]
    return any(kw in text for kw in BLOCK_KEYWORDS)

# -------------------------------
# 4. 숨은 명저 점수 계산
# -------------------------------
DENSITY_KEYWORDS = {
    "사유": 3,
    "문장": 3,
    "태도": 2,
    "관점": 2,
    "일상": 1,
    "침묵": 1
}

def score_book(book):
    score = 0

    for k, v in DENSITY_KEYWORDS.items():
        if k in book["desc"]:
            score += v

    try:
        review_count = int(book["reviews"])
        if review_count < 300:
            score += 2
    except:
        pass

    return score

# -------------------------------
# 5. 최종 1권 선택
# -------------------------------
def find_hidden_book():
    soup = search_kyobo("인문학 사유")
    books = extract_books(soup)

    candidates = []
    for b in books:
        if not is_overexposed(b):
            b["score"] = score_book(b)
            if b["score"] >= 5:
                candidates.append(b)

    if not candidates:
        return None

    return sorted(candidates, key=lambda x: x["score"], reverse=True)[0]

# -------------------------------
# 6. 설명 문구 생성
# -------------------------------
def make_reason(book):
    return f"""
이 책은 크게 알려지지 않았지만,
삶을 다루는 문장이 비교적 절제되어 있다.

요즘 책들이 해답이나 메시지를 전면에 내세울 때,
이 책은 생각이 머무는 지점을 남긴다.

읽고 나면 무엇을 알게 되기보다는,
하루를 대하는 태도가 조용히 남는다.
"""

# -------------------------------
# 7. UI
# -------------------------------
if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("조용히 찾는 중..."):
        try:
            book = find_hidden_book()
        except Exception as e:
            st.error("검색 중 문제가 발생했습니다.")
            st.stop()

    if book:
        st.subheader(book["title"])
        st.write(make_reason(book))
        st.caption("※ 교보문고 검색 결과를 기반으로 자동 선별되었습니다.")
    else:
        st.write("오늘은 조용히 남아 있는 책을 찾지 못했습니다.")