from celery import Celery
from sqlalchemy.orm import Session

from src.background_tasks.db_celery import get_sync_db_session
from src.staticfiles.dependencies import get_static_files_manager
from src.property.models import Property, PropertyImage

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def delete_property(id: int):
    db: Session = get_sync_db_session()
    property: Property = db.query(Property).get(id)
    if property is None:
        return 
    static_files_manager = get_static_files_manager()
    for image in property.images:
        static_files_manager.delete(image.path)
    db.query(PropertyImage).filter(PropertyImage.property_id == id).delete()
    db.delete(property)
    db.commit()
    db.close()
