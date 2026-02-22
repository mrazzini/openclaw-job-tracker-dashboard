from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import json
import copy
import httpx

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ambros:ambros_secure_pass@localhost:5432/job_tracker")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    level = Column(String)  # Expert, Strong, Working, Learning, None
    category = Column(String)  # Languages, ML/AI, Data, DevOps, Tools, Other

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    url = Column(String)
    score = Column(Integer)
    status = Column(String, default="found")  # found, applied, interview, rejected, offer
    requirements = Column(Text, default="")
    has_early_applicant = Column(Boolean, default=False)
    source = Column(String, default="LinkedIn")
    found_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime, nullable=True)
    notes = Column(Text, default="")

class CV(Base):
    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    version = Column(String)
    content = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class SkillCreate(BaseModel):
    name: str
    level: str
    category: str

class SkillResponse(SkillCreate):
    id: int
    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    company: str
    url: str
    score: int
    requirements: str = ""
    has_early_applicant: bool = False
    source: str = "LinkedIn"

class JobUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class JobResponse(JobCreate):
    id: int
    status: str
    found_at: datetime
    applied_at: Optional[datetime] = None
    notes: str
    class Config:
        from_attributes = True

class CVCreate(BaseModel):
    name: str
    version: str
    content: str

class CVResponse(CVCreate):
    id: int
    updated_at: datetime
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    found: int
    applied: int
    interview: int
    rejected: int

