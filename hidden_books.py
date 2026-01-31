import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time
import datetime
import hashlib
from urllib.parse import quote

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저")

st.title("📚 오늘의 숨은 명저")
st.caption("알라딘 검색 결과 중, 오늘의 나에게 맞는 조용한 한 권")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# ===============================
# 독서 기분 → 키워드
# ===============================
MOOD_KEYWORDS = {
    "생각이 깊어지는 책": ["철학", "사유", "존재"],
    "조용히 읽히는 책": ["에세이", "문장", "일상"],
    "관점이 흔들리는 책": ["사회", "역사", "비판"],
    "마음이 정리되는 책": ["삶", "태도", "고독"]
}

BLOCK_WORDS = [
    "베스트셀러", "성공", "부자", "유튜브", "재테크", "주식"
]

# ===============================
# 알라딘 검색
# ===============================
def search_aladin(keyword):
    url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={quote(keyword)}"
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

        if any(w in title for w in BLOCK_WORDS):
            continue

        if len(desc) < 30:
            continue

        books.append({
            "title": title,
            "desc": desc,
            "link": "https://www.aladin.co.kr" + title_tag["href"]
        })

    return books

# ===============================
# 날짜 고정용 랜덤
# ===============================
def daily_random_choice(items):
    today = datetime.date.today().isoformat()
    seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
    random.seed(seed)
    return random.choice(items)

# ===============================
# 반드시 검색
# ===============================
def find_book_by_mood(mood):
    keywords = MOOD_KEYWORDS.get(mood, [])
    random.shuffle(keywords)

    for keyword in keywords:
        try:
            soup = search_aladin(keyword)
            books = extract_books(soup)

            if books:
                return daily_random_choice(books)

            time.sleep(0.4)

        except Exception:
            continue

    raise RuntimeError("알라딘 검색 실패")

# ===============================
# 하루마다 달라지는 선정 이유
# ===============================
REASON_POOL = {
    "생각이 깊어지는 책": [
        "답을 주기보다 질문을 남기는 방식으로 전개됩니다.",
        "사고의 속도를 늦추며 한 문장씩 생각하게 만듭니다.",
        "논리를 설득하기보다 사유를 유도하는 책입니다."
    ],
    "조용히 읽히는 책": [
        "문장이 앞서지 않고 생각이 자연스럽게 이어집니다.",
        "의미를 밀어붙이지 않아 편안하게 읽힙니다.",
        "하루의 끝에 읽기 좋은 호흡을 가지고 있습니다."
    ],
    "관점이 흔들리는 책": [
        "익숙한 전제를 다시 보게 만드는 힘이 있습니다.",
        "한 방향의 해석에 머물지 않게 만듭니다.",
        "생각의 좌표를 살짝 이동시키는 책입니다."
    ],
    "마음이 정리되는 책": [
        "속도를 낮추고 생각을 정돈하게 합니다.",
        "감정을 자극하기보다 차분히 가라앉힙니다.",
        "지금의 상태를 있는 그대로 받아들이게 돕습니다."
    ]
}

def make_daily_reason(mood):
    reasons = REASON_POOL.get(mood, [])
    if not reasons:
        return "지금의 상태에 무리 없이 스며드는 책입니다."

    today = datetime.date.today().isoformat()
    seed = int(hashlib.md5((today + mood).encode()).hexdigest(), 16)
    random.seed(seed)
    return random.choice(reasons)

# ===============================
# UI
# ===============================
st.subheader("오늘은 어떤 책이 필요하신가요?")

selected_mood = st.radio(
    "독서 기분 선택",
    options=list(MOOD_KEYWORDS.keys()),
    label_visibility="collapsed"
)

if st.button("오늘의 숨은 명저 찾기"):
    with st.spinner("알라딘 서가를 조용히 훑는 중..."):
        try:
            book = find_book_by_mood(selected_mood)
        except Exception:
            st.error("알라딘 검색에 실패했습니다. 잠시 후 다시 시도해주세요.")
            st.stop()

    st.divider()

    # 제목 + 링크
    st.markdown(
        f"""
        <h2 style="margin-bottom:0.5rem;">
        <a href="{book['link']}" target="_blank" style="color:white; text-decoration:none;">
        {book['title']}
        </a>
        </h2>
        """,
        unsafe_allow_html=True
    )

    # 선정 이유
    st.markdown("### 📖 책 선정 이유")
    st.write(make_daily_reason(selected_mood))

    # 책 소개 (접기/펼치기)
    with st.expander("📘 책 소개 펼쳐보기"):
        st.write(book["desc"])

    st.caption("※ 알라딘 실시간 검색 결과 기반 · 하루 1회 고정 추천")