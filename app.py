import streamlit as st
from datetime import datetime, date
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
CHEER_FILE = "cheer.txt"
DDAY_FILE = "ddays.csv"               # D-Day 목록
LUNCH_FILE = "lunch.txt"              # 급식 메뉴 (하나만)
CLEANING_FILE = "cleaning.csv"        # 청소 당번 / 1인 1역
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

/* D-Day 전용 카드 */
.dday-card {
    background: linear-gradient(135deg, #5b6ef5 0%, #8b5cf6 100%);
    border-radius: 16px;
    padding: 18px 22px;
    margin: 10px 0;
    color: white !important;
    box-shadow: 0 4px 14px rgba(91, 110, 245, 0.25);
    animation: fadeUp 0.5s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.dday-card * { color: white !important; }
.dday-num {
    font-size: 24px;
    font-weight: 800;
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
    flex-wrap: wrap;
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

def overwrite_all(filename, headers, items):
    """목록 전체를 다시 저장합니다. (좋아요 수 갱신 등에 사용)"""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for item in items:
            writer.writerow([item[h] for h in headers])

# ---------------------------
# 단일 텍스트 저장 함수 (응원문구, 급식)
# ---------------------------
def load_text(filename, default):
    if not os.path.exists(filename):
        return default
    with open(filename, mode="r", encoding="utf-8") as f:
        text = f.read().strip()
        return text if text else default

def save_text(filename, text):
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(text)

# ---------------------------
# D-Day 계산 함수
# ---------------------------
def calc_dday(target_str):
    """목표 날짜까지 남은 날을 계산합니다. (예: '2025-07-25')"""
    try:
        target = datetime.strptime(target_str, "%Y-%m-%d").date()
        today = date.today()
        diff = (target - today).days
        if diff > 0:
            return f"D-{diff}"
        elif diff == 0:
            return "D-DAY"
        else:
            return f"D+{abs(diff)}"
    except ValueError:
        return "날짜오류"

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

# 📅 D-Day 카운터
st.subheader("📅 D-Day 카운터")
ddays = load_data(DDAY_FILE, ["title", "target"])
if ddays:
    for d in ddays:
        st.markdown(
            f"<div class='dday-card'><span>🎯 {d['title']} "
            f"<small>({d['target']})</small></span>"
            f"<span class='dday-num'>{calc_dday(d['target'])}</span></div>",
            unsafe_allow_html=True
        )
else:
    st.markdown("<span style='color:#9a9fb0;'>등록된 D-Day가 없어요.</span>",
                unsafe_allow_html=True)

st.divider()

# 🍱 오늘의 급식
st.subheader("🍱 오늘의 급식")
lunch = load_text(LUNCH_FILE, "아직 오늘의 급식이 등록되지 않았어요.")
st.info(lunch)

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
    st.markdown("<span style='color:#9a9fb0;'>등록된 시험 범위가 없어요.</span>",
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

# 🧹 청소 당번 / 1인 1역
st.subheader("🧹 청소 당번 / 1인 1역")
cleanings = load_data(CLEANING_FILE, ["role", "name"])
if cleanings:
    for c in cleanings:
        st.markdown(
            f"<div class='card'><b>{c['role']}</b> · {c['name']}</div>",
            unsafe_allow_html=True
        )
else:
    st.markdown("<span style='color:#9a9fb0;'>등록된 당번이 없어요.</span>",
                unsafe_allow_html=True)

st.divider()

# 📣 응원 안내
st.subheader("📣 응원 안내")
default_cheer = "시험 보느라 정말 고생 많았어요! 이제 푹 쉬면서 재충전하는 시간을 가져요. 모두 수고했어요 🎉"
st.success(load_text(CHEER_FILE, default_cheer))

st.divider()

# 🧼 교실 환경 안내
st.subheader("🧼 교실 환경 안내")
st.markdown("""
<div class='card'>
· 하교 전 자기 자리 주변 정리하기<br>
· 창문 닫기 / 전등 끄기 (당번 확인)<br>
· 분리수거 규칙 지키기
</div>
""", unsafe_allow_html=True)

st.divider()

# 💬 건의 게시판 (공개 + 좋아요)
st.subheader("💬 건의 게시판")
st.markdown("<span style='color:#6a6f80;'>친구들의 건의에 공감하면 👍를 눌러주세요! "
            "이름은 쓰지 않아도 돼요.</span>", unsafe_allow_html=True)

# 건의 작성 폼
with st.form("suggestion_form"):
    s_category = st.selectbox(
        "건의 종류",
        ["학급 공지", "수행평가/일정", "교실 환경", "시험기간", "기타"]
    )
    suggestion = st.text_area("건의 내용")
    s_submitted = st.form_submit_button("건의 올리기")

    if s_submitted:
        if suggestion.strip() == "":
            st.warning("건의 내용을 입력해주세요.")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            # 좋아요(likes)는 0으로 시작
            save_data(SUGGESTION_FILE, ["time", "category", "content", "likes"],
                      [now, s_category, suggestion.strip(), "0"])
            st.success("건의가 등록되었어요! 🙏")
            st.toast("건의가 올라갔어요! ✨")
            st.rerun()

# 건의 목록 + 좋아요 버튼
suggestions = load_data(SUGGESTION_FILE, ["time", "category", "content", "likes"])
if suggestions:
    # 좋아요 많은 순으로 정렬
    suggestions_sorted = sorted(
        suggestions, key=lambda x: int(x.get("likes", 0)), reverse=True
    )
    for idx, item in enumerate(suggestions_sorted):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                f"<div class='card'><span style='color:#8a8fa3; font-size:13px;'>"
                f"{item['time']} · {item['category']}</span><br>{item['content']}</div>",
                unsafe_allow_html=True
            )
        with col2:
            like_count = int(item.get("likes", 0))
            if st.button(f"👍 {like_count}", key=f"like_{item['time']}_{idx}"):
                # 원본 목록에서 같은 건의를 찾아 좋아요 +1
                for s in suggestions:
                    if s["time"] == item["time"] and s["content"] == item["content"]:
                        s["likes"] = str(int(s.get("likes", 0)) + 1)
                        break
                overwrite_all(SUGGESTION_FILE,
                              ["time", "category", "content", "likes"], suggestions)
                st.rerun()
else:
    st.markdown("<span style='color:#9a9fb0;'>아직 올라온 건의가 없어요.</span>",
                unsafe_allow_html=True)

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

    tab_dday, tab_lunch, tab_clean, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["D-Day", "급식", "청소당번", "일정", "수행평가", "시험범위", "준비물", "응원문구", "건의관리"]
    )

    # ===== D-Day =====
    with tab_dday:
        st.markdown("#### ➕ 새 D-Day 등록")
        with st.form("add_dday"):
            title = st.text_input("이름 (예: 기말고사)")
            target = st.date_input("목표 날짜")
            if st.form_submit_button("D-Day 추가"):
                if title.strip():
                    save_data(DDAY_FILE, ["title", "target"],
                              [title.strip(), target.strftime("%Y-%m-%d")])
                    st.toast("D-Day가 등록됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("이름을 입력해주세요.")

        st.markdown("#### 🗑️ D-Day 삭제")
        items = load_data(DDAY_FILE, ["title", "target"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(f"🎯 **{item['title']}** ({item['target']}) → {calc_dday(item['target'])}")
                if col2.button("삭제", key=f"dday_{i}"):
                    delete_data(DDAY_FILE, ["title", "target"], i)
                    st.rerun()
        else:
            st.info("등록된 D-Day가 없어요.")

    # ===== 급식 =====
    with tab_lunch:
        st.markdown("#### 🍱 오늘의 급식 수정")
        st.info(load_text(LUNCH_FILE, "아직 등록되지 않았어요."))
        with st.form("edit_lunch"):
            new_lunch = st.text_area(
                "급식 메뉴를 입력하세요",
                value=load_text(LUNCH_FILE, "")
            )
            if st.form_submit_button("급식 저장"):
                if new_lunch.strip():
                    save_text(LUNCH_FILE, new_lunch.strip())
                    st.toast("급식이 저장됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("메뉴를 입력해주세요.")

    # ===== 청소 당번 =====
    with tab_clean:
        st.markdown("#### ➕ 청소 당번 / 1인 1역 등록")
        with st.form("add_cleaning"):
            role = st.text_input("역할 (예: 칠판 담당, 창문 담당)")
            name = st.text_input("이름")
            if st.form_submit_button("당번 추가"):
                if role.strip() and name.strip():
                    save_data(CLEANING_FILE, ["role", "name"],
                              [role.strip(), name.strip()])
                    st.toast("당번이 등록됐어요! ✨")
                    st.rerun()
                else:
                    st.warning("역할과 이름을 모두 입력해주세요.")

        st.markdown("#### 🗑️ 당번 삭제")
        items = load_data(CLEANING_FILE, ["role", "name"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['role']}** · {item['name']}")
                if col2.button("삭제", key=f"clean_{i}"):
                    delete_data(CLEANING_FILE, ["role", "name"], i)
                    st.rerun()
        else:
            st.info("등록된 당번이 없어요.")

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
        st.success(load_text(CHEER_FILE, default_cheer))
        with st.form("edit_cheer"):
            new_cheer = st.text_area("새 응원 문구를 입력하세요",
                                     value=load_text(CHEER_FILE, default_cheer))
            if st.form_submit_button("응원 문구 저장"):
                if new_cheer.strip():
                    save_text(CHEER_FILE, new_cheer.strip())
                    st.toast("응원 문구가 바뀌었어요! ✨")
                    st.rerun()
                else:
                    st.warning("문구를 입력해주세요.")

    # ===== 건의 관리 =====
    with tab6:
        st.markdown("#### 📬 건의 관리 (삭제)")
        items = load_data(SUGGESTION_FILE, ["time", "category", "content", "likes"])
        if items:
            for i, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.markdown(
                    f"<span style='color:#8a8fa3; font-size:13px;'>"
                    f"{item['time']} · {item['category']} · 👍 {item.get('likes', 0)}</span><br>"
                    f"{item['content']}",
                    unsafe_allow_html=True
                )
                if col2.button("삭제", key=f"sug_del_{i}"):
                    delete_data(SUGGESTION_FILE,
                                ["time", "category", "content", "likes"], i)
                    st.rerun()
        else:
            st.info("아직 접수된 건의가 없어요.")

elif password != "":
    st.error("비밀번호가 올바르지 않아요.")
