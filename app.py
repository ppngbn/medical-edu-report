import streamlit as st
from github import Github
from datetime import datetime

# --- 설정 (Secrets 금고 사용) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

# 깃허브에 파일을 올리는 함수
def upload_to_github(file_bytes, inst_type, inst_name, original_name):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # 파일명 중복을 막기 위해 현재 시간 기록
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 💡 핵심: 파일명에 [분류]를 포함시킵니다.
    # 결과 예시: 20260421_143000_종합병원_한국병원_결과보고서.xlsx
    path = f"data/{now}_{inst_type}_{inst_name}_{original_name}"
    
    # 깃허브 업로드 실행
    repo.create_file(path, f"Upload: {inst_name}", file_bytes)

# --- 화면 구성 ---
st.set_page_config(page_title="교육 결과 제출", page_icon="🏥")
st.title("🏥 2026년 신고의무자 교육 결과 제출")
st.info("기관 정보를 정확히 입력하시고, 결과보고서 엑셀 파일을 업로드해 주세요.")

with st.form("submit_form"):
    st.subheader("📝 기관 정보")
    
    # 기관 분류 선택
    inst_type = st.selectbox(
        "기관 분류", 
        ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"]
    )
    inst_name = st.text_input("의료기관 명칭", placeholder="예: 한국병원")
    email = st.text_input("담당자 이메일")
    
    st.subheader("📂 파일 업로드")
    file = st.file_uploader("결과보고서(엑셀)를 올려주세요", type=["xlsx"])
    
    submitted = st.form_submit_button("제출하기")

# --- 제출 버튼 눌렀을 때 동작 ---
if submitted:
    if inst_name and file:
        with st.spinner("서버에 안전하게 저장 중입니다... 잠시만 기다려 주세요."):
            try:
                # 엑셀 파일 데이터와 기관 정보를 깃허브로 전송
                upload_to_github(file.getvalue(), inst_type, inst_name, file.name)
                st.success(f"✅ {inst_name} 담당자님, 제출이 완료되었습니다! 감사합니다.")
                st.balloons()
            except Exception as e:
                st.error(f"제출 중 서버 오류가 발생했습니다: {e}")
    else:
        st.error("⚠️ 기관명과 엑셀 파일을 모두 확인해 주세요.")
