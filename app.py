import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
import random

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Student App", layout="wide")

# -------------------------------
# DATABASE (FIXED)
# -------------------------------
conn = sqlite3.connect("students.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    username TEXT,
    subject TEXT,
    date TEXT
)
""")
conn.commit()

# Insert default user
try:
    c.execute("INSERT INTO users VALUES (?, ?)", ("admin", "1234"))
    conn.commit()
except:
    pass

# -------------------------------
# SESSION
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# -------------------------------
# DARK MODE + GLASS UI
# -------------------------------
dark = st.sidebar.toggle("🌙 Dark Mode")

if dark:
    bg = "#0e1117"
    text = "white"
    glass = "rgba(255,255,255,0.1)"
else:
    bg = "#66a6ff"
    text = "black"
    glass = "rgba(255,255,255,0.3)"

st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
}}
.glass {{
    background: {glass};
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# NOTIFICATION
# -------------------------------
def notify(msg):
    st.toast(msg)

# -------------------------------
# SIDEBAR
# -------------------------------
if st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Attendance", "Study Planner", "Logout"])
else:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# -------------------------------
# LOGIN (FIXED)
# -------------------------------
def login():
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = c.fetchone()

        if result:
            st.session_state.logged_in = True
            st.session_state.user = user
            notify("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid username or password ❌")

# -------------------------------
# REGISTER
# -------------------------------
def register():
    st.title("🆕 Register")

    user = st.text_input("New Username")
    pwd = st.text_input("New Password", type="password")

    if st.button("Register"):
        try:
            c.execute("INSERT INTO users VALUES (?,?)", (user, pwd))
            conn.commit()
            notify("Registered successfully ✅")
        except:
            st.error("Username already exists ❌")

# -------------------------------
# DASHBOARD
# -------------------------------
def dashboard():
    st.title(f"👋 Welcome {st.session_state.user}")

    st.markdown('<div class="glass">📊 Dashboard Overview</div>', unsafe_allow_html=True)

    c.execute("SELECT * FROM attendance WHERE username=?", (st.session_state.user,))
    total = len(c.fetchall())

    col1, col2 = st.columns(2)

    col1.metric("Total Attendance", total)
    col2.metric("Status", "Active")

# -------------------------------
# ATTENDANCE + PIE CHART
# -------------------------------
def attendance():
    st.title("📝 Attendance")

    subjects = ["Math", "Physics", "Programming"]
    subject = st.selectbox("Subject", subjects)

    selected_date = st.date_input("Date", date.today())

    if st.button("Mark Attendance"):
        c.execute("INSERT INTO attendance VALUES (?,?,?)",
                  (st.session_state.user, subject, str(selected_date)))
        conn.commit()
        notify("Attendance saved ✅")

    if st.button("View Records"):
        c.execute("SELECT subject,date FROM attendance WHERE username=?",
                  (st.session_state.user,))
        data = c.fetchall()

        if data:
            df = pd.DataFrame(data, columns=["Subject", "Date"])
            st.dataframe(df, use_container_width=True)

            # Pie chart
            counts = df["Subject"].value_counts()

            st.subheader("📊 Subject Analytics")

            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct="%1.1f%%")
            ax.axis("equal")

            st.pyplot(fig)
        else:
            st.info("No records found")

# -------------------------------
# SMART STUDY PLANNER
# -------------------------------
def study_planner():
    st.title("📅 Smart Study Planner")

    num = st.number_input("Subjects", 1, 10)

    subjects = []
    scores = []

    for i in range(int(num)):
        col1, col2 = st.columns(2)
        with col1:
            sub = st.text_input(f"Subject {i+1}", key=f"s{i}")
        with col2:
            sc = st.number_input(f"Score {i+1}", 0, 100, key=f"sc{i}")

        subjects.append(sub)
        scores.append(sc)

    if st.button("Generate Schedule"):

        days = ["Mon","Tue","Wed","Thu","Fri"]
        slots = ["9-11","11-1","2-4","4-6"]

        schedule = []

        for sub, sc in zip(subjects, scores):
            if sub == "":
                continue

            sessions = 3 if sc < 50 else 2 if sc < 75 else 1

            for _ in range(sessions):
                schedule.append([
                    random.choice(days),
                    random.choice(slots),
                    sub
                ])

        df = pd.DataFrame(schedule, columns=["Day","Time","Subject"]).drop_duplicates()

        st.dataframe(df, use_container_width=True)

# -------------------------------
# LOGOUT
# -------------------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.rerun()

# -------------------------------
# NAVIGATION
# -------------------------------
if menu == "Login":
    login()
elif menu == "Register":
    register()
elif menu == "Dashboard":
    dashboard()
elif menu == "Attendance":
    attendance()
elif menu == "Study Planner":
    study_planner()
elif menu == "Logout":
    logout()