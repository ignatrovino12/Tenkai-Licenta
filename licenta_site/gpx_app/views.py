from django.shortcuts import render, redirect
from django.http import JsonResponse
from google.cloud import storage
import json
from .models import Video
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import gpxpy
from django.utils import timezone

bucket_name="bucket-licenta-rovin"

def get_user_id_from_username(username):
    user = User.objects.get(username=username)
    return user.id

def generate_signed_url_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            video_name = data.get('video_name')
            user_id = get_user_id_from_username(username)

            if user_id is None:
                return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
            
            if Video.objects.filter(user_profile__user_id=user_id, video_name=video_name).exists():
                return JsonResponse({'success': False, 'message': 'Video name already associated with the user'}, status=404)

            video = Video.objects.create(video_name=video_name, user_profile_id=user_id, timestamp=timezone.now())
            storage_client = storage.Client()
            bucket_name="bucket-licenta-rovin"

            blob = storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{video_name}')
            current_datetime = datetime.now()
            expiration_time = current_datetime + timedelta(minutes=8)
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


def generate_signed_url_gpx(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            gpx_name = data.get('gpx_name')
            user_id = get_user_id_from_username(username)

            if user_id is None:
                return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
            
            storage_client = storage.Client()
            bucket_name="bucket-licenta-rovin"

            blob = storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{gpx_name}')
            current_datetime = datetime.now()
            expiration_time = current_datetime + timedelta(minutes=8)
            signed_url = blob.generate_signed_url(
                version='v4',
                expiration=expiration_time,
                method='PUT',
                content_type='application/gpx+xml'
            )

            return JsonResponse({'success': True, 'signed_url': signed_url}, status=200)
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

