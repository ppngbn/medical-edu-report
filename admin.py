import streamlit as st
from github import Github

GITHUB_TOKEN = "11B37IKZY0GVbCp9gUFDCk_BoqViwL3dLTMJuUl6ZggMiZgvBMrsq4RJl2OsigSkjMD6EDHVHIyNxVgUL2"
REPO_NAME = "ppngbn/medical-edu-report"

st.title("🔐 관리자 시스템")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

st.subheader("📊 제출된 파일 리스트")

# data 폴더 안의 파일들 가져오기
try:
    contents = repo.get_contents("data")
    for content in contents:
        col1, col2 = st.columns([3, 1])
        col1.write(f"📄 {content.name}")
        # 다운로드 링크 생성
        col2.markdown(f"[다운로드]({content.download_url})")
except:
    st.write("아직 제출된 파일이 없습니다.")
