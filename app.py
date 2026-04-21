import streamlit as st
import pandas as pd
from github import Github
from datetime import datetime

# --- 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"] 
REPO_NAME = st.secrets["REPO_NAME"]

def upload_to_github(file_bytes, hospital_name, original_name):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # 파일명 중복 방지를 위해 현재 시간 추가
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"data/{now}_{hospital_name}_{original_name}"
    
    # 깃허브 업로드
    repo.create_file(path, f"Upload: {hospital_name}", file_bytes)

# --- 화면 구성 ---
st.set_page_config(page_title="교육 결과 제출", page_icon="🏥")
st.title("🏥 2026년 신고의무자 교육 결과 제출")

with st.form("submit_form"):
    st.subheader("📝 기관 정보")
    inst_type = st.selectbox("기관 분류", ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"])
    inst_name = st.text_input("의료기관 명칭")
    email = st.text_input("담당자 이메일")
    
    st.subheader("📂 파일 업로드")
    file = st.file_uploader("결과보고서(엑셀)를 올려주세요", type=["xlsx"])
    
    submitted = st.form_submit_button("제출하기")

if submitted:
    if inst_name and file:
        with st.spinner("제출 중... 잠시만 기다려 주세요."):
            upload_to_github(file.getvalue(), inst_name, file.name)
            st.success(f"✅ {inst_name}님, 제출이 완료되었습니다!")
            st.balloons()
    else:
        st.error("기관명과 파일을 확인해 주세요.")
