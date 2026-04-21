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
    
    # 💡 데이터 구분을 위해 '^' 기호를 사용합니다. (파일명 규칙 설정)
    # [시간]^[분류]^[기관명]^[연락처]^[이메일]^[파일명]
    safe_file_name = original_name.replace("^", "_") # 파일명에 ^가 있으면 에러 방지
    path = f"data/{now}^{inst_type}^{inst_name}^{phone}^{email}^{safe_file_name}"
    
    repo.create_file(path, f"제출: {inst_name}", file_bytes)

# --- UI 구성 ---
st.set_page_config(page_title="신고의무자 교육 제출", layout="centered")
st.title("🏥 2026년 신고의무자 교육 결과 보고")

with st.form("upload_form"):
    st.subheader("📝 기관 및 담당자 정보 입력")
    inst_type = st.selectbox("기관 분류", ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"])
    inst_name = st.text_input("의료기관 명칭", placeholder="정확한 명칭을 입력하세요")
    
    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("담당자 연락처", placeholder="010-0000-0000")
    with col2:
        email = st.text_input("담당자 이메일", placeholder="example@mail.com")
        
    st.subheader("📂 결과보고서 업로드")
    file = st.file_uploader("엑셀 파일(.xlsx) 선택", type=["xlsx"])
    
    submitted = st.form_submit_button("제출하기")

if submitted:
    if inst_name and phone and file:
        with st.spinner("서버에 저장 중입니다..."):
            try:
                upload_to_github(file.getvalue(), inst_type, inst_name, phone, email, file.name)
                st.success(f"✅ {inst_name}님, 제출이 완료되었습니다.")
                st.balloons()
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("⚠️ 모든 빈칸을 채우고 파일을 업로드해 주세요.")
