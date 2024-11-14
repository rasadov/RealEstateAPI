import os, io, uuid
from typing import Optional
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import UploadFile
from PIL import Image

import src.staticfiles.exceptions as exceptions
from src.config import S3Settings

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

class S3StaticFilesManager(S3Settings, BaseStaticFilesManager):
    """S3 static files service with file size, type limitations, and image processing"""
    MAX_FILE_SIZE_MB: int = 5
    MAX_IMAGE_SIZE_PX: tuple[int, int] = (1000, 1000)
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}

    def __init__(self):
        super().__init__()
        self.s3_client = boto3.client(
            "s3",
            region_name=self.AWS_REGION,
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file size and type"""
        # Check file size
        file.file.seek(0, 2)  # Move file pointer to end
        file_size_mb = file.file.tell() / (1024 * 1024)
        file.file.seek(0)  # Reset file pointer to start

        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise exceptions.FileTooLarge

        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise exceptions.UnsupportedFileType

    def _process_image(self, file: UploadFile) -> UploadFile:
        """Process image if needed (e.g., resize or convert format)"""
        if file.content_type.startswith("image/"):
            try:
                image = Image.open(file.file)
                image.thumbnail(self.MAX_IMAGE_SIZE_PX)

                buffer = io.BytesIO()
                image.save(buffer, format="WEBP", quality=85)
                buffer.seek(0)

                file = UploadFile(
                    filename=file.filename.rsplit('.', 1)[0] + ".webp",
                    file=buffer,
                    content_type="image/webp"
                )
            except Exception:
                raise exceptions.ImageProcessingError
        return file

    def get(self, file_path: str) -> Optional[bytes]:
        """Get file from S3        
        """
        try:
            response = self.s3_client.get_object(Bucket=self.AWS_BUCKET_NAME, Key=file_path)
            return response["Body"].read()
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            raise exceptions.FileUploadError(f"Error getting file from S3: {e}")

    def upload(self, file: UploadFile) -> str:
        """Upload file to S3, ensuring unique filenames and applying validation/processing
        
        returns: S3 URL of the uploaded file
        """
        self._validate_file(file)
        file = self._process_image(file)

        unique_filename = self._generate_unique_filename(file.filename)
        file_path = f"uploads/{unique_filename}"
        try:
            self.s3_client.upload_fileobj(file.file, self.AWS_BUCKET_NAME, file_path)
            return "https://%s.s3.%s.amazonaws.com/%s".format(
                self.AWS_BUCKET_NAME, self.AWS_REGION, file_path
            )
        except Exception as e:
            raise exceptions.FileUploadError(f"Error uploading file to S3: {e}")

    def upload_static_file(self, file: UploadFile) -> str:
        """Upload static file to S3 with similar behavior"""
        return self.upload(file)

    def delete(self, file_path: str) -> None:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.AWS_BUCKET_NAME, Key=file_path)
            print(f"Deleted {file_path} from S3")
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            raise e
