from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/translations", tags=["translations"])


@router.get("/", response_model=List[schemas.TranslationWithScores])
async def list_translations(
    execution_id: Optional[str] = None,
    prompt_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    query = db.query(models.Translation).options(
        joinedload(models.Translation.prompt),
        joinedload(models.Translation.manual_scores)
    )

    if execution_id:
        query = query.filter(models.Translation.execution_id == execution_id)
    if prompt_id:
        query = query.filter(models.Translation.prompt_id == prompt_id)

    translations = query.offset(skip).limit(limit).all()

    # Attach manual scores for current user
    result = []
    for translation in translations:
        trans_dict = schemas.Translation.model_validate(translation).model_dump()
        # Get current user's manual score if exists
        manual_score = db.query(models.ManualScore).filter(
            models.ManualScore.translation_id == translation.id,
            models.ManualScore.user_id == current_user.id
        ).first()
        trans_dict['manual_score'] = schemas.ManualScore.model_validate(manual_score) if manual_score else None
        result.append(trans_dict)

    return result


@router.get("/{translation_id}", response_model=schemas.TranslationWithScores)
async def get_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    translation = db.query(models.Translation).options(
        joinedload(models.Translation.prompt)
    ).filter(models.Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    trans_dict = schemas.Translation.model_validate(translation).model_dump()

    # Get current user's manual score if exists
    manual_score = db.query(models.ManualScore).filter(
        models.ManualScore.translation_id == translation_id,
        models.ManualScore.user_id == current_user.id
    ).first()

    trans_dict['manual_score'] = schemas.ManualScore.model_validate(manual_score) if manual_score else None

    return trans_dict


@router.get("/executions/list")
async def list_executions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    executions = db.query(
        models.Translation.execution_id,
        func.count(models.Translation.id).label('count'),
        func.max(models.Translation.created_at).label('latest_date'),
        func.max(models.Translation.execution_description).label('description')
    ).group_by(
        models.Translation.execution_id
    ).order_by(
        func.max(models.Translation.created_at).desc()
    ).all()

    return [{
        "execution_id": e.execution_id,
        "count": e.count,
        "latest_date": e.latest_date.isoformat() if e.latest_date else None,
        "description": e.description
    } for e in executions]


@router.post("/", response_model=schemas.Translation)
async def create_translation(
    translation: schemas.TranslationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_translation = models.Translation(**translation.model_dump())
    db.add(db_translation)
    db.commit()
    db.refresh(db_translation)
    return db_translation
