import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="의료기관 교육 결과 보고 시스템", layout="wide")

# 사이드바 메뉴 구성
menu = st.sidebar.selectbox("메뉴 선택", ["기관용: 결과보고 제출", "관리자용: 데이터 결산"])

# --- [메뉴 1: 기관용 제출 페이지] ---
if menu == "기관용: 결과보고 제출":
    st.title("🏥 2026년 신고의무자 교육 결과보고서 제출")
    st.info("각 의료기관 담당자께서는 정보를 입력하고 엑셀 파일을 업로드해 주세요.")

    with st.form("upload_form"):
        st.subheader("📝 기관 정보 입력")
        col1, col2 = st.columns(2)
        with col1:
            inst_type = st.selectbox("기관 분류", ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"])
            inst_name = st.text_input("의료기관명", placeholder="정확한 명칭을 입력하세요")
        with col2:
            email = st.text_input("담당자 이메일")
            phone = st.text_input("담당자 연락처 (핸드폰)")
        
        st.subheader("📂 파일 업로드")
        uploaded_file = st.file_uploader("결과보고서 엑셀파일(.xlsx)", type=["xlsx"])
        
        submit = st.form_submit_button("제출하기")

    if submit:
        if inst_name and uploaded_file:
            # 💡 실제 운영 시 여기에 구글 시트 저장 로직이 들어갑니다.
            st.success(f"✅ {inst_name}의 보고서가 성공적으로 제출되었습니다!")
            st.balloons()
        else:
            st.error("기관명과 파일을 확인해 주세요.")

# --- [메뉴 2: 관리자용 결산 페이지] ---
elif menu == "관리자용: 데이터 결산":
    st.title("🔐 관리자 전용 결산 시스템")
    
    # 간단한 비밀번호 확인 (실제 업무용으로 쓰시려면 필요해요!)
    password = st.text_input("관리자 암호를 입력하세요", type="password")
    
    if password == "1234": # ⬅️ 원하시는 비밀번호로 바꾸세요!
        st.success("인증되었습니다.")
        
        st.subheader("📊 전체 기관 제출 현황")
        # 임시 데이터 예시 (나중에 구글 시트와 연결되면 자동으로 바뀝니다)
        st.info("현재 구글 시트와 연결되지 않아 실시간 데이터가 표시되지 않습니다.")
        
        # 가상의 리스트 보여주기 (예시)
        example_data = pd.DataFrame({
            "제출시간": ["2026-04-21 10:00", "2026-04-21 11:30"],
            "기관분류": ["종합병원", "의원"],
            "기관명": ["한국병원", "서울내과"],
            "담당자": ["홍길동", "김철수"],
            "파일링크": ["다운로드", "다운로드"]
        })
        st.table(example_data)
        
        # 결산 버튼
        if st.button("전체 데이터 엑셀로 내려받기"):
            st.write("모든 기관의 데이터를 하나로 합친 파일을 생성합니다...")
            # 여기에 집계 로직 추가 예정
            
    elif password != "":
        st.error("비밀번호가 틀렸습니다.")
