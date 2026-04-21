import streamlit as st
from github import Github
import pandas as pd
import io
from datetime import datetime

# --- 설정 ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

st.set_page_config(page_title="관리자 시스템", layout="wide")
st.title("🔐 교육 결과보고 통합 관리 시스템")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

try:
    # 1. 깃허브에서 파일 목록 가져오기
    contents = repo.get_contents("data")
    raw_data = []
    
    for content in contents:
        if content.name == ".gitkeep": continue
        
        # 파일명 분석 (구분자 '^' 기준)
        parts = content.name.split('^')
        if len(parts) >= 6:
            raw_data.append({
                "제출일시": f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:8]} {parts[0][9:11]}:{parts[0][11:13]}",
                "기관분류": parts[1],
                "기관명": parts[2],
                "연락처": parts[3],
                "이메일": parts[4],
                "파일명": parts[5],
                "github_path": content.path, # 삭제용
                "content_obj": content      # 다운로드용
            })

    df = pd.DataFrame(raw_data)

    if not df.empty:
        # --- [상단 요약 현황] ---
        st.subheader("📊 기관 분류별 제출 통계")
        counts = df['기관분류'].value_counts()
        cols = st.columns(len(counts))
        for i, (cat, count) in enumerate(counts.items()):
            cols[i].metric(cat, f"{count}건")
        
        st.divider()

        # --- [중단: 전체 리스트 및 엑셀 추출] ---
        st.subheader("📋 전체 제출 현황 리스트")
        
        # 전체 리스트 엑셀로 추출하기 버튼
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df = df[["제출일시", "기관분류", "기관명", "연락처", "이메일", "파일명"]]
            export_df.to_excel(writer, index=False, sheet_name='현황')
        
        st.download_button(
            label="📥 전체 제출현황 엑셀 다운로드",
            data=output.getvalue(),
            file_name=f"전체제출현황_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel"
        )

        # 표로 한 줄씩 보여주기
        st.dataframe(df[["제출일시", "기관분류", "기관명", "연락처", "이메일", "파일명"]], use_container_width=True)

        st.divider()

        # --- [하단: 개별 관리 (다운로드 및 삭제)] ---
        st.subheader("🛠️ 개별 파일 관리")
        
        # 삭제 기능을 위한 선택 박스
        to_delete = st.multiselect("❌ 삭제할 기관 선택 (파일이 영구 삭제됩니다)", options=df['기관명'].unique())
        if st.button("선택 항목 삭제 실행"):
            if to_delete:
                for target in to_delete:
                    target_row = df[df['기관명'] == target].iloc[0]
                    file_to_del = repo.get_contents(target_row['github_path'])
                    repo.delete_file(file_to_del.path, f"관리자 삭제: {target}", file_to_del.sha)
                st.success("선택한 데이터가 삭제되었습니다.")
                st.rerun() # 페이지 새로고침

        st.write("▼ 개별 기관 원본 파일 다운로드")
        for i, row in df.iterrows():
            c1, c2 = st.columns([8, 2])
            c1.write(f"[{row['기관분류']}] {row['기관명']} - {row['파일명']}")
            c2.download_button("내려받기", data=row['content_obj'].decoded_content, 
                               file_name=row['파일명'], key=f"btn_{i}")

    else:
        st.info("현재 제출된 데이터가 없습니다.")

except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
