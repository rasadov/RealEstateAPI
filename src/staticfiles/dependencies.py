from src.staticfiles.manager import S3StaticFilesManager

def get_static_files_manager() -> S3StaticFilesManager:
    """Dependency injector for static files manager"""
    return S3StaticFilesManager()
