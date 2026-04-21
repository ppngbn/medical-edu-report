import streamlit as st
from github import Github
from datetime import datetime
import pytz

# --- 1. 설정 (Streamlit Secrets 사용) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

# 깃허브 업로드 함수
def upload_to_github(file_bytes, inst_type, inst_name, phone, email, original_name):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # 대한민국 서울 시간대 설정
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).strftime("%Y%m%d_%H%M%S")
    
    # 파일명 생성 (구분자 '^' 사용, 파일명 내 '^'는 '_'로 치환)
    safe_name = original_name.replace("^", "_")
    path = f"data/{now}^{inst_type}^{inst_name}^{phone}^{email}^{safe_name}"
    
    repo.create_file(path, f"제출: {inst_name}", file_bytes)

# --- 2. UI 구성 ---
st.set_page_config(page_title="신고의무자 교육 결과 제출", layout="centered")
st.title("🏥 2026년 신고의무자 교육 결과 보고")
st.info("기관 및 담당자 정보를 입력하신 후 결과보고서(엑셀)를 업로드해 주세요.")

with st.form("upload_form"):
    st.subheader("📝 정보 입력")
    
    # 기관 분류 선택
    inst_type = st.selectbox(
        "기관 분류", 
        ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"]
    )
    
    # 의료기관 명칭 (예시 문구 포함)
    inst_name = st.text_input("의료기관 명칭", placeholder="예: 한국병원")
    
    col1, col2 = st.columns(2)
    with col1:
        # 담당자 연락처 (예시 문구 포함)
        phone = st.text_input("담당자 연락처", placeholder="예: 010-0000-0000")
    with col2:
        # 담당자 이메일 (예시 문구 포함)
        email = st.text_input("담당자 이메일", placeholder="예: example@mail.com")
        
    st.subheader("📂 보고서 업로드")
    file = st.file_uploader("결과보고서 엑셀파일(.xlsx) 선택", type=["xlsx"])
    
    submitted = st.form_submit_button("제출하기")

# --- 3. 제출 로직 ---
if submitted:
    if inst_name and phone and file:
        with st.spinner("서버에 안전하게 저장 중입니다..."):
            try:
                upload_to_github(file.getvalue(), inst_type, inst_name, phone, email, file.name)
                st.success(f"✅ {inst_name} 담당자님, 제출이 완료되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"제출 중 오류가 발생했습니다: {e}")
    else:
        st.warning("⚠️ 모든 필수 입력 항목을 채우고 파일을 업로드해 주세요.")
