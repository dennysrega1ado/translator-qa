from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routers import auth, translations, scores, reports, prompts
from app.init_db import init_database

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Translation QA API",
    description="API for managing translation quality assessments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(translations.router)
app.include_router(scores.router)
app.include_router(reports.router)
app.include_router(prompts.router)


@app.on_event("startup")
async def startup_event():
    # Initialize database with default admin user
    init_database()


@app.get("/")
async def root():
    return {
        "message": "Translation QA API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
