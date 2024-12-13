from fastapi import HTTPException


class PropertyNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Property not found",
        )

class PropertyImageNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Property image not found",
        )

class PropertyImagesLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Property images limit exceeded",
        )

class PropertyImageUploadError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Property image upload error",
        )

class ListingNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Listing not found",
        )

class ListingImageNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Listing image not found",
        )

class ListingImagesLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Listing images limit exceeded",
        )