# FastAPI app
app = FastAPI(title="Ambros Job Tracker API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
def root():
    return {"message": "Ambros Job Tracker API", "status": "running"}

@app.get("/api/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    found = db.query(Job).filter(Job.status == "found").count()
    applied = db.query(Job).filter(Job.status == "applied").count()
    interview = db.query(Job).filter(Job.status == "interview").count()
    rejected = db.query(Job).filter(Job.status == "rejected").count()
    return DashboardStats(found=found, applied=applied, interview=interview, rejected=rejected)

# Skills
@app.get("/api/skills", response_model=List[SkillResponse])
def get_skills(db=Depends(get_db)):
    return db.query(Skill).all()

@app.post("/api/skills", response_model=SkillResponse)
def create_skill(skill: SkillCreate, db=Depends(get_db)):
    db_skill = Skill(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@app.post("/api/skills/bulk")
def create_skills_bulk(skills: List[SkillCreate], db=Depends(get_db)):
    created = []
    for skill_data in skills:
        db_skill = Skill(**skill_data.model_dump())
        db.add(db_skill)
        created.append(db_skill)
    db.commit()
    return {"count": len(created), "message": f"Created {len(created)} skills"}

@app.delete("/api/skills/{skill_id}")
def delete_skill(skill_id: int, db=Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted"}

# Jobs
@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs(status: Optional[str] = None, db=Depends(get_db)):
    query = db.query(Job).order_by(Job.found_at.desc())
    if status and status != "All":
        query = query.filter(Job.status == status)
    return query.all()

@app.post("/api/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db=Depends(get_db)):
    db_job = Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.post("/api/jobs/bulk")
def create_jobs_bulk(jobs: List[JobCreate], db=Depends(get_db)):
    created = []
    for job_data in jobs:
        db_job = Job(**job_data.model_dump())
        db.add(db_job)
        created.append(db_job)
    db.commit()
    return {"count": len(created), "message": f"Created {len(created)} jobs"}

@app.patch("/api/jobs/{job_id}", response_model=JobResponse)
def update_job(job_id: int, update: JobUpdate, db=Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if update.status:
        job.status = update.status
        if update.status == "applied":
            job.applied_at = datetime.utcnow()
    if update.notes is not None:
        job.notes = update.notes
    db.commit()
    db.refresh(job)
    return job

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db=Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}

# CVs
@app.get("/api/cvs", response_model=List[CVResponse])
def get_cvs(db=Depends(get_db)):
    return db.query(CV).order_by(CV.updated_at.desc()).all()

@app.post("/api/cvs", response_model=CVResponse)
def create_cv(cv: CVCreate, db=Depends(get_db)):
    db_cv = CV(**cv.model_dump())
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)
    return db_cv

@app.delete("/api/cvs/{cv_id}")
def delete_cv(cv_id: int, db=Depends(get_db)):
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    db.delete(cv)
    db.commit()
    return {"message": "CV deleted"}

# Export/Import
@app.get("/api/export")
def export_data(db=Depends(get_db)):
    import json
    data = {
        "skills": [s.__dict__ for s in db.query(Skill).all()],
        "jobs": [{k: v for k, v in j.__dict__.items() if k != '_sa_instance_state'} for j in db.query(Job).all()],
        "cvs": [c.__dict__ for c in db.query(CV).all()],
        "exported_at": datetime.utcnow().isoformat()
    }
    return data

@app.post("/api/import")
def import_data(data: dict, db=Depends(get_db)):
    # Import skills
    for s in data.get("skills", []):
        skill = Skill(name=s.get("name"), level=s.get("level"), category=s.get("category"))
        db.add(skill)
    # Import jobs
    for j in data.get("jobs", []):
        job = Job(
            title=j.get("title"), company=j.get("company"), url=j.get("url"),
            score=j.get("score", 0), status=j.get("status", "found"),
            requirements=j.get("requirements", ""), has_early_applicant=j.get("has_early_applicant", False),
            source=j.get("source", "LinkedIn")
        )
        db.add(job)
    db.commit()
    return {"message": "Data imported successfully"}

# ============================================================
# CV Generation via Reactive Resume (rxresu.me) cloud API
# ============================================================

RXRESUME_API = "https://rxresu.me/api/openapi"
RXRESUME_API_KEY = os.getenv("RXRESUME_API_KEY", "")
MASTER_RESUME_ID = os.getenv("MASTER_RESUME_ID", "019bef9f-2538-77aa-8e23-02f23d5c9cc2")

def rxresume_headers():
    return {"x-api-key": RXRESUME_API_KEY, "Content-Type": "application/json"}

class CVGenerateRequest(BaseModel):
    job_id: int
    custom_summary: Optional[str] = None

@app.get("/api/cv/master")
async def get_master_resume():
    """Get the master resume from Reactive Resume."""
    if not RXRESUME_API_KEY:
        raise HTTPException(status_code=500, detail="RXRESUME_API_KEY not set")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{RXRESUME_API}/resumes/{MASTER_RESUME_ID}", headers=rxresume_headers())
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch master resume")
        return resp.json()

@app.get("/api/cv/resumes")
async def list_resumes():
    """List all resumes on Reactive Resume account."""
    if not RXRESUME_API_KEY:
        raise HTTPException(status_code=500, detail="RXRESUME_API_KEY not set")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{RXRESUME_API}/resumes", headers=rxresume_headers())
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to list resumes")
        return resp.json()

@app.post("/api/cv/generate")
async def generate_tailored_cv(req: CVGenerateRequest, db=Depends(get_db)):
    """
    Generate a tailored CV for a specific job.
    1. Fetches master resume from rxresu.me
    2. Duplicates it with a job-specific name
    3. Tailors skills and summary to match job requirements
    4. Returns the new resume ID and PDF export URL
    """
    if not RXRESUME_API_KEY:
        raise HTTPException(status_code=500, detail="RXRESUME_API_KEY not set")

    # Get the job
    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get user skills from dashboard DB
    user_skills = db.query(Skill).all()
    strong_skills = [s.name for s in user_skills if s.level in ("Expert", "Strong")]
    working_skills = [s.name for s in user_skills if s.level == "Working"]
    learning_skills = [s.name for s in user_skills if s.level == "Learning"]
    no_skills = [s.name for s in user_skills if s.level == "None"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Duplicate master resume
        slug = f"{job.company.lower().replace(' ', '-')}-{job.title.lower().replace(' ', '-')}"[:50]
        dup_resp = await client.post(
            f"{RXRESUME_API}/resumes/{MASTER_RESUME_ID}/duplicate",
            headers=rxresume_headers(),
            json={"name": f"{job.title} @ {job.company}", "slug": slug, "tags": ["tailored", job.company.lower()]}
        )
        if dup_resp.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Failed to duplicate resume: {dup_resp.text}")

        new_resume_id = dup_resp.json() if isinstance(dup_resp.json(), str) else dup_resp.json().get("id", "")

        # Step 2: Fetch the duplicated resume to get its full data
        get_resp = await client.get(
            f"{RXRESUME_API}/resumes/{new_resume_id}",
            headers=rxresume_headers()
        )
        if get_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch duplicated resume")

        resume_data = get_resp.json()["data"]

        # Step 3: Tailor the resume
        # Filter skills: emphasize strong/working, remove "None" level skills
        job_keywords = (job.title + " " + job.requirements).lower()

        # Tailor summary if custom provided, otherwise adjust for role
        if req.custom_summary:
            resume_data["summary"]["content"] = req.custom_summary
        else:
            base_summary = resume_data["summary"]["content"]
            role_context = f" Seeking a {job.title} position with focus on building production-grade AI systems."
            if "rag" in job_keywords or "llm" in job_keywords:
                role_context = f" Seeking a {job.title} role, bringing hands-on experience with RAG architectures, LLM integration, and document processing pipelines."
            elif "computer vision" in job_keywords or "cv" in job_keywords or "yolo" in job_keywords:
                role_context = f" Seeking a {job.title} role, bringing proven experience in computer vision systems, object detection pipelines, and safety data extraction."
            elif "data engineer" in job_keywords:
                role_context = f" Seeking a {job.title} role, with strong capabilities in ETL pipeline design, PostgreSQL, and end-to-end data system ownership."
            elif "agentic" in job_keywords or "agent" in job_keywords:
                role_context = f" Seeking a {job.title} role, with active experience building agentic AI systems and LLM orchestration workflows."
            resume_data["summary"]["content"] = base_summary.rstrip("</p>") + role_context + "</p>"

        # Step 4: Update the duplicated resume with tailored data
        update_resp = await client.put(
            f"{RXRESUME_API}/resumes/{new_resume_id}",
            headers=rxresume_headers(),
            json={"data": resume_data}
        )
        if update_resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to update resume: {update_resp.text}")

        # Step 5: Get PDF export URL
        pdf_url = f"{RXRESUME_API}/resumes/{new_resume_id}/export/pdf"

        # Save to dashboard CV vault
        cv_entry = CV(
            name=f"{job.title} @ {job.company}",
            version="v1.0",
            content=json.dumps({
                "rxresume_id": new_resume_id,
                "job_id": job.id,
                "pdf_url": pdf_url,
                "tailored_for": f"{job.title} @ {job.company}",
                "generated_at": datetime.utcnow().isoformat()
            })
        )
        db.add(cv_entry)
        db.commit()

        return {
            "resume_id": new_resume_id,
            "name": f"{job.title} @ {job.company}",
            "pdf_url": pdf_url,
            "message": f"Tailored CV generated for {job.title} @ {job.company}"
        }

@app.get("/api/cv/{resume_id}/pdf")
async def get_cv_pdf(resume_id: str):
    """Proxy PDF export from Reactive Resume."""
    if not RXRESUME_API_KEY:
        raise HTTPException(status_code=500, detail="RXRESUME_API_KEY not set")
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(
            f"{RXRESUME_API}/resumes/{resume_id}/export/pdf",
            headers=rxresume_headers()
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to export PDF")
        return StreamingResponse(
            iter([resp.content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cv-{resume_id}.pdf"}
        )

@app.delete("/api/cv/{resume_id}")
async def delete_generated_cv(resume_id: str):
    """Delete a generated CV from Reactive Resume."""
    if not RXRESUME_API_KEY:
        raise HTTPException(status_code=500, detail="RXRESUME_API_KEY not set")
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{RXRESUME_API}/resumes/{resume_id}",
            headers=rxresume_headers()
        )
        if resp.status_code not in (200, 204):
            raise HTTPException(status_code=resp.status_code, detail="Failed to delete resume")
        return {"message": "CV deleted from Reactive Resume"}
