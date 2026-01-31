import streamlit as st

st.set_page_config(page_title="숨은 명저", layout="centered")

st.title("📚 오늘의 숨은 명저")
st.caption("조용히 남아 있는 한 권을 찾습니다.")

def find_hidden_book():
    # 👉 이후 여기에 교보/도서관 검색 로직이 들어갈 자리
    return {
        "title": "보통 사람들의 철학",
        "reason": """
이 책은 크게 알려지지 않았지만,
삶을 다루는 문장이 매우 절제되어 있다.

요즘 책들이 해답을 말할 때,
이 책은 질문에 머문다.

읽고 나면 정보를 얻기보다는
하루를 대하는 태도가 남는다.
"""
    }

if st.button("오늘의 책 찾기"):
    book = find_hidden_book()
    st.subheader(book["title"])
    st.write(book["reason"])