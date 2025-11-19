from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    manual_scores = relationship("ManualScore", back_populates="user")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    translations = relationship("Translation", back_populates="prompt")


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), index=True, nullable=False)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)

    # Content
    original_content = Column(Text, nullable=False)
    translated_content = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)

    # Automated scores
    automated_coherence = Column(Float)
    automated_fidelity = Column(Float)
    automated_naturalness = Column(Float)
    automated_overall = Column(Float)

    # S3 references
    s3_insights_path = Column(String(500))
    s3_automated_qa_path = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prompt = relationship("Prompt", back_populates="translations")
    manual_scores = relationship("ManualScore", back_populates="translation")


class ManualScore(Base):
    __tablename__ = "manual_scores"

    id = Column(Integer, primary_key=True, index=True)
    translation_id = Column(Integer, ForeignKey("translations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Manual scores
    coherence = Column(Float)
    fidelity = Column(Float)
    naturalness = Column(Float)
    overall = Column(Float)

    # Metadata
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    translation = relationship("Translation", back_populates="manual_scores")
    user = relationship("User", back_populates="manual_scores")
