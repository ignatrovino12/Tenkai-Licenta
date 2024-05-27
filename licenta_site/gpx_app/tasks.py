from celery import shared_task
from google.cloud import storage
from django.conf import settings
import exiftool
import os
from django.core.files.temp import NamedTemporaryFile


@shared_task
def process_and_upload_gpx(username, user_id , temp_mp4_file_path, gpx_name):
    try:

        exiftool_path = os.path.join(settings.BASE_DIR, 'video_data/exiftool.exe')
        gpx_fmt_path = os.path.join(settings.BASE_DIR, 'video_data/gpx.fmt')


        # convert to gpx with exiftool
        with exiftool.ExifTool(exiftool_path) as et:
            gpx_output = et.execute(
                '-p', gpx_fmt_path,
                '-ee', temp_mp4_file_path
            )

        print("Exiftool command executed successfully")

        return gpx_output
    except Exception as e:

        print(f"Error processing and uploading GPX: {str(e)}")
        return None