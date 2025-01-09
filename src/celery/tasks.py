import os

from celery import Celery
from sqlalchemy.orm import Session

from src.celery.db_celery import get_sync_db_session
from src.staticfiles.dependencies import get_static_files_manager
from src.property.models import Property, PropertyImage
from src.listing.models import Listing, ListingImage


# Get the Redis URL from the environment variable
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Initialize the Celery app with the Redis URL
celery_app = Celery('tasks', broker=redis_url)

@celery_app.task
def queue_delete_property(id: int):
    db: Session = get_sync_db_session()
    property: Property = db.query(Property).get(id)
    static_files_manager = get_static_files_manager()

    if property is None:
        return
    for image in property.images:
        print(f"Deleting image: {image.image_url}")
        static_files_manager.delete(image.image_url)
    db.query(PropertyImage).filter(PropertyImage.property_id == id).delete()
    db.delete(property)
    db.commit()
    db.close()

@celery_app.task
def queue_delete_listing(id: int):
    db: Session = get_sync_db_session()
    listing: Listing = db.query(Listing).get(id)
    static_files_manager = get_static_files_manager()

    if listing is None:
        return
    for image in listing.images:
        print(f"Deleting image: {image.image_url}")
        static_files_manager.delete(image.image_url)
    db.query(ListingImage).filter(ListingImage.listing_id == id).delete()
    db.delete(listing)
    db.commit()
    db.close()
