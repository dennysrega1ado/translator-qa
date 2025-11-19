import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from io import BytesIO
from app.config import get_settings

settings = get_settings()


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def upload_json(self, object_name: str, data: Dict[Any, Any]) -> bool:
        pass

    @abstractmethod
    def get_json(self, object_name: str) -> Dict[Any, Any]:
        pass

    @abstractmethod
    def list_objects(self, prefix: str = "") -> list:
        pass


class MinIOBackend(StorageBackend):
    """MinIO storage backend"""

    def __init__(self):
        from minio import Minio
        from minio.error import S3Error

        self.S3Error = S3Error
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()
        print(f"Using MinIO backend: {settings.MINIO_ENDPOINT}/{self.bucket}")

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except self.S3Error as e:
            print(f"Error creating bucket: {e}")

    def upload_json(self, object_name: str, data: Dict[Any, Any]) -> bool:
        try:
            json_data = json.dumps(data, indent=2).encode('utf-8')
            self.client.put_object(
                self.bucket,
                object_name,
                BytesIO(json_data),
                len(json_data),
                content_type='application/json'
            )
            return True
        except self.S3Error as e:
            print(f"Error uploading to MinIO: {e}")
            return False

    def get_json(self, object_name: str) -> Dict[Any, Any]:
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = json.loads(response.read().decode('utf-8'))
            return data
        except self.S3Error as e:
            print(f"Error getting from MinIO: {e}")
            return {}
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

    def list_objects(self, prefix: str = ""):
        try:
            objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except self.S3Error as e:
            print(f"Error listing objects: {e}")
            return []


class AWSS3Backend(StorageBackend):
    """AWS S3 storage backend"""

    def __init__(self):
        import boto3
        from botocore.exceptions import ClientError

        self.ClientError = ClientError
        self.bucket = settings.AWS_S3_BUCKET
        self.prefix = settings.AWS_S3_PREFIX

        # Initialize boto3 client with different credential strategies
        if settings.AWS_PROFILE:
            # Use AWS SSO or named profile from ~/.aws/config
            session = boto3.Session(profile_name=settings.AWS_PROFILE)
            self.client = session.client('s3', region_name=settings.AWS_REGION)
            print(f"Using AWS S3 backend with profile '{settings.AWS_PROFILE}': s3://{self.bucket}/{self.prefix or ''}")
        elif settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            # Use explicit access keys
            self.client = boto3.client(
                's3',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            print(f"Using AWS S3 backend with access keys: s3://{self.bucket}/{self.prefix or ''}")
        else:
            # Use default credentials (IAM role, environment, or default profile)
            self.client = boto3.client('s3', region_name=settings.AWS_REGION)
            print(f"Using AWS S3 backend with default credentials: s3://{self.bucket}/{self.prefix or ''}")

    def _get_full_key(self, object_name: str) -> str:
        """Add prefix to object name if configured"""
        if self.prefix:
            return f"{self.prefix.rstrip('/')}/{object_name}"
        return object_name

    def upload_json(self, object_name: str, data: Dict[Any, Any]) -> bool:
        try:
            json_data = json.dumps(data, indent=2).encode('utf-8')
            full_key = self._get_full_key(object_name)
            self.client.put_object(
                Bucket=self.bucket,
                Key=full_key,
                Body=json_data,
                ContentType='application/json'
            )
            return True
        except self.ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False

    def get_json(self, object_name: str) -> Dict[Any, Any]:
        try:
            full_key = self._get_full_key(object_name)
            response = self.client.get_object(Bucket=self.bucket, Key=full_key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            return data
        except self.ClientError as e:
            print(f"Error getting from S3: {e}")
            return {}

    def list_objects(self, prefix: str = ""):
        try:
            full_prefix = self._get_full_key(prefix)
            objects = []
            paginator = self.client.get_paginator('list_objects_v2')

            for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        # Remove the configured prefix from the returned keys
                        if self.prefix and key.startswith(self.prefix):
                            key = key[len(self.prefix):].lstrip('/')
                        objects.append(key)

            return objects
        except self.ClientError as e:
            print(f"Error listing objects: {e}")
            return []


class S3Service:
    """Unified S3 service that switches between MinIO and AWS S3"""

    def __init__(self):
        backend_type = settings.STORAGE_BACKEND.lower()

        if backend_type == "s3":
            self.backend = AWSS3Backend()
        elif backend_type == "minio":
            self.backend = MinIOBackend()
        else:
            raise ValueError(f"Invalid STORAGE_BACKEND: {backend_type}. Must be 'minio' or 's3'")

    def upload_json(self, object_name: str, data: Dict[Any, Any]) -> bool:
        return self.backend.upload_json(object_name, data)

    def get_json(self, object_name: str) -> Dict[Any, Any]:
        return self.backend.get_json(object_name)

    def list_objects(self, prefix: str = "") -> list:
        return self.backend.list_objects(prefix)


# Global instance
s3_service = S3Service()
