import streamlit as st
from datetime import datetime
import csv
import os

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="2학년 2반 온라인 알리미",
    page_icon="📌",
    layout="centered"
)

SCHEDULE_FILE = "schedule.csv"
ASSIGNMENT_FILE = "assignments.csv"
EXAM_FILE = "exams.csv"
MATERIAL_FILE = "materials.csv"
SUGGESTION_FILE = "suggestions.csv"
CHEER_FILE = "cheer.txt"              # 응원 문구 저장
ADMIN_PASSWORD = "teacher1234"

# ---------------------------
# 🎨 모던 디자인 (CSS)
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

.stApp {
    background-color: #f7f8fa;
    font-family: 'Noto Sans KR', sans-serif;
}

h1 {
    color: #1a1a2e !important;
    text-align: center;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h3 {
    color: #1a1a2e !important;
    font-weight: 700 !important;
    border-left: 4px solid #5b6ef5;
    padding-left: 12px;
}

p, li, span, div, label, .stMarkdown {
    color: #2d2d3a;
}

.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 16px 20px;
    margin: 10px 0;
    border: 1px solid #eceef3;
    box-shadow: 0 2px 10px rgba(30, 40, 90, 0.04);
    color: #2d2d3a;
    animation: fadeUp 0.5s ease;
}
.card:hover {
    box-shadow: 0 4px 16px rgba(91, 110, 245, 0.12);
    transform: translateY(-2px);
    transition: all 0.25s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.stAlert {
    border-radius: 14px !important;
    animation: fadeUp 0.5s ease;
}

.stButton > button {
    background-color: #5b6ef5;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 6px 18px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: #4a5ce0;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(91, 110, 245, 0.3);
}

.stFormSubmitButton > button {
    background-color: #1a1a2e;
    color: white;
    border-radius: 10px;
    font-weight: 600;
    border: none;
    transition: all 0.2s ease;
}
.stFormSubmitButton > button:hover {
    background-color: #5b6ef5;
}

.stTextInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid #dfe2ea !important;
}

hr {
    border: none;
    border-top: 1px solid #e8eaf0;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    font-weight: 600;
}

