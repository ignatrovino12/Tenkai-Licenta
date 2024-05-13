from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# from django.contrib import messages
from django.http import JsonResponse
import json
import re
from django.middleware.csrf import get_token
from .models import UserProfile
from django.shortcuts import render
import gpxpy

def user_login(request):
   
    if request.method == 'POST':
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        
            csrf_token = get_token(request)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.csrf_token = csrf_token
            profile.save()
            
            # send csrf-token to frontend
            response = JsonResponse({'success': True, 'message': 'Logged in successfully!', 'csrf_token': csrf_token},status=200)
            return response
            
        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password'}, status=401)
    
    return JsonResponse({'success': False, 'message': 'This method only supports POST requests'}, status=405)
    
def user_signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        password_verify = data.get('password_verify')
        email = data.get('email')

        # username/password requirements
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists'}, status=400)
        
        if password != password_verify:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'}, status=400)
        
        if len(username)<6 or len(username)>30:
            return JsonResponse({'success': False, 'message': 'Username should have between 6 and 30 characters'}, status=400)
        
        if len(password)<8 or len(password)>30:
            return JsonResponse({'success': False, 'message': 'Password should have between 8 and 30 characters'}, status=400)

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
            return JsonResponse({'success': False, 'message': 'Password should contain both letters and numbers'}, status=400)
        
           
        user = User.objects.create_user(username=username, email=email, password=password)
        csrf_token = get_token(request)
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.csrf_token = csrf_token
        profile.save()

        # send csrf-token to frontend
        response = JsonResponse({'success': True, 'message': 'User created successfully!', 'csrf_token': csrf_token},status=200)
        return response
    else:
        return JsonResponse({'success': False, 'message': 'This method only supports POST requests'}, status=405)
    
def user_logout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            csrf_token  = data.get('csrf_token')

            user = User.objects.get(username=username)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.csrf_token=''
            profile.save()

            logout(request)

     
            return JsonResponse({'success': True, 'message': 'Logged out successfully'})
        except User.DoesNotExist:      
            return JsonResponse({'success': False, 'message': 'User not found'}, status=400)

    return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)

def is_logged(request):
    if request.method == 'POST':
        return JsonResponse({'success': True, 'message': 'Verified if it is logged at start of loading'}, status=200)
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)

def display_gpx(request):
    gpx_file_path = "C:\\Users\\ignat\\Documents\\Facultate2\\Licenta\\Licenta-2024\\licenta_site\\video_data\\gpx\\test2.gpx"
    
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    waypoints = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                waypoints.append({'lat': point.latitude, 'lng': point.longitude})

    return JsonResponse({'waypoints': waypoints})

