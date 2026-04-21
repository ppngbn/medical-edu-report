import streamlit as st
import pandas as pd
from github import Github # 깃허브 조작용 도구
import base64

# --- 깃허브 설정 (보안을 위해 나중에 Streamlit Secrets에 넣는게 좋아요) ---
GITHUB_TOKEN = "11B37IKZY0GVbCp9gUFDCk_BoqViwL3dLTMJuUl6ZggMiZgvBMrsq4RJl2OsigSkjMD6EDHVHIyNxVgUL2"
REPO_NAME = "ppngbn/medical-edu-report"

def upload_to_github(file_name, file_content, hospital_name):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # 저장될 경로: data/기관명_시간.xlsx
    path = f"data/{hospital_name}_{file_name}"
    
    # 깃허브에 파일 생성
    repo.create_file(path, f"Upload from {hospital_name}", file_content)

st.title("🏥 교육 결과보고 제출처")

with st.form("my_form"):
    inst_name = st.text_input("의료기관명")
    uploaded_file = st.file_uploader("엑셀 파일 선택", type=["xlsx"])
    submit = st.form_submit_button("제출")

if submit and uploaded_file and inst_name:
    # 파일을 읽어서 깃허브로 전송
    file_bytes = uploaded_file.getvalue()
    upload_to_github(uploaded_file.name, file_bytes, inst_name)
    st.success("파일이 성공적으로 서버에 저장되었습니다!")
