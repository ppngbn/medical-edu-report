import streamlit as st
from github import Github
import pandas as pd
import io
import math
from datetime import datetime

# --- 1. 설정 (Secrets 사용) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 통합 관리 시스템")

# 깃허브 연결
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# 기관 분류 리스트 정의 (0건 표시용)
CATEGORIES = ["종합병원", "병원", "요양병원", "한방병원", "치과병원", "의원", "치과의원", "한의원"]

try:
    # 2. 데이터 불러오기 및 파싱
    contents = repo.get_contents("data")
    raw_data = []
    
    for content in contents:
        if content.name == ".gitkeep": continue
        parts = content.name.split('^')
        if len(parts) >= 6:
            dt = parts[0]
            # 파일명 기반 서울 시간 포맷팅
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

    # --- [상단: 통계 요약 (0건 포함)] ---
    st.subheader("📊 기관별 제출 통계")
    
    # 모든 카테고리에 대해 기본값 0 설정
    stats = {cat: 0 for cat in CATEGORIES}
    if not df.empty:
        actual_counts = df['기관분류'].value_counts().to_dict()
        for cat, count in actual_counts.items():
            if cat in stats:
                stats[cat] = count
    
    # 4개씩 2줄로 배치 (가독성 향상)
    stat_cols = st.columns(4)
    for idx, cat in enumerate(CATEGORIES):
        with stat_cols[idx % 4]:
            st.metric(label=cat, value=f"{stats[cat]}건")

    if not df.empty:
        # 최신순 정렬 및 연번(No.) 부여
        df = df.sort_values(by="제출일시", ascending=False).reset_index(drop=True)
        df.insert(0, 'No.', range(1, len(df) + 1))

        # 전체 현황 엑셀 다운로드
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

        # --- [중단: 리스트 페이지네이션 (20줄)] ---
        st.subheader("📋 전체 제출 현황 리스트")
        rows_per_page = 20
        total_pages = math.ceil(len(df) / rows_per_page)
        
        if total_pages > 1:
            page = st.selectbox("리스트 페이지 선택", range(1, total_pages + 1), key="table_page")
        else:
            page = 1
        
        start_idx = (page - 1) * rows_per_page
        st.table(df.iloc[start_idx : start_idx + rows_per_page].drop(columns=['github_path', 'content_obj']))

        st.divider()

        # --- [하단: 개별 기관 파일 관리 (다운로드 및 즉시 삭제)] ---
        st.subheader("📂 개별 기관 파일 관리 (다운로드/삭제)")
        
        if total_pages > 1:
            dl_page = st.select_slider("목록 페이지 이동", options=range(1, total_pages + 1), key="dl_page")
        else:
            dl_page = 1
            
        dl_start = (dl_page - 1) * rows_per_page
        
        for i, row in df.iloc[dl_start : dl_start + rows_per_page].iterrows():
            c1, c2, c3 = st.columns([7, 1.5, 1.5])
            c1.write(f"**{row['No.']}**. [{row['기관분류']}] {row['기관명']} - {row['파일명']}")
            
            c2.download_button(
                label="📥 내려받기", 
                data=row['content_obj'].decoded_content, 
                file_name=row['파일명'], 
                key=f"dl_btn_{row['No.']}"
            )
            
            with c3:
                with st.popover("🗑️ 삭제"):
                    st.warning("정말 삭제하시겠습니까?")
                    if st.button("네, 삭제합니다", key=f"del_confirm_{row['No.']}", type="primary"):
                        try:
                            file_to_del = repo.get_contents(row['github_path'])
                            repo.delete_file(file_to_del.path, f"Admin Delete: {row['기관명']}", file_to_del.sha)
                            st.success(f"{row['기관명']} 삭제 완료")
                            st.rerun()
                        except Exception as e:
                            st.error(f"삭제 실패: {e}")
    else:
        st.divider()
        st.info("현재 제출된 데이터가 없습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
