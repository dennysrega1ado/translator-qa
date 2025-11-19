from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://translator_user:translator_pass@postgres:5432/translator_qa"

    # Storage Backend
    STORAGE_BACKEND: str = "minio"  # Options: "minio" or "s3"

    # MinIO Configuration
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "translations"
    MINIO_SECURE: bool = False

    # AWS S3 Configuration
    AWS_S3_BUCKET: str = "pangea-data-dev-bedrock-datasets"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_PREFIX: str = ""
    AWS_PROFILE: str = ""  # For AWS SSO profiles (e.g., "sso-ro-data-dev")

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()
