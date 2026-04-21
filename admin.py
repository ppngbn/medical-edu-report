import streamlit as st
import pandas as pd

# --- 관리자 페이지 설정 ---
st.set_page_config(page_title="관리자 전용 결산 시스템", layout="wide")

st.title("🔐 교육 결과 관리자 시스템")
st.sidebar.title("관리 메뉴")

# 현재는 데이터베이스 연결 전이라 예시 리스트만 보여줍니다.
st.subheader("📊 실시간 제출 현황 리스트")

# 임시 데이터 (나중에 구글 시트 연동 시 자동으로 채워집니다)
st.info("데이터베이스(구글 시트)를 연결하면 여기에 실시간 리스트가 나타납니다.")

# 예시 테이블 구조
data = {
    "제출일시": ["2026-04-21 10:05", "2026-04-21 11:20"],
    "기관분류": ["종합병원", "의원"],
    "기관명": ["한국병원", "서울내과"],
    "담당자": ["홍길동", "김철수"],
    "이메일": ["hong@mail.com", "kim@mail.com"],
    "파일": ["report_01.xlsx", "report_02.xlsx"]
}
df = pd.DataFrame(data)
st.table(df)

st.divider()

st.subheader("📥 전체 데이터 다운로드")
col1, col2 = st.columns(2)
with col1:
    if st.button("전체 제출 명단 다운로드 (CSV)"):
        st.write("준비 중...")
with col2:
    if st.button("모든 첨부파일 압축 다운로드"):
        st.write("준비 중...")
