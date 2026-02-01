import streamlit as st
import requests
import random
import datetime
import hashlib

# ===============================
# 🔐 알라딘 TTBKey 설정
# ===============================
# 로컬 테스트 시에는 아래 문자열에 직접 키를 넣거나, 
# 배포 시 .streamlit/secrets.toml 에 설정해주세요.
try:
    TTB_KEY = st.secrets["ALADIN_TTB_KEY"].strip().replace("\n", "")
except:
    # 예비용 (직접 입력 필요)
    TTB_KEY = "여기에_알라딘_TTB키를_입력하세요" 

# ===============================
# 페이지 설정
# ===============================
st.set_page_config(page_title="오늘의 숨은 명저", layout="centered")
st.title("📚 오늘의 숨은 명저")
st.caption("알라딘 서가 구석구석 · 깊이 있는 개인 독서 추천")

# ===============================
# 1. 기분 → 탐색 키워드 (Deep Dive 확장)
# ===============================
# 기존의 포괄적 단어(철학, 역사)를 구체적이고 마이너한 단어로 교체하여
# 베스트셀러가 아닌 '숨은 명작'이 걸릴 확률을 높입니다.
MOOD_PROFILE = {
    "생각이 깊어지는 책": {
        "intent": "본질과 사유 중심의 독서",
        "focus": "사고 실험, 존재론, 미학적 관점"
    },
    "조용히 읽히는 책": {
        "intent": "활자 밀도가 높은 침잠의 독서",
        "focus": "내면의 고요, 문장의 호흡, 서간(편지)"
    },
    "관점이 흔들리는 책": {
        "intent": "당연한 세계에 균열을 내는 독서",
        "focus": "문화인류학, 미시사, 비평, 구조적 통찰"
    },
    "마음이 정리되는 책": {
        "intent": "삶의 태도를 조율하는 독서",
        "focus": "단순한 삶, 걷기, 태도, 숲과 자연"
    }
}

MOOD_KEYWORDS = {
    "생각이 깊어지는 책": ["현상학", "지성", "미학", "사유", "고전", "인문학"],
    "조용히 읽히는 책": ["서간집", "산문", "고독", "정적", "문장", "시론"],
    "관점이 흔들리는 책": ["인류학", "미시사", "구조주의", "담론", "비평", "지정학"],
    "마음이 정리되는 책": ["명상", "단순함", "숲", "태도", "걷기", "성찰"]
}

# 상업적 서적 필터링을 위한 차단 단어
BLOCK_WORDS = ["성공", "부자", "재테크", "주식", "코인", "유튜브", "1억", "매매", "토익", "수험"]

# ===============================
# 2. 알라딘 API (페이징 기능 강화)
# ===============================
def search_aladin(keyword, page=1):
    url = "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTB_KEY,
        "Query": keyword,
        "QueryType": "Keyword",
        "MaxResults": 50, # 탐색 풀 확장 (30 -> 50)
        "start": page,    # 페이지 동적 할당
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }
    try:
        r = requests.get(url, params=params, timeout=7)
        r.raise_for_status()
        return r.json().get("item", [])
    except Exception as e:
        return []

def filter_books(items):
    results = []
    for b in items:
        title = b.get("title", "")
        desc = b.get("description", "")

        # 제목 필터링
        if any(w in title for w in BLOCK_WORDS):
            continue
        
        # 설명 길이 필터링 (너무 짧으면 제외)
        if len(desc) < 60:
            continue

        results.append({
            "title": title,
            "author": b.get("author", "").split(",")[0], # 첫 번째 저자만 표시
            "desc": desc,
            "link": b.get("link"),
            "cover": b.get("cover")
        })
    return results

# ===============================
# 3. 책 탐색 로직 (Serendipity Engine)
# ===============================
def pick_with_seed(items, seed):
    # 시드값을 숫자로 변환하여 랜덤성 고정
    seed_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    random.seed(seed_val)
    return random.choice(items)

def find_books(mood, retry_count):
    # 키워드 가져오기
    keywords = MOOD_KEYWORDS[mood][:]
    
    # 시드 생성: 날짜 + 기분 + (재시도 횟수 // 2)
    # 재시도를 누를 때마다 바로 키워드가 바뀌기보다, 
    # 같은 키워드 그룹 안에서 '더 깊은 페이지'를 탐색하도록 유도
    seed_val = f"{datetime.date.today()}{mood}{retry_count}"
    random.seed(seed_val)
    random.shuffle(keywords)

    for kw in keywords:
        # 핵심 로직: 재시도 횟수가 늘어날수록 더 깊은 페이지(구석진 서가)를 탐색
        # 예: 0번 시도 -> 1~2페이지, 3번 시도 -> 1~5페이지 랜덤
        max_page = 2 + (retry_count % 4) 
        target_page = random.randint(1, max_page) 
        
        raw_books = search_aladin(kw, page=target_page)
        books = filter_books(raw_books)
        
        # 필터링 후 남은 책이 너무 적으면, 다음 페이지까지 한 번 더 긁어옴
        if len(books) < 3:
            extra_books = search_aladin(kw, page=target_page + 1)
            books.extend(filter_books(extra_books))
            
        if books:
            return books
            
    return []

# ===============================
# 4. 선정 이유 생성 (맥락화)
# ===============================
def build_reason(book, mood):
    profile = MOOD_PROFILE[mood]
    
    return f"""
이 책은 **{profile['intent']}**를 원하시는 지금, 가장 적절한 선택지입니다.

소개된 내용을 보면 **{profile['focus']}**에 깊이 천착하고 있으며,  
단순한 정보의 나열보다는 독자가 스스로 맥락을 구성하게끔 돕습니다.

베스트셀러 순위나 유행하는 키워드보다는,  
**텍스트 그 자체의 밀도와 사유의 깊이**가 돋보이는 책입니다.
""".strip()

# ===============================
# 5. UI 구성
# ===============================
st.markdown("### 오늘은 어떤 문장이 필요하신가요?")
mood = st.radio(
    label="Mood Selector",
    options=list(MOOD_KEYWORDS.keys()),
    label_visibility="collapsed",
    horizontal=True
)

# 세션 상태 초기화
if "retry" not in st.session_state:
    st.session_state.retry = 0

# 버튼 영역
st.write("") # 간격
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔍 오늘의 숨은 명저 찾기", use_container_width=True):
        st.session_state.retry = 0 # 초기화 및 재검색
        
with col2:
    if st.button("🪐 더 깊은 서가로 이동 (다른 책)", use_container_width=True):
        st.session_state.retry += 1 # 깊이 증가

# 결과 출력
st.divider()

with st.spinner("서가의 먼지를 털어내고 숨겨진 책을 찾고 있습니다..."):
    books = find_books(mood, st.session_state.retry)

if not books:
    st.error("조건에 맞는 책을 찾지 못했습니다. 잠시 후 다시 시도하거나 다른 기분을 선택해주세요.")
    st.stop()

# 최종 책 선정
final_seed = f"{datetime.date.today()}{mood}{st.session_state.retry}"
book = pick_with_seed(books, final_seed)

# 책 정보 표시 UI
c1, c2 = st.columns([1, 3])

with c1:
    if book.get("cover"):
        st.image(book["cover"], use_container_width=True)
    else:
        st.markdown("📚")

with c2:
    st.markdown(f"### [{book['title']}]({book['link']})")
    st.caption(f"저자: {book['author']}")
    st.info(build_reason(book, mood))

with st.expander("📄 책 소개 미리보기", expanded=True):
    st.write(book["desc"])

st.markdown("---")
st.caption(f"Debug Info: Keyword Group '{mood}' | Depth Lv.{st.session_state.retry}")
