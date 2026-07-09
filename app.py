import streamlit as st
from datetime import datetime
import csv
import os

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="우리 반 온라인 알리미",
    page_icon="🏫",
    layout="centered"
)

SUGGESTION_FILE = "suggestions.csv"   # 건의 내용 저장 파일
SCHEDULE_FILE = "schedule.csv"        # 일정/공지 저장 파일
ADMIN_PASSWORD = "teacher1234"        # 관리자 비밀번호 (원하는 값으로 변경)

# ---------------------------
# 고정 데이터 (자주 안 바뀌는 것)
# ---------------------------
assignments = [
    {"subject": "국어", "task": "쟁점 글쓰기 제출", "deadline": "7/10"},
    {"subject": "영어", "task": "발표 대본 준비", "deadline": "7/12"},
    {"subject": "과학", "task": "탐구 보고서 제출", "deadline": "7/15"},
]

exam_range = {
    "국어": "교과서 120~155쪽, 학습지 3~5번",
    "수학": "수열, 함수 단원",
    "영어": "교과서 5과 본문, 단어장 1~3회독",
}

materials = [
    "체육복 (화, 목)",
    "실험용 앞치마 (수)",
    "미술 준비물: 색연필, 스케치북 (금)",
]

# ---------------------------
# 일정(공지) 관련 함수
# ---------------------------
def load_schedule():
    """저장된 일정을 파일에서 불러옵니다."""
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_schedule(date_str, category, content):
    """새 일정을 파일에 추가로 저장합니다."""
    file_exists = os.path.exists(SCHEDULE_FILE)
    with open(SCHEDULE_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "category", "content"])  # 헤더
        writer.writerow([date_str, category, content])

def delete_schedule(index):
    """특정 순서의 일정을 삭제합니다."""
    items = load_schedule()
    if 0 <= index < len(items):
        del items[index]
        with open(SCHEDULE_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "content"])
            for item in items:
                writer.writerow([item["date"], item["category"], item["content"]])

# ---------------------------
# 건의 저장 함수
# ---------------------------
def save_suggestion(category, content):
    """건의 내용을 CSV 파일에 저장합니다."""
    file_exists = os.path.exists(SUGGESTION_FILE)
    with open(SUGGESTION_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["시간", "종류", "내용"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        writer.writerow([now, category, content])

# ---------------------------
# 화면 그리기
# ---------------------------
st.title("🏫 우리 반 온라인 알리미")
st.caption("수행평가, 시험 일정, 준비물, 공지사항을 한곳에서 확인하세요.")

st.divider()

# 이번 주 주요 일정 (파일에서 불러와서 표시)
st.subheader("📌 이번 주 주요 일정")
schedule = load_schedule()
if schedule:
    for item in schedule:
        st.info(f"**{item['date']} [{item['category']}]**  \n{item['content']}")
else:
    st.write("아직 등록된 일정이 없습니다.")

st.divider()

# 수행평가 / 제출 기한
st.subheader("📝 수행평가 / 제출 기한")
for a in assignments:
    st.write(f"- **{a['subject']}**: {a['task']} / 마감: **{a['deadline']}**")

st.divider()

# 시험 범위
st.subheader("📚 시험 범위")
for subject, content in exam_range.items():
    st.write(f"- **{subject}**: {content}")

st.divider()

# 준비물
st.subheader("🎒 준비물")
for m in materials:
    st.write(f"- {m}")

st.divider()

# 시험기간 응원 안내
st.subheader("📣 시험기간 응원 안내")
st.success("시험 준비하느라 고생 많아요! 충분히 자고, 컨디션 관리도 공부의 일부예요. 우리 모두 파이팅! 💪")

st.divider()

# 교실 환경 안내
st.subheader("🧹 교실 환경 안내")
st.write("- 하교 전 자기 자리 주변 정리하기")
st.write("- 창문 닫기 / 전등 끄기 (당번 확인)")
st.write("- 분리수거 규칙 지키기")

st.divider()

# 익명 건의함
st.subheader("💬 익명 건의함")
st.write("불편한 점이나 건의하고 싶은 내용을 남겨주세요. 이름은 쓰지 않아도 됩니다.")

with st.form("suggestion_form"):
    s_category = st.selectbox(
        "건의 종류",
        ["학급 공지", "수행평가/일정", "교실 환경", "시험기간", "기타"]
    )
    suggestion = st.text_area("건의 내용")
    s_submitted = st.form_submit_button("제출하기")

    if s_submitted:
        if suggestion.strip() == "":
            st.warning("건의 내용을 입력해주세요.")
        else:
            save_suggestion(s_category, suggestion.strip())
            st.success("건의가 제출되었습니다. 소중한 의견 감사합니다! 🙏")

st.divider()

# ---------------------------
# 관리자 모드 (일정 추가/삭제, 건의 확인)
# ---------------------------
st.subheader("🔒 관리자 모드")
st.write("공지 등록, 일정 관리는 관리자만 할 수 있습니다.")

password = st.text_input("관리자 비밀번호를 입력하세요", type="password")

if password == ADMIN_PASSWORD:
    st.success("관리자 로그인 성공! ✅")

    # --- 일정(공지) 추가 ---
    st.markdown("### ➕ 새 일정 / 공지 등록")
    with st.form("schedule_form"):
        new_date = st.text_input("날짜 (예: 7/20)")
        new_category = st.selectbox(
            "종류",
            ["수행평가", "준비물", "공지", "시험", "기타"]
        )
        new_content = st.text_area("내용")
        add_submitted = st.form_submit_button("일정 추가하기")

        if add_submitted:
            if new_date.strip() == "" or new_content.strip() == "":
                st.warning("날짜와 내용을 모두 입력해주세요.")
            else:
                save_schedule(new_date.strip(), new_category, new_content.strip())
                st.success("일정이 등록되었습니다!")
                st.rerun()

    # --- 일정 삭제 ---
    st.markdown("### 🗑️ 일정 삭제")
    current_schedule = load_schedule()
    if current_schedule:
        for i, item in enumerate(current_schedule):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{item['date']} [{item['category']}]** {item['content']}")
            with col2:
                if st.button("삭제", key=f"del_{i}"):
                    delete_schedule(i)
                    st.rerun()
    else:
        st.write("삭제할 일정이 없습니다.")

    # --- 건의 내용 확인 ---
    st.markdown("### 📬 접수된 건의 확인")
    if os.path.exists(SUGGESTION_FILE):
        with open(SUGGESTION_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if len(rows) > 1:
            st.table(rows[1:])
        else:
            st.write("아직 접수된 건의가 없습니다.")
    else:
        st.write("아직 접수된 건의가 없습니다.")

elif password != "":
    st.error("비밀번호가 올바르지 않습니다.")
