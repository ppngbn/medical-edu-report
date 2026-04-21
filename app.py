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

# --- 페이지 설정 ---
st.set_page_config(page_title="의료기관 교육보고 시스템", page_icon="🏥")

# 간단한 디자인 적용
st.markdown("""
    <style>
    .report-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 2026년 신고의무자 교육 결과보고")
st.info("기관 정보와 엑셀 파일을 업로드하면 교육 결과가 자동으로 집계됩니다.")

# --- 입력 폼 ---
with st.form("main_form"):
    st.subheader("📝 기관 정보 입력")
    col1, col2 = st.columns(2)
    with col1:
        inst_type = st.selectbox("기관 분류", ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"])
        inst_name = st.text_input("의료기관명")
    with col2:
        email = st.text_input("담당자 이메일")
        phone = st.text_input("담당자 연락처")
    
    st.subheader("📂 결과보고서 업로드")
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx)을 선택하세요", type=["xlsx"])
    
    submit = st.form_submit_button("제출 및 자동 결산 시작")

# --- 제출 및 분석 로직 ---
if submit:
    if not inst_name or not uploaded_file:
        st.error("기관명과 파일을 모두 확인해 주세요!")
    else:
        try:
            # 엑셀 읽기 (유저가 올린 서식 기준)
            df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ {inst_name}님, 제출이 완료되었습니다!")
            
            # --- 내부 자료 결산 (자동 추출) ---
            st.markdown("---")
            st.subheader("📊 제출 내용 자동 결산 (내부 자료)")
            
            # 교육명 열에서 데이터 추출 (예시 파일의 구조를 가정)
            # 보통 '교육명', '대상자수', '이수자수' 컬럼이 있다고 가정합니다.
            summary_df = df[['교육명', '대상자수', '이수자수', '이수율']].copy()
            
            # 화면에 표로 깔끔하게 출력
            st.table(summary_df)
            
            # 담당자용 팁
            st.caption("위 데이터는 시스템에 임시 기록되었습니다. 관리자 페이지에서 전체 합계를 확인하세요.")
            
        except Exception as e:
            st.error(f"파일 분석 중 오류가 발생했습니다. 서식을 확인해 주세요. (오류내용: {e})")
