from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: bool = False


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Prompt Schemas
class PromptBase(BaseModel):
    prompt_id: str
    name: str
    description: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class Prompt(PromptBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Translation Schemas
class TranslationBase(BaseModel):
    execution_id: str
    original_content: str
    translated_content: str
    source_language: str
    target_language: str


class TranslationCreate(TranslationBase):
    prompt_id: int
    automated_coherence: Optional[float] = None
    automated_fidelity: Optional[float] = None
    automated_naturalness: Optional[float] = None
    automated_overall: Optional[float] = None
    s3_insights_path: Optional[str] = None
    s3_automated_qa_path: Optional[str] = None


class Translation(TranslationBase):
    id: int
    prompt_id: int
    automated_coherence: Optional[float]
    automated_fidelity: Optional[float]
    automated_naturalness: Optional[float]
    automated_overall: Optional[float]
    s3_insights_path: Optional[str] = None
    s3_automated_qa_path: Optional[str] = None
    created_at: datetime
    prompt: Prompt

    class Config:
        from_attributes = True


# Manual Score Schemas
class ManualScoreBase(BaseModel):
    coherence: Optional[float] = Field(None, ge=0, le=1)
    fidelity: Optional[float] = Field(None, ge=0, le=1)
    naturalness: Optional[float] = Field(None, ge=0, le=1)
    overall: Optional[float] = Field(None, ge=0, le=1)
    notes: Optional[str] = None


class ManualScoreCreate(ManualScoreBase):
    translation_id: int


class ManualScoreUpdate(ManualScoreBase):
    pass


class ManualScore(ManualScoreBase):
    id: int
    translation_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TranslationWithScores(Translation):
    manual_score: Optional[ManualScore] = None


# Reporting Schemas
class ReportFilter(BaseModel):
    execution_id: Optional[str] = None
    prompt_id: Optional[int] = None
    manual_only: bool = False


class ExecutionReport(BaseModel):
    execution_id: str
    prompt_id: int
    prompt_name: str
    total_translations: int
    translations_with_manual_scores: int
    manual_score_percentage: float
    avg_automated_coherence: Optional[float]
    avg_automated_fidelity: Optional[float]
    avg_automated_naturalness: Optional[float]
    avg_automated_overall: Optional[float]
    avg_manual_coherence: Optional[float]
    avg_manual_fidelity: Optional[float]
    avg_manual_naturalness: Optional[float]
    avg_manual_overall: Optional[float]
    avg_combined_coherence: Optional[float]
    avg_combined_fidelity: Optional[float]
    avg_combined_naturalness: Optional[float]
    avg_combined_overall: Optional[float]
