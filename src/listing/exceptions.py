from fastapi import HTTPException


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
