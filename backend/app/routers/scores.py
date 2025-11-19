from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/scores", tags=["scores"])


@router.post("/", response_model=schemas.ManualScore)
async def create_manual_score(
    score_data: schemas.ManualScoreCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Check if translation exists
    translation = db.query(models.Translation).filter(
        models.Translation.id == score_data.translation_id
    ).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    # Check if user already scored this translation
    existing_score = db.query(models.ManualScore).filter(
        models.ManualScore.translation_id == score_data.translation_id,
        models.ManualScore.user_id == current_user.id
    ).first()

    if existing_score:
        raise HTTPException(
            status_code=400,
            detail="Score already exists. Use PUT to update."
        )

    # Create new score
    db_score = models.ManualScore(
        **score_data.model_dump(),
        user_id=current_user.id
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.put("/{score_id}", response_model=schemas.ManualScore)
async def update_manual_score(
    score_id: int,
    score_data: schemas.ManualScoreUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Get existing score
    db_score = db.query(models.ManualScore).filter(
        models.ManualScore.id == score_id,
        models.ManualScore.user_id == current_user.id
    ).first()

    if not db_score:
        raise HTTPException(
            status_code=404,
            detail="Score not found or you don't have permission to edit it"
        )

    # Update score
    update_data = score_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_score, key, value)

    db.commit()
    db.refresh(db_score)
    return db_score


@router.get("/{score_id}", response_model=schemas.ManualScore)
async def get_manual_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    score = db.query(models.ManualScore).filter(
        models.ManualScore.id == score_id
    ).first()

    if not score:
        raise HTTPException(status_code=404, detail="Score not found")

    return score


@router.delete("/{score_id}")
async def delete_manual_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    score = db.query(models.ManualScore).filter(
        models.ManualScore.id == score_id,
        models.ManualScore.user_id == current_user.id
    ).first()

    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found or you don't have permission to delete it"
        )

    db.delete(score)
    db.commit()
    return {"message": "Score deleted successfully"}
