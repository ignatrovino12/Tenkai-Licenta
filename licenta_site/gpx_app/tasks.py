from celery import shared_task
from google.cloud import storage
from django.conf import settings
import exiftool
import os
from django.core.files.temp import NamedTemporaryFile


@shared_task
def process_and_upload_gpx(username, user_id , mp4_file_name):
    try:

        # exiftool_path = os.path.join(settings.BASE_DIR, 'video_data/exiftool.exe')
        gpx_fmt_path = os.path.join(settings.BASE_DIR, 'video_data/gpx.fmt')

        storage_client = storage.Client()
        bucket_name = "bucket-licenta-rovin"

        if mp4_file_name.endswith('.MP4'):
            mp4_file_name = mp4_file_name.rsplit('.', 1)[0] + '.mp4'
        
        video_blob= storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{mp4_file_name}')

        temp_mp4_file = NamedTemporaryFile(suffix='.mp4')

        video_blob.download_to_file(temp_mp4_file)   

        temp_mp4_file.flush()

        # convert to gpx with exiftool
        with exiftool.ExifTool() as et:
            print(et.executable)
            gpx_output = et.execute(
                '-p', gpx_fmt_path,
                '-ee3', temp_mp4_file.name,
            )

        print("Exiftool command executed successfully")
        temp_mp4_file.close()

        if gpx_output:
            gpx_name = mp4_file_name.rsplit('.', 1)[0]

            gpx_blob_name = f'uploads/{user_id}/{gpx_name}.gpx'
            blob = storage_client.bucket(bucket_name).blob(gpx_blob_name)
            blob.upload_from_string(gpx_output, content_type='application/gpx+xml')

    except Exception as e:

        print(f"Error processing and uploading GPX: {str(e)}")
        return None
    
