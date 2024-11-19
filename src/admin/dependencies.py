from src.admin.service import AdminService

def get_admin_service() -> AdminService:
    """Get admin service."""
    return AdminService()