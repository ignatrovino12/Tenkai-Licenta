from django.shortcuts import render, redirect
from django.http import JsonResponse
from google.cloud import storage
import json
from .models import Video
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import gpxpy
from django.utils import timezone
from celery.result import AsyncResult
from django.core.files.temp import NamedTemporaryFile
import exiftool
import os
from django.conf import settings
from .tasks import process_and_upload_gpx


bucket_name="bucket-licenta-rovin"

def get_user_id_from_username(username):
    try:
        user = User.objects.get(username=username)
        return user.id
    except User.DoesNotExist:
        return None

def generate_signed_url_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            video_name = data.get('video_name')
            user_id = get_user_id_from_username(username)
            
            if not (video_name.endswith('.mp4') or video_name.endswith('.MP4')):
                return JsonResponse({'success': False, 'message': 'File provided is not an mp4'}, status=404)

            if video_name.endswith('.MP4'):
                video_name = video_name.rsplit('.', 1)[0] + '.mp4'

            if user_id is None:
                return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
            
            if Video.objects.filter(user_profile__user_id=user_id, video_name=video_name).exists():
                return JsonResponse({'success': False, 'message': 'Video name already associated with the user'}, status=404)

            # database creation
            video = Video.objects.create(video_name=video_name, user_profile_id=user_id, timestamp=timezone.now())

            # generate google cloud link
            storage_client = storage.Client()
            bucket_name="bucket-licenta-rovin"

            blob = storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{video_name}')
            current_datetime = datetime.now()
            expiration_time = current_datetime + timedelta(minutes=10)
            signed_url = blob.generate_signed_url(
                version='v4',
                expiration=expiration_time,
                method='PUT',
                content_type='video/mp4'
            )

            return JsonResponse({'success': True, 'signed_url': signed_url}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

    
def convert_gpx(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            # print("NUMELE ESTE")
            # print(username)
            mp4_file_name = request.POST.get('mp4_file')
            user_id = get_user_id_from_username(username)

            if not mp4_file_name:
                return JsonResponse({'success': False, 'message': 'No MP4 file provided'}, status=400)

            # save mp4 to temporary file 
            # temp_mp4_file = NamedTemporaryFile(suffix='.mp4')
            # for chunk in mp4_file.chunks():
            #     temp_mp4_file.write(chunk)
            # temp_mp4_file_path = temp_mp4_file.name
            
            process_and_upload_gpx.delay(username, user_id,  mp4_file_name)


            # if gpx_output:
            #     storage_client = storage.Client()
            #     bucket_name="bucket-licenta-rovin"

            #     gpx_blob_name = f'uploads/{user_id}/{gpx_name}.gpx'
            #     blob = storage_client.bucket(bucket_name).blob(gpx_blob_name)
            #     blob.upload_from_string(gpx_output, content_type='application/gpx+xml')

            return JsonResponse({'success': True, 'message': 'GPX uploaded to cloud'}, status=202)
    
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


def get_video_by_name(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            video_name = data.get('video_name')
            user_id = get_user_id_from_username(username)

            if not video_name:
                return JsonResponse({'success': False, 'message': 'Missing video_name parameter'}, status=400)

            if user_id is None:
                return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
            
            if video_name.endswith('.MP4'):
                video_name = video_name.rsplit('.', 1)[0] + '.mp4'

            if not Video.objects.filter(user_profile_id=user_id, video_name=video_name).exists():
                return JsonResponse({'success': False, 'message': 'Video name is not associated with the user'}, status=409)
            
            storage_client = storage.Client()
            bucket_name = "bucket-licenta-rovin"
            
            video_blob = storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{video_name}')

            expiration_time = datetime.now() + timedelta(minutes=10)
            
            video_signed_url = video_blob.generate_signed_url(
                version='v4',
                expiration=expiration_time,
                method='GET',
                # content_type='video/mp4',
            )
        

            return JsonResponse({
                'success': True,
                'video': video_signed_url,
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)  
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

def display_gpx(request):
    gpx_file_path = "./video_data/gpx/test.gpx"

    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    waypoints = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                 waypoints.append({
                'lat': point.latitude,
                'lng': point.longitude,
                'ele': point.elevation,
                'time': point.time.timestamp()
            })

    return JsonResponse({'waypoints': waypoints})


