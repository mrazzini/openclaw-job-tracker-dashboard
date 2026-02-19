from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

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
def get_stats(db: Session = None):
    if db is None:
        db = SessionLocal()
    try:
        found = db.query(Job).filter(Job.status == "found").count()
        applied = db.query(Job).filter(Job.status == "applied").count()
        interview = db.query(Job).filter(Job.status == "interview").count()
        rejected = db.query(Job).filter(Job.status == "rejected").count()
        return DashboardStats(found=found, applied=applied, interview=interview, rejected=rejected)
    finally:
        db.close()

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
