import streamlit as st
import sqlite3
from datetime import datetime
from pathlib import Path

# Config - mobile friendly
st.set_page_config(
    page_title="Ambros Job Tracker",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database
DB_PATH = Path(__file__).parent / "job_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        level TEXT,
        category TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        company TEXT,
        url TEXT,
        score INTEGER,
        status TEXT DEFAULT 'found',
        requirements TEXT,
        has_early_applicant INTEGER DEFAULT 0,
        source TEXT,
        found_at TEXT,
        applied_at TEXT,
        notes TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cvs (
        id INTEGER PRIMARY KEY,
        name TEXT,
        version TEXT,
        content TEXT,
        updated_at TEXT
    )''')
    
    conn.commit()
    conn.close()

def load_skills():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, level, category FROM skills")
    skills = c.fetchall()
    conn.close()
    return [{"name": s[0], "level": s[1], "category": s[2]} for s in skills]

def load_jobs(status_filter=None):
    conn = sqlite3.connect(DB_PATH)
    if status_filter and status_filter != "All":
        c = conn.cursor()
        c.execute("SELECT * FROM jobs WHERE status = ? ORDER BY found_at DESC", (status_filter,))
    else:
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY found_at DESC")
    jobs = c.fetchall()
    conn.close()
    return jobs

def get_status_counts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
    counts = dict(c.fetchall())
    conn.close()
    return counts

def add_job(title, company, url, score, requirements="", has_early_applicant=0, source="LinkedIn"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO jobs (title, company, url, score, requirements, has_early_applicant, source, found_at, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'found')""",
              (title, company, url, score, requirements, has_early_applicant, source, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_job_status(job_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    applied_at = datetime.now().isoformat() if new_status == "applied" else None
    c.execute("UPDATE jobs SET status = ?, applied_at = ? WHERE id = ?", (new_status, applied_at, job_id))
    conn.commit()
    conn.close()

# Initialize
init_db()

# Sidebar
st.sidebar.title("🦅 Ambros")
st.sidebar.markdown("---")

# Page navigation
page = st.sidebar.radio("Menu", ["Dashboard", "Jobs", "Skills", "CVs"])

# Load data
skills = load_skills()
status_counts = get_status_counts()

if page == "Dashboard":
    st.title("📊 Dashboard")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Found", status_counts.get("found", 0))
    with col2:
        st.metric("Applied", status_counts.get("applied", 0))
    with col3:
        st.metric("Interview", status_counts.get("interview", 0))
    with col4:
        st.metric("Rejected", status_counts.get("rejected", 0))
    
    st.divider()
    
    # Skills
    st.subheader("🛠️ Your Skills")
    if skills:
        cats = {}
        for s in skills:
            c = s["category"] or "Other"
            if c not in cats: cats[c] = []
            cats[c].append(f"{s['name']} ({s['level']})")
        for cat, lst in cats.items():
            st.write(f"**{cat}:** {', '.join(lst)}")
    else:
        st.info("Add skills in the Skills tab")
    
    st.divider()
    
    # Recent
    st.subheader("📋 Recent Jobs")
    jobs = load_jobs()
    for job in jobs[:5]:
        emoji = {"found": "🆕", "applied": "📤", "interview": "🎤", "rejected": "❌", "offer": "🎉"}.get(job[5], "📋")
        st.write(f"{emoji} **{job[1]}** @ {job[2]} — Score: {job[4]}")

elif page == "Jobs":
    st.title("💼 Jobs")
    
    filter_status = st.selectbox("Status", ["All", "found", "applied", "interview", "rejected", "offer"])
    jobs = load_jobs(filter_status)
    
    st.write(f"Showing {len(jobs)} jobs")
    
    for job in jobs:
        with st.expander(f"{job[1]} @ {job[2]} (Score: {job[4]})"):
            st.write(f"**Status:** {job[5]}")
            st.write(f"[Open in LinkedIn]({job[3]})")
            st.write(f"**Requirements:** {job[6]}")
            st.write(f"**Early Applicant:** {'✅' if job[7] else '❌'}")
            
            # Status update buttons
            new_status = st.selectbox("Update status", 
                                     ["found", "applied", "interview", "rejected", "offer"],
                                     index=["found", "applied", "interview", "rejected", "offer"].index(job[5]) if job[5] in ["found", "applied", "interview", "rejected", "offer"] else 0,
                                     key=f"status_{job[0]}")
            if new_status != job[5]:
                update_job_status(job[0], new_status)
                st.rerun()

elif page == "Skills":
    st.title("🛠️ Skills")
    
    with st.form("add_skill"):
        c1, c2, c3 = st.columns(3)
        new_skill = c1.text_input("Skill")
        level = c2.selectbox("Level", ["Expert", "Strong", "Working", "Learning", "None"])
        category = c3.selectbox("Category", ["Languages", "ML/AI", "Data", "DevOps", "Tools", "Other"])
        if st.form_submit_button("Add"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO skills (name, level, category) VALUES (?, ?, ?)", (new_skill, level, category))
                conn.commit()
                st.success("Added!")
            except:
                st.error("Already exists")
            conn.close()
            st.rerun()
    
    st.divider()
    
    # Display
    for s in skills:
        st.write(f"• **{s['name']}** — {s['level']} ({s['category']})")

elif page == "CVs":
    st.title("📄 CVs")
    
    # JSON Import/Export for persistence
    st.subheader("💾 Data Backup")
    
    col1, col2 = st.columns(2)
    
    # Export
    with col1:
        if st.button("📤 Export All Data"):
            import json
            data = {
                "skills": load_skills(),
                "jobs": [dict(zip(["id", "title", "company", "url", "score", "status", "requirements", "has_early_applicant", "source", "found_at", "applied_at", "notes"], job)) 
                        for job in load_jobs()],
                "exported_at": datetime.now().isoformat()
            }
            st.download_button("⬇️ Download JSON", json.dumps(data, indent=2), "ambros_job_tracker.json", "application/json")
    
    # Import
    with col2:
        uploaded = st.file_uploader("📥 Import Data", type="json")
        if uploaded:
            import json
            data = json.load(uploaded)
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Import skills
            if "skills" in data:
                for s in data["skills"]:
                    try:
                        c.execute("INSERT OR REPLACE INTO skills (name, level, category) VALUES (?, ?, ?)", 
                                 (s["name"], s["level"], s.get("category", "Other")))
                    except:
                        pass
            
            # Import jobs
            if "jobs" in data:
                for j in data["jobs"]:
                    try:
                        c.execute("""INSERT OR REPLACE INTO jobs (title, company, url, score, status, requirements, has_early_applicant, source, found_at, applied_at, notes)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (j.get("title"), j.get("company"), j.get("url"), j.get("score", 0), j.get("status", "found"),
                                  j.get("requirements", ""), j.get("has_early_applicant", 0), j.get("source", "LinkedIn"),
                                  j.get("found_at", datetime.now().isoformat()), j.get("applied_at"), j.get("notes", "")))
                    except:
                        pass
            
            conn.commit()
            conn.close()
            st.success("Data imported! Refresh to see.")
            st.rerun()
    
    st.divider()
    st.info("💡 Export your data before redeploying. Import the JSON file after each deployment to keep your data.")
