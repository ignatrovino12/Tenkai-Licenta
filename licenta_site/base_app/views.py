from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import re
from django.middleware.csrf import get_token
from .models import UserProfile
from google.cloud import storage
from .tasks import update_picture_task
from datetime import datetime, timedelta
from gpx_app.models import Video

storage_client = storage.Client()
bucket_name = "bucket-licenta-rovin"

def get_user_id_from_username(username):
    try:
        user = User.objects.get(username=username)
        return user.id
    except User.DoesNotExist:
        return None


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

def update_picture(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        image=data.get('image')
        user_id = get_user_id_from_username(username)

        succes=update_picture_task.delay(user_id, image)


        if succes :
            # database mark
            user_profile = UserProfile.objects.get(user_id=user_id)
            user_profile.has_picture = True
            user_profile.save()
            return JsonResponse({'success': True, 'message': 'Updated the image for the user'}, status=200) 
        else:
            return JsonResponse({'success': False, 'message': 'User does not exist or picture can not be uploaded'}, status=405)
        
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)
    

def update_credentials(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            username = data.get('username')
            email=data.get('email')
            password =data.get('password')
            old_password =data.get('old_password')

            user = User.objects.get(username=username)

            if not user.check_password(old_password):
                return JsonResponse({'success': False, 'message': 'Old password is incorrect'}, status=400)
            
            if password:
                
                if len(password)<8 or len(password)>30:
                    return JsonResponse({'success': False, 'message': 'Password should have between 8 and 30 characters'}, status=400)

                if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
                    return JsonResponse({'success': False, 'message': 'Password should contain both letters and numbers'}, status=400)
                
                user.set_password(password)
                user.save()

            if email:
                user.email = email
                user.save()



            return JsonResponse({'success': True, 'message': 'Credentials updated successfully'}, status=200)


        except User.DoesNotExist:      
            return JsonResponse({'success': False, 'message': 'User not found'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)


def profile_view(request, username):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)
            has_picture = user_profile.has_picture
            user_id = get_user_id_from_username(username)

             # check if user has image or we set default otherwise
            if(has_picture is True):
                file_path = f'images/{user_id}/ppicture.png'
            else :
                file_path = f'images/0/ppicture.png'


            # image link for user
            blob = storage_client.bucket(bucket_name).blob(file_path)
            current_datetime = datetime.now()
            expiration_time = current_datetime + timedelta(hours=4)


            image_link = blob.generate_signed_url(
                version='v4',
                expiration=expiration_time,
                method='GET',
            )

            # videos of the user
            videos = Video.objects.filter(user_profile=user_profile)

            video_data = []
            for video in videos:
                video_data.append({
                    'video_name': video.video_name,
                    'country': video.country,
                    'city': video.city
                })

            return JsonResponse({
                'username': username,
                'image_link': image_link,
                'videos': video_data
            },status=200)
        
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
          

    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)

def display_videos_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)

            videos = Video.objects.filter(user_profile=user_profile)

            video_data = []
            for video in videos:
                video_data.append({
                    'video_name': video.video_name,
                    'country': video.country,
                    'city': video.city
                })

            return JsonResponse({'succes':True, 'videos': video_data}, status=200)
        
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
          

    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)
    

def delete_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            video_name = data.get('video_name')
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)

            video = Video.objects.get(user_profile=user_profile, video_name=video_name)
            video.delete()

            return JsonResponse({'success': True, 'message': 'Video deleted successfully'}, status=200)
        
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
        
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User profile not found'}, status=404)
        
        except Video.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Video not found'}, status=404)
    
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)



    


