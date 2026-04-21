import streamlit as st
from github import Github
from datetime import datetime
import pytz # 시간대 설정용

# --- 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

def upload_to_github(file_bytes, inst_type, inst_name, phone, email, original_name):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # 💡 서울 시간으로 파일명 생성
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).strftime("%Y%m%d_%H%M%S")
    
    safe_file_name = original_name.replace("^", "_")
    path = f"data/{now}^{inst_type}^{inst_name}^{phone}^{email}^{safe_file_name}"
    
    repo.create_file(path, f"제출: {inst_name}", file_bytes)

# --- UI ---
st.set_page_config(page_title="신고의무자 교육 제출", layout="centered")
st.title("🏥 2026년 신고의무자 교육 결과 보고")

with st.form("upload_form"):
    st.subheader("📝 기관 및 담당자 정보 입력")
    inst_type = st.selectbox("기관 분류", ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"])
    inst_name = st.text_input("의료기관 명칭")
    
    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("담당자 연락처")
    with col2:
        email = st.text_input("담당자 이메일")
        
    file = st.file_uploader("결과보고서 업로드", type=["xlsx"])
    submitted = st.form_submit_button("제출하기")

if submitted:
    if inst_name and phone and file:
        with st.spinner("제출 중..."):
            upload_to_github(file.getvalue(), inst_type, inst_name, phone, email, file.name)
            st.success("✅ 제출이 완료되었습니다.")
            st.balloons()
