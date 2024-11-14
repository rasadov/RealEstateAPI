import os
import uuid
from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import Optional


class BaseStaticFilesManager(ABC):
    """Base static files service"""

    @abstractmethod
    def get(self, file_path: str) -> Optional[bytes]:
        """Get file"""
        ...

    @abstractmethod
    def upload(self, file: UploadFile) -> str:
        """Upload file"""
        ...

    @abstractmethod
    def upload_static_file(self, file: UploadFile) -> str:
        """Upload static file"""
        ...

    @abstractmethod
    def delete(self, file_path: str) -> None:
        """Delete file"""
        ...

    def _generate_unique_filename(self, filename: str) -> str:
        """Generate a unique filename"""
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
        return unique_filename

class LocalStaticFilesManager(BaseStaticFilesManager):
    """Local static files service"""
    STATIC_FILES_DIR: str = "static_files"

    def __init__(self):
        os.makedirs(self.STATIC_FILES_DIR, exist_ok=True)

    def get(self, file_path: str) -> Optional[bytes]:
        """Get file"""
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def upload(self, file: UploadFile) -> str:
        """Upload file, ensuring unique filenames"""
        try:
            unique_filename = self._generate_unique_filename(file.filename)
            file_path = os.path.join(self.STATIC_FILES_DIR, unique_filename)
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            return file_path
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e

    def upload_static_file(self, file: UploadFile) -> str:
        """Upload static file with similar behavior"""
        return self.upload(file)

class S3StaticFilesManager(BaseStaticFilesManager):
    """S3 static files service"""
    AWS_BUCKET_NAME: str = "my-bucket"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    def __init__(self, AWS_ACCESS_KEY_ID: str, AWS_SECRET_ACCESS_KEY: str):
        self.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY

    # TO DO
