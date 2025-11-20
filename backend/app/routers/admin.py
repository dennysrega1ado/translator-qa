from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uuid
import hashlib
import subprocess
from app.database import get_db
from app import models
from app.auth import get_current_active_user
from app.s3_service import s3_service
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/admin", tags=["admin"])


# Pydantic models
class ValidatePrefixRequest(BaseModel):
    prefix: str


class ValidatePrefixResponse(BaseModel):
    valid: bool
    message: str
    has_en_folder: bool = False
    has_es_folder: bool = False
    sample_files: List[str] = []


class LoadTranslationsRequest(BaseModel):
    prefix: str
    description: str


class LoadTranslationsResponse(BaseModel):
    success: bool
    message: str
    execution_id: str = ""
    translations_loaded: int = 0
    prompts_created: int = 0


def is_admin(current_user: models.User = Depends(get_current_active_user)):
    """Dependency to verify user is admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/s3/validate-prefix", response_model=ValidatePrefixResponse)
async def validate_s3_prefix(
    request: ValidatePrefixRequest,
    current_user: models.User = Depends(is_admin)
):
    """
    Validate that S3 prefix exists and contains en/ and es/ folders
    """
    prefix = request.prefix.strip().rstrip('/')

    if not prefix:
        return ValidatePrefixResponse(
            valid=False,
            message="Prefix cannot be empty"
        )

    try:
        # List objects with the prefix
        objects = s3_service.list_objects(prefix=prefix)

        if not objects:
            return ValidatePrefixResponse(
                valid=False,
                message=f"No objects found at prefix: {prefix}"
            )

        # Check for en/ and es/ folders
        has_en = any(obj.startswith(f"{prefix}/en/") or obj.startswith("en/") for obj in objects)
        has_es = any(obj.startswith(f"{prefix}/es/") or obj.startswith("es/") for obj in objects)

        if not has_en or not has_es:
            missing = []
            if not has_en:
                missing.append("en/")
            if not has_es:
                missing.append("es/")

            return ValidatePrefixResponse(
                valid=False,
                message=f"Missing required folders: {', '.join(missing)}",
                has_en_folder=has_en,
                has_es_folder=has_es,
                sample_files=objects[:5]
            )

        # Get sample files
        sample_files = [obj for obj in objects[:10] if obj.endswith('.json')]

        return ValidatePrefixResponse(
            valid=True,
            message=f"Valid prefix with {len(objects)} objects found",
            has_en_folder=True,
            has_es_folder=True,
            sample_files=sample_files
        )

    except Exception as e:
        return ValidatePrefixResponse(
            valid=False,
            message=f"Error validating prefix: {str(e)}"
        )


@router.post("/s3/load-translations", response_model=LoadTranslationsResponse)
async def load_translations_from_s3(
    request: LoadTranslationsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(is_admin)
):
    """
    Load translations from S3 prefix into database using load_from_s3.py script
    Validates prefix first, then executes the script
    """
    prefix = request.prefix.strip().rstrip('/')

    if not prefix:
        raise HTTPException(status_code=400, detail="Prefix cannot be empty")

    try:
        # First, validate the prefix
        objects = s3_service.list_objects(prefix=prefix)

        if not objects:
            raise HTTPException(
                status_code=400,
                detail=f"No objects found at prefix: {prefix}"
            )

        # Check for en/ and es/ folders
        has_en = any(obj.startswith(f"{prefix}/en/") or obj.startswith("en/") for obj in objects)
        has_es = any(obj.startswith(f"{prefix}/es/") or obj.startswith("es/") for obj in objects)

        if not has_en or not has_es:
            missing = []
            if not has_en:
                missing.append("en/")
            if not has_es:
                missing.append("es/")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required folders: {', '.join(missing)}"
            )

        # Generate execution_id from prefix + description to check for duplicates
        combined = f"{prefix}|{request.description}"
        combined_hash = hashlib.md5(combined.encode()).hexdigest()
        execution_id = str(uuid.UUID(combined_hash))

        # Check if this execution_id already exists
        existing_count = db.query(models.Translation).filter(
            models.Translation.execution_id == execution_id
        ).count()

        if existing_count > 0:
            return LoadTranslationsResponse(
                success=False,
                message=f"Translations from this prefix already loaded (execution_id: {execution_id})",
                execution_id=execution_id,
                translations_loaded=0
            )

        # Execute the load_from_s3.py script with the prefix and description
        result = subprocess.run(
            ['python', 'load_from_s3.py', prefix, request.description],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            # Parse output to extract counts
            output = result.stdout

            # Extract translations_loaded and prompts_created from output
            translations_loaded = 0
            prompts_created = 0

            for line in output.split('\n'):
                if 'Translations loaded:' in line:
                    translations_loaded = int(line.split(':')[-1].strip())
                elif 'Prompts created:' in line:
                    prompts_created = int(line.split(':')[-1].strip())

            return LoadTranslationsResponse(
                success=True,
                message=f"Successfully loaded {translations_loaded} translations",
                execution_id=execution_id,
                translations_loaded=translations_loaded,
                prompts_created=prompts_created
            )
        else:
            error_msg = result.stderr or result.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Error loading translations: {error_msg}"
            )

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Operation timed out (max 5 minutes)")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading translations: {str(e)}")


@router.get("/s3/bucket-info")
async def get_bucket_info(current_user: models.User = Depends(is_admin)):
    """
    Get S3 bucket configuration info
    """
    return {
        "storage_backend": settings.STORAGE_BACKEND,
        "bucket": settings.AWS_S3_BUCKET if settings.STORAGE_BACKEND == "s3" else settings.MINIO_BUCKET,
        "region": settings.AWS_REGION if settings.STORAGE_BACKEND == "s3" else None,
        "prefix": settings.AWS_S3_PREFIX if settings.STORAGE_BACKEND == "s3" else None
    }


class CleanTablesResponse(BaseModel):
    success: bool
    message: str
    tables_cleaned: List[str] = []


@router.post("/clean-tables", response_model=CleanTablesResponse)
async def clean_database_tables(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(is_admin)
):
    """
    Clean all data from prompts, translations, and manual_scores tables.
    This is a destructive operation that cannot be undone.
    """
    try:
        # Execute the clean_tables.py script with auto-confirmation
        # We use echo "yes" to automatically confirm the operation
        result = subprocess.run(
            'echo "yes" | python clean_tables.py',
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Parse the output to confirm success
            if "SUCCESS" in result.stdout:
                return CleanTablesResponse(
                    success=True,
                    message="All tables have been cleaned successfully",
                    tables_cleaned=["manual_scores", "translations", "prompts"]
                )
            else:
                return CleanTablesResponse(
                    success=False,
                    message=f"Unexpected output: {result.stdout}"
                )
        else:
            return CleanTablesResponse(
                success=False,
                message=f"Error cleaning tables: {result.stderr}"
            )

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Operation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing clean operation: {str(e)}")
