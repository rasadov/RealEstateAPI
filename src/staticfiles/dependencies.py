from src.staticfiles.manager import LocalStaticFilesManager

def get_static_files_manager() -> LocalStaticFilesManager:
    """Dependency injector for static files manager"""
    return LocalStaticFilesManager()
