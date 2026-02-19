# Ambros Job Tracker 🦅

AI-powered job search assistant for ML/AI engineers. Built with Streamlit.

## What is this?

A personal job tracking dashboard that:
- Tracks your skills matrix
- Stores jobs found during automated LinkedIn scans
- Manages application status
- Provides mobile-friendly access via Streamlit Cloud

## Tech Stack

- **Frontend:** Streamlit (Python)
- **Database:** SQLite (embedded)
- **Deployment:** Streamlit Cloud

## Features

- 📊 Dashboard with application 💼 Job bank with scoring and status tracking
 stats
-- 🛠️ Skills matrix (your tech stack)
- 📄 CV vault

## Deployment

```bash
# Local
streamlit run app.py

# Deploy to Streamlit Cloud
# Connect GitHub repo to share.streamlit.io
```

## Data Persistence (Important!)

Streamlit Cloud has ephemeral storage — the database resets on each deploy.

**Workflow:**
1. Before redeploying: Go to CVs tab → click "📤 Export All Data"
2. After deploying: Go to CVs tab → upload your JSON file
3. Your jobs and skills will be restored

Or commit `ambros_job_tracker.json` to your repo and import after each deploy.

## Customization

Edit `app.py` to add:
- More skills
- Different scoring weights
- Additional filters

## Author

Built by Ambros for Mattia Razzini — ML/AI Engineer transition from Chemical R&D.
