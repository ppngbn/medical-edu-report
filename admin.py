import streamlit as st
from github import Github
import pandas as pd
import io

# --- 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 통합 관리 시스템")

# 깃허브 연결
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

st.subheader("📊 기관별 교육 이수 현황 합계")

try:
    contents = repo.get_contents("data")
    
    all_data = [] # 모든 기관의 숫자를 모을 리스트
    file_info_list = [] # 파일 다운로드용 리스트

    with st.spinner('데이터를 분석 중입니다...'):
        for content in contents:
            if content.name == ".gitkeep": continue
            
            # 1. 파일 내용 가져오기 (메모리로 직접 읽기)
            file_data = content.decoded_content
            
            try:
                # 2. 엑셀 분석 (보안망을 타지 않고 서버 내부에서 읽음)
                df = pd.read_excel(io.BytesIO(file_data))
                
                # 예시 서식의 컬럼명에 맞춰 데이터 추출 (컬럼명은 서식에 맞게 수정 필요)
                # 여기서는 '교육명', '대상자수', '이수자수'가 있다고 가정합니다.
                if '교육명' in df.columns:
                    summary = df.groupby('교육명')[['대상자수', '이수자수']].sum().reset_index()
                    summary['기관명'] = content.name.split('_')[1] # 파일명에서 기관명 추출
                    all_data.append(summary)
                
                # 파일 다운로드용 정보 저장
                file_info_list.append({"name": content.name, "data": file_data})
                
            except Exception as e:
                st.warning(f"⚠️ {content.name} 파일을 읽을 수 없습니다: {e}")

    # --- [화면 출력 1: 통합 집계표] ---
    if all_data:
        total_df = pd.concat(all_data, ignore_index=True)
        # 전체 합계 계산
        pivot_total = total_df.groupby('교육명')[['대상자수', '이수자수']].sum()
        pivot_total['이수율(%)'] = (pivot_total['이수자수'] / pivot_total['대상자수'] * 100).round(1)
        
        st.write("### 📈 전체 교육 항목별 합계")
        st.table(pivot_total)
        
        st.write("### 🏢 기관별 상세 내역")
        st.dataframe(total_df)
    else:
        st.info("아직 분석할 데이터가 없습니다.")

    st.divider()

    # --- [화면 출력 2: 보안망 우회 다운로드] ---
    st.subheader("📥 원본 파일 다운로드")
    st.caption("링크 방식이 아닌 사이트 직접 전송 방식으로 보안 차단을 우회합니다.")
    
    for file_info in file_info_list:
        col1, col2 = st.columns([4, 1])
        col1.write(f"📄 {file_info['name']}")
        # 💡 중요: 링크가 아닌 st.download_button 사용 (보안망 통과 가능성 높음)
        col2.download_button(
            label="내려받기",
            data=file_info['data'],
            file_name=file_info['name'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=file_info['name'] # 고유 키 설정
        )

except Exception as e:
    st.error(f"데이터를 가져오는 중 오류 발생: {e}")