.point {
    color: #5b6ef5;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 공통 파일 함수
# ---------------------------
def load_data(filename, headers):
    if not os.path.exists(filename):
        return []
    with open(filename, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_data(filename, headers, row):
    file_exists = os.path.exists(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

def delete_data(filename, headers, index):
    items = load_data(filename, headers)
    if 0 <= index < len(items):
        del items[index]
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for item in items:
                writer.writerow([item[h] for h in headers])

# ---------------------------
# 응원 문구 함수 (하나만 저장 → 덮어쓰기)
# ---------------------------
def load_cheer():
    """응원 문구를 불러옵니다. 없으면 기본 문구(시험 종료 버전)를 사용해요."""
    default = "시험 보느라 정말 고생 많았어요! 이제 푹 쉬면서 재충전하는 시간을 가져요. 모두 수고했어요 🎉"
    if not os.path.exists(CHEER_FILE):
        return default
    with open(CHEER_FILE, mode="r", encoding="utf-8") as f:
        text = f.read().strip()
        return text if text else default

def save_cheer(text):
    """응원 문구를 저장(덮어쓰기)합니다."""
    with open(CHEER_FILE, mode="w", encoding="utf-8") as f:
        f.write(text)

# ---------------------------
# 화면 그리기
# ---------------------------
st.title("📌 2학년 2반 온라인 알리미")
st.markdown(
    "<p style='text-align:center; color:#8a8fa3; font-size:15px;'>"
    "오늘 뭐 해야 하는지 한눈에 확인하세요</p>",
    unsafe_allow_html=True
)

st.divider()

# 📌 이번 주 주요 일정
st.subheader("📌 이번 주 주요 일정")
schedule = load_data(SCHEDULE_FILE, ["date", "category", "content"])
if schedule:
    for item in schedule:
        st.info(f"**{item['date']} · {item['category']}**  \n{item['content']}")
else:
    st.markdown("<span style='color:#9a9fb0;'>아직 등록된 일정이 없어요.</span>",
                unsafe_allow_html=True)

st.divider()

# 📝 수행평가
st.subheader("📝 수행평가 / 제출 기한")
assignments = load_data(ASSIGNMENT_FILE, ["subject", "task", "deadline"])
if assignments:
    for a in assignments:
        st.markdown(
            f"<div class='card'><b>{a['subject']}</b> · {a['task']}<br>"
            f"마감 <span class='point'>{a['deadline']}</span></div>",
            unsafe_allow_html=True
        )
else:
    st.markdown("<span style='color:#9a9fb0;'>등록된 수행평가가 없어요.</span>",
                unsafe_allow_html=True)

st.divider()

# 📚 시험 범위
st.subheader("📚 시험 범위")
exams = load_data(EXAM_FILE, ["subject", "content"])
if exams:
    for e in exams:
        st.markdown(
            f"<div class='card'><b>{e['subject']}</b><br>{e['content']}</div>",
            unsafe_allow_html=True
        )
else:
    st.markdown("<span style='color:#9a9fb0;'>등록된 시험 범위가 없어요. (시험 종료!)</span>",
                unsafe_allow_html=True)

st.divider()

# 🎒 준비물
st.subheader("🎒 준비물")
materials = load_data(MATERIAL_FILE, ["content"])
if materials:
    for m in materials:
        st.markdown(f"<div class='card'>{m['content']}</div>", unsafe_allow_html=True)
else:
    st.markdown("<span style='color:#9a9fb0;'>등록된 준비물이 없어요.</span>",
                unsafe_allow_html=True)

st.divider()

# 📣 응원 안내 (시험 종료 버전)
st.subheader("📣 응원 안내")
st.success(load_cheer())

st.divider()

# 🧹 교실 환경 안내
st.subheader("🧹 교실 환경 안내")
st.markdown("""
<div class='card'>
· 하교 전 자기 자리 주변 정리하기<br>
· 창문 닫기 / 전등 끄기 (당번 확인)<br>
· 분리수거 규칙 지키기
</div>
""", unsafe_allow_html=True)

st.divider()

# 💬 익명 건의함
st.subheader("💬 익명 건의함")
st.markdown("<span style='color:#6a6f80;'>불편한 점이나 건의하고 싶은 내용을 남겨주세요. "
            "이름은 쓰지 않아도 돼요.</span>", unsafe_allow_html=True)

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
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_data(SUGGESTION_FILE, ["time", "category", "content"],
                      [now, s_category, suggestion.strip()])
            st.success("건의가 제출되었어요. 소중한 의견 감사합니다 🙏")
            st.toast("건의가 등록되었어요! ✨")

st.divider()

# ---------------------------
# 🔒 관리자 모드
# ---------------------------
st.subheader("🔒 관리자 모드")
st.markdown("<span style='color:#6a6f80;'>공지 등록, 일정 관리는 관리자만 할 수 있어요.</span>",
            unsafe_allow_html=True)

password = st.text_input("관리자 비밀번호를 입력하세요", type="password")

if password == ADMIN_PASSWORD:
    st.success("관리자 로그인 성공 ✅")
    st.toast("환영합니다! 👋")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["일정", "수행평가", "시험범위", "준비물", "응원문구", "건의확인"]
    )

    # ===== 일정 =====
    with tab1:
        st.markdown("#### ➕ 새 일정 등록")
        with st.form("add_schedule"):
            d = st.text_input("날짜 (예: 7/20)")
            c = st.selectbox("종류", ["수행평가", "준비물", "공지", "시험", "기타"])
            content = st.text_area("내용")
            if st.form_submit_button("일정 추가"):
                if d.strip() and content.strip():
                    save_data(SCHEDULE_FILE, ["date", "category", "content"],
                              [d.strip(), c, content.strip()])
                    st.toast("일정이 등록됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("날짜와 내용을 모두 입력해주세요.")

        st.markdown("#### 🗑️ 일정 삭제")
        items = load_data(SCHEDULE_FILE, ["date", "category", "content"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['date']} · {item['category']}** {item['content']}")
                if col2.button("삭제", key=f"sch_{i}"):
                    delete_data(SCHEDULE_FILE, ["date", "category", "content"], i)
                    st.rerun()
        else:
            st.info("등록된 일정이 없어요.")

    # ===== 수행평가 =====
    with tab2:
        st.markdown("#### ➕ 새 수행평가 등록")
        with st.form("add_assignment"):
            subject = st.text_input("과목 (예: 국어)")
            task = st.text_input("내용 (예: 쟁점 글쓰기 제출)")
            deadline = st.text_input("마감일 (예: 7/15)")
            if st.form_submit_button("수행평가 추가"):
                if subject.strip() and task.strip() and deadline.strip():
                    save_data(ASSIGNMENT_FILE, ["subject", "task", "deadline"],
                              [subject.strip(), task.strip(), deadline.strip()])
                    st.toast("수행평가가 등록됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("모든 칸을 입력해주세요.")

        st.markdown("#### 🗑️ 수행평가 삭제")
        items = load_data(ASSIGNMENT_FILE, ["subject", "task", "deadline"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['subject']}** · {item['task']} (마감 {item['deadline']})")
                if col2.button("삭제", key=f"asg_{i}"):
                    delete_data(ASSIGNMENT_FILE, ["subject", "task", "deadline"], i)
                    st.rerun()
        else:
            st.info("등록된 수행평가가 없어요.")

    # ===== 시험범위 =====
    with tab3:
        st.markdown("#### ➕ 새 시험범위 등록")
        with st.form("add_exam"):
            subject = st.text_input("과목 (예: 수학)")
            content = st.text_area("범위 (예: 수열, 함수 단원)")
            if st.form_submit_button("시험범위 추가"):
                if subject.strip() and content.strip():
                    save_data(EXAM_FILE, ["subject", "content"],
                              [subject.strip(), content.strip()])
                    st.toast("시험범위가 등록됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("모든 칸을 입력해주세요.")

        st.markdown("#### 🗑️ 시험범위 삭제")
        items = load_data(EXAM_FILE, ["subject", "content"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['subject']}** · {item['content']}")
                if col2.button("삭제", key=f"exm_{i}"):
                    delete_data(EXAM_FILE, ["subject", "content"], i)
                    st.rerun()
        else:
            st.info("등록된 시험범위가 없어요.")

    # ===== 준비물 =====
    with tab4:
        st.markdown("#### ➕ 새 준비물 등록")
        with st.form("add_material"):
            content = st.text_input("준비물 (예: 체육복 (화, 목))")
            if st.form_submit_button("준비물 추가"):
                if content.strip():
                    save_data(MATERIAL_FILE, ["content"], [content.strip()])
                    st.toast("준비물이 등록됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("내용을 입력해주세요.")

        st.markdown("#### 🗑️ 준비물 삭제")
        items = load_data(MATERIAL_FILE, ["content"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(f"{item['content']}")
                if col2.button("삭제", key=f"mat_{i}"):
                    delete_data(MATERIAL_FILE, ["content"], i)
                    st.rerun()
        else:
            st.info("등록된 준비물이 없어요.")

    # ===== 응원 문구 =====
    with tab5:
        st.markdown("#### 📣 응원 문구 수정")
        st.markdown("<span style='color:#6a6f80;'>현재 문구를 확인하고 새로 바꿀 수 있어요.</span>",
                    unsafe_allow_html=True)

        st.success(load_cheer())  # 현재 문구 미리보기

        with st.form("edit_cheer"):
            new_cheer = st.text_area("새 응원 문구를 입력하세요", value=load_cheer())
            if st.form_submit_button("응원 문구 저장"):
                if new_cheer.strip():
                    save_cheer(new_cheer.strip())
                    st.toast("응원 문구가 바뀌었어요! ✨")
                    st.rerun()
                else:
                    st.warning("문구를 입력해주세요.")

    # ===== 건의 확인 =====
    with tab6:
        st.markdown("#### 📬 접수된 건의")
        items = load_data(SUGGESTION_FILE, ["time", "category", "content"])
        if items:
            for item in items:
                st.markdown(
                    f"<div class='card'><span style='color:#8a8fa3; font-size:13px;'>"
                    f"{item['time']} · {item['category']}</span><br>{item['content']}</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("아직 접수된 건의가 없어요.")

elif password != "":
    st.error("비밀번호가 올바르지 않아요.")
