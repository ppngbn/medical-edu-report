import streamlit as st
from github import Github
import pandas as pd
import io

# --- 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 통합 관리자 페이지")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

try:
    contents = repo.get_contents("data")
    raw_data = []
    
    for content in contents:
        if content.name == ".gitkeep": continue
        
        # 파일명 분리 (^ 구분자 기준)
        parts = content.name.split('^')
        if len(parts) >= 6:
            raw_data.append({
                "제출일시": f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:8]} {parts[0][9:11]}:{parts[0][11:13]}",
                "기관분류": parts[1],
                "기관명": parts[2],
                "연락처": parts[3],
                "이메일": parts[4],
                "파일명": parts[5],
                "github_path": content.path, # 삭제용 경로
                "download_url": content.download_url,
                "content_obj": content # 다운로드용
            })

    df = pd.DataFrame(raw_data)

    if not df.empty:
        # --- [1. 요약 통계] ---
        st.subheader("📊 기관별 제출 현황")
        counts = df['기관분류'].value_counts()
        cols = st.columns(len(counts))
        for i, (cat, count) in enumerate(counts.items()):
            cols[i].metric(cat, f"{count}건")
        
        st.divider()

        # --- [2. 전체 현황 관리 (표 형식)] ---
        st.subheader("📂 제출 명단 관리")
        
        # 엑셀 추출 기능
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # 삭제용 경로 등 관리용 데이터 제외하고 저장
            export_df = df[["제출일시", "기관분류", "기관명", "연락처", "이메일", "파일명"]]
            export_df.to_excel(writer, index=False, sheet_name='제출현황')
        
        st.download_button(
            label="📈 전체 현황 엑셀로 내보내기",
            data=buffer.getvalue(),
            file_name=f"교육제출현황_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )

        # 데이터 표시 (한 줄 보기)
        st.dataframe(df[["제출일시", "기관분류", "기관명", "연락처", "이메일", "파일명"]], use_container_width=True)

        # --- [3. 파일 다운로드 및 개별 삭제] ---
        st.subheader("🛠️ 개별 데이터 관리 (다운로드/삭제)")
        
        # 선택 삭제를 위한 멀티 셀렉트
        to_delete = st.multiselect("삭제할 기관을 선택하세요 (실행 후 복구 불가)", options=df['기관명'].unique())
        if st.button("❌ 선택한 데이터 영구 삭제"):
            if to_delete:
                for target in to_delete:
                    target_path = df[df['기관명'] == target]['github_path'].values[0]
                    file_to_del = repo.get_contents(target_path)
                    repo.delete_file(file_to_del.path, f"Delete: {target}", file_to_del.sha)
                st.success("데이터가 삭제되었습니다. 페이지를 새로고침하세요.")
                st.rerun()

        st.divider()
        st.write("▼ 개별 파일 다운로드")
        for i, row in df.iterrows():
            c1, c2, c3 = st.columns([6, 2, 2])
            c1.write(f"{row['제출일시']} | {row['기관분류']} | **{row['기관명']}**")
            
            # 다운로드 버튼
            c2.download_button("📥 다운로드", data=row['content_obj'].decoded_content, 
                               file_name=row['파일명'], key=f"dl_{i}")

    else:
        st.info("현재 제출된 데이터가 없습니다.")

except Exception as e:
    st.error(f"데이터 로드 중 오류: {e}")
