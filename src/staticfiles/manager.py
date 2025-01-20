import os, io, uuid, logging
from urllib.parse import urlparse
from typing import Optional
from abc import ABC, abstractmethod

import boto3
from PIL import Image
import boto3.s3
from fastapi import UploadFile

import src.staticfiles.exceptions as exceptions
from src.config import S3Settings
from src.staticfiles.utils import (generate_unique_filename, validate_file, process_image)

class BaseStaticFilesManager(ABC):
    """Base static files service"""

    @abstractmethod
    def __init__(self):
        """Initialize service"""
        ...

    @abstractmethod
    def get(self, file_path: str) -> Optional[bytes]:
        """Get file"""
        ...

    @abstractmethod
    async def upload(self, file: UploadFile, path: str) -> str:
        """Upload file"""
        ...

    @abstractmethod
    async def delete(self, file_path: str) -> None:
        """Delete file"""
        ...

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
            unique_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(
                self.STATIC_FILES_DIR,
                unique_filename
                )
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            return file_path
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e
    
    def delete(self, file_path: str) -> None:
        """Delete file"""
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise e

class S3StaticFilesManager(S3Settings, BaseStaticFilesManager):
    """S3 static files service with file size, type limitations, and image processing"""
    MAX_FILE_SIZE_MB: int = 100
    MAX_IMAGE_SIZE_PX: tuple[int, int] = (4000, 4000)
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"}

    def __init__(self):
        super().__init__()
        self.s3_client = boto3.client(
            "s3",
            region_name=self.AWS_REGION,
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )

    def get(self, file_path: str) -> Optional[bytes]:
        """Get file from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.AWS_BUCKET_NAME,
                Key=file_path,
                )
            return response["Body"].read()
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            raise exceptions.FileUploadError(f"Error getting file from S3: {e}")

    async def upload(self, file: UploadFile, path: str) -> str:
        """Upload file to S3, ensuring unique filenames and applying validation/processing
        
        returns: S3 URL of the uploaded file
        """
        validate_file(file, self.MAX_FILE_SIZE_MB, self.ALLOWED_IMAGE_TYPES)
        file = await process_image(file, self.MAX_IMAGE_SIZE_PX)

        unique_filename = generate_unique_filename(file.filename)
        file_path = f"uploads/{path}/{unique_filename}"
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.AWS_BUCKET_NAME,
                file_path,
                )
            return "https://{}.s3.{}.amazonaws.com/{}".format(
                self.AWS_BUCKET_NAME, self.AWS_REGION, file_path
            )
        except Exception as e:
            raise exceptions.FileUploadError(f"Error uploading file to S3: {e}")

    def delete(self, image_url: str) -> None:
        """Delete file from S3"""
        try:
            parsed_url = urlparse(image_url)
            file_path = parsed_url.path.lstrip('/')

            response = self.s3_client.delete_object(
                Bucket=self.AWS_BUCKET_NAME,
                Key=file_path,
                )
            print(response)
            print(f"Deleted {file_path} from S3")
        except Exception as e:
            raise exceptions.FileDeleteError(f"Error deleting file from S3: {e}")
