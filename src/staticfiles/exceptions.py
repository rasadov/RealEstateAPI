from fastapi import HTTPException

class FileTooLarge(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="File too large")

class UnsupportedFileType(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Unsupported file type")

class ImageProcessingError(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail="Error processing image")

class FileUploadError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class FileDeleteError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)
