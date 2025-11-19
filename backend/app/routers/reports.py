from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/", response_model=List[schemas.ExecutionReport])
async def get_reports(
    execution_id: Optional[str] = None,
    prompt_id: Optional[int] = None,
    manual_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Base query grouping by execution_id and prompt_id
    query = db.query(
        models.Translation.execution_id,
        models.Translation.prompt_id,
        models.Prompt.name.label('prompt_name'),
        func.count(models.Translation.id).label('total_translations'),
        func.count(func.distinct(models.ManualScore.translation_id)).label('translations_with_manual_scores'),

        # Automated scores averages
        func.avg(models.Translation.automated_coherence).label('avg_automated_coherence'),
        func.avg(models.Translation.automated_fidelity).label('avg_automated_fidelity'),
        func.avg(models.Translation.automated_naturalness).label('avg_automated_naturalness'),
        func.avg(models.Translation.automated_overall).label('avg_automated_overall'),

        # Manual scores averages
        func.avg(models.ManualScore.coherence).label('avg_manual_coherence'),
        func.avg(models.ManualScore.fidelity).label('avg_manual_fidelity'),
        func.avg(models.ManualScore.naturalness).label('avg_manual_naturalness'),
        func.avg(models.ManualScore.overall).label('avg_manual_overall'),
    ).join(
        models.Prompt,
        models.Translation.prompt_id == models.Prompt.id
    ).outerjoin(
        models.ManualScore,
        models.Translation.id == models.ManualScore.translation_id
    )

    # Apply filters
    if execution_id:
        query = query.filter(models.Translation.execution_id == execution_id)
    if prompt_id:
        query = query.filter(models.Translation.prompt_id == prompt_id)
    if manual_only:
        query = query.filter(models.ManualScore.id.isnot(None))

    # Group by
    query = query.group_by(
        models.Translation.execution_id,
        models.Translation.prompt_id,
        models.Prompt.name
    )

    results = query.all()

    reports = []
    for result in results:
        # Calculate combined averages (prefer manual, fallback to automated)
        total = result.total_translations
        manual_count = result.translations_with_manual_scores or 0

        def combine_scores(manual_avg, auto_avg):
            if manual_avg is not None and auto_avg is not None:
                # Weighted average based on coverage
                manual_weight = manual_count / total if total > 0 else 0
                auto_weight = (total - manual_count) / total if total > 0 else 0
                return (manual_avg * manual_weight) + (auto_avg * auto_weight)
            elif manual_avg is not None:
                return manual_avg
            elif auto_avg is not None:
                return auto_avg
            return None

        report = schemas.ExecutionReport(
            execution_id=result.execution_id,
            prompt_id=result.prompt_id,
            prompt_name=result.prompt_name,
            total_translations=total,
            translations_with_manual_scores=manual_count,
            manual_score_percentage=round((manual_count / total * 100) if total > 0 else 0, 2),

            avg_automated_coherence=round(result.avg_automated_coherence, 2) if result.avg_automated_coherence else None,
            avg_automated_fidelity=round(result.avg_automated_fidelity, 2) if result.avg_automated_fidelity else None,
            avg_automated_naturalness=round(result.avg_automated_naturalness, 2) if result.avg_automated_naturalness else None,
            avg_automated_overall=round(result.avg_automated_overall, 2) if result.avg_automated_overall else None,

            avg_manual_coherence=round(result.avg_manual_coherence, 2) if result.avg_manual_coherence else None,
            avg_manual_fidelity=round(result.avg_manual_fidelity, 2) if result.avg_manual_fidelity else None,
            avg_manual_naturalness=round(result.avg_manual_naturalness, 2) if result.avg_manual_naturalness else None,
            avg_manual_overall=round(result.avg_manual_overall, 2) if result.avg_manual_overall else None,

            avg_combined_coherence=round(combine_scores(result.avg_manual_coherence, result.avg_automated_coherence), 2) if combine_scores(result.avg_manual_coherence, result.avg_automated_coherence) else None,
            avg_combined_fidelity=round(combine_scores(result.avg_manual_fidelity, result.avg_automated_fidelity), 2) if combine_scores(result.avg_manual_fidelity, result.avg_automated_fidelity) else None,
            avg_combined_naturalness=round(combine_scores(result.avg_manual_naturalness, result.avg_automated_naturalness), 2) if combine_scores(result.avg_manual_naturalness, result.avg_automated_naturalness) else None,
            avg_combined_overall=round(combine_scores(result.avg_manual_overall, result.avg_automated_overall), 2) if combine_scores(result.avg_manual_overall, result.avg_automated_overall) else None,
        )
        reports.append(report)

    return reports
