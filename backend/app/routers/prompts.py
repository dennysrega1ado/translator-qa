from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("/", response_model=List[schemas.Prompt])
async def list_prompts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    prompts = db.query(models.Prompt).all()
    return prompts


@router.get("/{prompt_id}", response_model=schemas.Prompt)
async def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("/", response_model=schemas.Prompt)
async def create_prompt(
    prompt_data: schemas.PromptCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # Check if prompt_id already exists
    existing = db.query(models.Prompt).filter(
        models.Prompt.prompt_id == prompt_data.prompt_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Prompt with this prompt_id already exists"
        )

    db_prompt = models.Prompt(**prompt_data.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt
