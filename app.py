import streamlit as st
from github import Github
from datetime import datetime

# --- 설정 (Secrets 사용) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

def upload_to_github(file_bytes, inst_type, inst_name, phone, email, original_name):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 💡 파일명에 모든 메타데이터를 포함 (구분자 '^' 사용으로 안전하게 분리)
    path = f"data/{now}^{inst_type}^{inst_name}^{phone}^{email}^{original_name}"
    repo.create_file(path, f"Upload: {inst_name}", file_bytes)

# --- UI ---
st.set_page_config(page_title="교육 결과 제출", page_icon="🏥")
st.title("🏥 2026년 신고의무자 교육 결과 제출")

with st.form("submit_form"):
    st.subheader("📝 기관 및 담당자 정보")
    inst_type = st.selectbox("기관 분류", ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"])
    inst_name = st.text_input("의료기관 명칭", placeholder="예: 한국병원")
    
    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("담당자 연락처", placeholder="예: 010-0000-0000")
    with col2:
        email = st.text_input("담당자 이메일", placeholder="example@mail.com")
    
    st.subheader("📂 파일 업로드")
    file = st.file_uploader("결과보고서(엑셀) 업로드", type=["xlsx"])
    submitted = st.form_submit_button("제출하기")

if submitted:
    if inst_name and phone and file:
        with st.spinner("제출 중..."):
            upload_to_github(file.getvalue(), inst_type, inst_name, phone, email, file.name)
            st.success("✅ 제출이 완료되었습니다!")
            st.balloons()
    else:
        st.error("⚠️ 모든 필수 정보를 입력하고 파일을 올려주세요.")
