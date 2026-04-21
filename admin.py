import streamlit as st
from github import Github
import pandas as pd

# --- 설정 (Secrets 금고 사용) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 대시보드", layout="wide")
st.title("📊 교육 결과보고 제출 현황판")

# 깃허브 연결
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

try:
    # 'data' 폴더 안의 파일들 가져오기
    contents = repo.get_contents("data")
    
    # 1. 파일 이름에서 필요한 정보(통계용) 뽑아내기
    raw_data = []
    for content in contents:
        if content.name == ".gitkeep": continue # 빈 폴더 방지용 파일은 제외
        
        # 파일명 구조: [시간]_[기관분류]_[기관명]_[원래파일명].xlsx
        parts = content.name.split('_')
        
        if len(parts) >= 3:
            raw_data.append({
                "제출시간": parts[0],
                "기관분류": parts[1],
                "기관명": parts[2],
                "파일명": content.name,
                "content_obj": content # 💡 다운로드를 위해 파일 객체 자체를 저장
            })

    # 데이터를 분석하기 쉬운 표(DataFrame)로 변환
    df = pd.DataFrame(raw_data)

    # --- 2. 상단: 기관 분류별 종합 통계 (대시보드 핵심) ---
    st.subheader("💡 종합 현황 (기관 분류별 제출 수)")
    if not df.empty:
        counts = df['기관분류'].value_counts()
        
        # 종류 개수만큼 가로로 칸을 나누어서 숫자 표시
        cols = st.columns(len(counts))
        for i, (cat, count) in enumerate(counts.items()):
            cols[i].metric(label=cat, value=f"{count}개소")
    else:
        st.info("아직 제출된 내역이 없습니다.")

    st.divider()

    # --- 3. 하단: 필터링 가능한 상세 리스트 및 다운로드 ---
    st.subheader("📂 상세 제출 내역 및 다운로드")
    if not df.empty:
        # 드롭다운으로 원하는 기관만 걸러서 보기 기능
        selected_cat = st.multiselect(
            "📌 필터링할 기관 분류를 선택하세요", 
            options=df['기관분류'].unique(), 
            default=df['기관분류'].unique()
        )
        
        # 선택한 기관만 남기기
        filtered_df = df[df['기관분류'].isin(selected_cat)]
        st.write(f"검색 결과: 총 **{len(filtered_df)}**건")
        
        # 리스트 출력 및 다운로드 버튼 생성
        for index, row in filtered_df.iterrows():
            col1, col2, col3 = st.columns([1.5, 4, 2])
            
            # 날짜 형식 다듬기 (YYYYMMDD -> YYYY-MM-DD)
            date_str = row['제출시간']
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            col1.write(f"**[{row['기관분류']}]**")
            col2.write(f"{row['기관명']} (제출일: {formatted_date})")
            
            # 💡 사내 보안망 우회용 다운로드 버튼
            with col3:
                # 다운로드 버튼을 누르기 전 미리 파일 데이터를 읽어옴
                file_data = row['content_obj'].decoded_content
                st.download_button(
                    label="📥 내려받기",
                    data=file_data,
                    file_name=row['파일명'],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=row['파일명']
                )
            st.markdown("---")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다. (아직 제출 내역이 없거나 네트워크 오류일 수 있습니다): {e}")
