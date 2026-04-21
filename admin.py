import streamlit as st
from github import Github

# --- 설정 (app.py와 동일하게) ---
GITHUB_TOKEN = "11B37IKZY0GVbCp9gUFDCk_BoqViwL3dLTMJuUl6ZggMiZgvBMrsq4RJl2OsigSkjMD6EDHVHIyNxVgUL2"
REPO_NAME = "ppngbn/medical-edu-report"

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 관리자 페이지")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

st.subheader("📊 제출된 파일 리스트")

try:
    # 'data' 폴더 내 파일 목록 가져오기
    contents = repo.get_contents("data")
    
    # 보기 좋게 표 형식으로 구성하기 위한 리스트
    file_list = []
    for content in contents:
        if content.name == ".gitkeep": continue # 빈 폴더 유지용 파일 제외
        
        col1, col2 = st.columns([4, 1])
        col1.write(f"📄 {content.name}")
        # 클릭 시 바로 다운로드 가능한 링크
        col2.markdown(f"[📥 다운로드]({content.download_url})")
        st.divider()
        
except Exception as e:
    st.info("아직 제출된 파일이 없거나 data 폴더가 생성되지 않았습니다.")
