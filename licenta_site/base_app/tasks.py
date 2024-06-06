from celery import shared_task
from google.cloud import storage
from .models import UserProfile
import base64
import imghdr

ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png']

@shared_task
def update_picture_task(user_id, image):

    try:
        # upload to cloud storage
        storage_client = storage.Client()
        bucket_name = "bucket-licenta-rovin"
        
        _, base64_data = image.split(",", 1)
        image_bytes = base64.b64decode(base64_data)

        extension = imghdr.what(None, h=image_bytes)

        if extension is None:
            return False
        
        extension = extension.lower()

        if extension not in ALLOWED_IMAGE_FORMATS:
            return False
        content_type = f"image/{extension}"

        image_blob_name = f'images/{user_id}/ppicture.{extension}'
        blob = storage_client.bucket(bucket_name).blob(image_blob_name)
        blob.upload_from_string(image_bytes, content_type=content_type)

        return True

    except UserProfile.DoesNotExist:
        return False