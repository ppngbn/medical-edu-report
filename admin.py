import streamlit as st
from github import Github
import pandas as pd
import io
import math
from datetime import datetime

# --- 1. 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 통합 관리 시스템")

# 깃허브 연결
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

try:
    # 2. 데이터 불러오기 및 파싱
    contents = repo.get_contents("data")
    raw_data = []
    
    for content in contents:
        if content.name == ".gitkeep": continue
        parts = content.name.split('^')
        if len(parts) >= 6:
            dt = parts[0]
            # 파일명 기반 서울 시간 포맷팅 (YYYY-MM-DD HH:MM:SS)
            f_date = f"{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[9:11]}:{dt[11:13]}:{dt[13:15]}"
            raw_data.append({
                "제출일시": f_date,
                "기관분류": parts[1],
                "기관명": parts[2],
                "연락처": parts[3],
                "이메일": parts[4],
                "파일명": parts[5],
                "github_path": content.path,
                "content_obj": content
            })

    df = pd.DataFrame(raw_data)

    if not df.empty:
        # 최신순 정렬 및 연번(No.) 부여
        df = df.sort_values(by="제출일시", ascending=False).reset_index(drop=True)
        df.insert(0, 'No.', range(1, len(df) + 1))

        # --- [상단: 통계 및 요약] ---
        st.subheader("📊 기관별 제출 통계")
        counts = df['기관분류'].value_counts()
        st.columns(len(counts)) # 칸 나누기
        for i, (cat, count) in enumerate(counts.items()):
            st.sidebar.write(f"{cat}: {count}건") # 사이드바 요약
            
        # 3. 전체 현황 엑셀 다운로드 버튼
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df = df.drop(columns=['github_path', 'content_obj'])
            export_df.to_excel(writer, index=False, sheet_name='제출현황')
        
        st.download_button(
            label="📈 전체 현황 엑셀로 내보내기",
            data=output.getvalue(),
            file_name=f"교육제출현황_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )
        st.divider()

        # --- [중단: 리스트 및 페이지네이션 (20줄)] ---
        st.subheader("📋 전체 제출 현황 리스트 (20건씩 보기)")
        rows_per_page = 20
        total_pages = math.ceil(len(df) / rows_per_page)
        
        # 페이지가 1개보다 많을 때만 선택창 표시
        if total_pages > 1:
            page = st.selectbox("페이지 선택", range(1, total_pages + 1), key="table_page")
        else:
            page = 1
        
        start_idx = (page - 1) * rows_per_page
        st.table(df.iloc[start_idx : start_idx + rows_per_page].drop(columns=['github_path', 'content_obj']))

        st.divider()

        # --- [하단: 개별 파일 다운로드 및 관리] ---
        st.subheader("📂 개별 기관 원본 파일 다운로드")
        
        # 다운로드 구역 전용 페이지네이션 (에러 방지 조건 포함)
        if total_pages > 1:
            dl_page = st.select_slider("목록 페이지 이동", options=range(1, total_pages + 1), key="dl_page")
        else:
            dl_page = 1
            
        dl_start = (dl_page - 1) * rows_per_page
        for i, row in df.iloc[dl_start : dl_start + rows_per_page].iterrows():
            c1, c2 = st.columns([8, 2])
            c1.write(f"**{row['No.']}**. [{row['기관분류']}] {row['기관명']} - {row['파일명']}")
            c2.download_button("📥 내려받기", data=row['content_obj'].decoded_content, 
                               file_name=row['파일명'], key=f"btn_{row['No.']}")

        st.divider()

        # --- [기능: 데이터 삭제] ---
        st.subheader("🛠️ 데이터 관리 (삭제)")
        to_delete = st.multiselect("삭제할 기관을 선택하세요 (No. 기준)", options=df['No.'].tolist())
        if st.button("❌ 선택 항목 영구 삭제"):
            if to_delete:
                for n in to_delete:
                    path = df[df['No.'] == n]['github_path'].values[0]
                    file_to_del = repo.get_contents(path)
                    repo.delete_file(file_to_del.path, "Admin Delete", file_to_del.sha)
                st.success("데이터가 삭제되었습니다. 페이지를 새로고침하세요.")
                st.rerun()

    else:
        st.info("현재 제출된 데이터가 없습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
