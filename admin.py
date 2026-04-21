import streamlit as st
from github import Github
import pandas as pd
import io
from datetime import datetime
import math

# --- 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 통합 관리 시스템")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

try:
    contents = repo.get_contents("data")
    raw_data = []
    
    for content in contents:
        if content.name == ".gitkeep": continue
        parts = content.name.split('^')
        if len(parts) >= 6:
            # 파일명 앞자리(시간)를 읽기 좋게 변환
            dt = parts[0]
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

    # 최신순 정렬 후 연번(No.) 부여
    df = pd.DataFrame(raw_data)
    if not df.empty:
        df = df.sort_values(by="제출일시", ascending=False).reset_index(drop=True)
        df.index = df.index + 1 # 연번 1부터 시작
        df.insert(0, 'No.', df.index)

        # --- [상단 요약 현황] ---
        st.subheader("📊 기관 분류별 제출 통계")
        counts = df['기관분류'].value_counts()
        cols = st.columns(len(counts))
        for i, (cat, count) in enumerate(counts.items()):
            cols[i].metric(cat, f"{count}건")
        st.divider()

        # --- [중단: 전체 제출 현황 리스트 (페이지네이션)] ---
        st.subheader("📋 전체 제출 현황 리스트")
        
        # 엑셀 다운로드 버튼 (전체 데이터)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.drop(columns=['github_path', 'content_obj']).to_excel(writer, index=False)
        st.download_button("📥 전체 현황 엑셀 다운로드", data=output.getvalue(), file_name="전체현황.xlsx")

        # 페이지네이션 설정
        rows_per_page = 20
        total_pages = math.ceil(len(df) / rows_per_page)
        
        # 페이지 선택 (특정 영역에서만 작동하도록 해당 구역에 배치)
        page = st.selectbox("페이지 선택", range(1, total_pages + 1), key="table_page")
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        st.table(df.iloc[start_idx:end_idx].drop(columns=['github_path', 'content_obj']))

        st.divider()

        # --- [하단: 개별 파일 다운로드 및 관리 (페이지네이션)] ---
        st.subheader("📂 개별 기관 원본 파일 다운로드")
        
        # 다운로드 구역 전용 페이지네이션
        dl_page = st.select_slider("다운로드 목록 페이지", options=range(1, total_pages + 1), key="dl_page")
        dl_start = (dl_page - 1) * rows_per_page
        dl_end = dl_start + rows_per_page
        
        page_df = df.iloc[dl_start:dl_end]
        
        for i, row in page_df.iterrows():
            c1, c2 = st.columns([8, 2])
            c1.write(f"**{row['No.']}**. [{row['기관분류']}] {row['기관명']} - {row['파일명']}")
            c2.download_button("내려받기", data=row['content_obj'].decoded_content, 
                               file_name=row['파일명'], key=f"btn_{row['No.']}")

        st.divider()
        # --- [관리 기능: 삭제] ---
        st.subheader("🛠️ 데이터 관리")
        to_delete = st.multiselect("삭제할 기관 선택 (No. 기준)", options=df['No.'].tolist())
        if st.button("선택 항목 영구 삭제"):
            if to_delete:
                for n in to_delete:
                    path = df[df['No.'] == n]['github_path'].values[0]
                    file_to_del = repo.get_contents(path)
                    repo.delete_file(file_to_del.path, "Admin Delete", file_to_del.sha)
                st.success("삭제되었습니다.")
                st.rerun()

    else:
        st.info("데이터가 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")
