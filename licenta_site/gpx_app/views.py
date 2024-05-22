from django.shortcuts import render, redirect
from django.http import JsonResponse
from google.cloud import storage
import json
from django.contrib.auth.models import User
from google.oauth2 import service_account
from datetime import datetime, timedelta
import gpxpy

bucket_name="bucket-licenta-rovin"

def get_user_id_from_username(username):
    user = User.objects.get(username=username)
    return user.id

def generate_signed_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            video_name = data.get('video_name')
            user_id = get_user_id_from_username(username)

            if user_id is None:
                return JsonResponse({'error': 'User not found'}, status=404)

            storage_client = storage.Client()
            bucket_name="bucket-licenta-rovin"

            blob = storage_client.bucket(bucket_name).blob(video_name)
            current_datetime = datetime.now()
            expiration_time = current_datetime + timedelta(minutes=8)
            signed_url = blob.generate_signed_url(
                version='v4',
                expiration=expiration_time,
                method='PUT',
                content_type='video/mp4'
            )

            return JsonResponse({'signed_url': signed_url, 'user_id': user_id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
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

