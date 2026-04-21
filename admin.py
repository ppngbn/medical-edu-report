import streamlit as st
from github import Github
import github # 에러 처리를 위해 필요함

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"] 
REPO_NAME = st.secrets["REPO_NAME"]


st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 관리자 페이지")

# 깃허브 연결
try:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    st.subheader("📊 제출된 파일 리스트")

    # 'data' 폴더 내 파일 목록 가져오기 시도
    try:
        contents = repo.get_contents("data")
        
        # 파일이 있는 경우 리스트 출력
        for content in contents:
            if content.name == ".gitkeep": continue 
            
            col1, col2 = st.columns([4, 1])
            col1.write(f"📄 {content.name}")
            col2.markdown(f"[📥 다운로드]({content.download_url})")
            st.divider()
            
    except github.GithubException as e:
        # 폴더가 없을 때(404) 발생하는 에러 처리
        if e.status == 404:
            st.info("📢 현재 제출된 보고서가 없습니다. (data 폴더가 아직 생성되지 않음)")
        else:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")

except Exception as e:
    st.error(f"깃허브 연결에 실패했습니다. 토큰과 저장소 이름을 확인해 주세요. ({e})")
