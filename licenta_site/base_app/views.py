from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import re
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token
from .models import UserProfile
from google.cloud import storage
from .tasks import update_picture_task
from datetime import datetime, timedelta
from gpx_app.models import Video,Upvote
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

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

        if re.search(r'\s', username):
            return JsonResponse({'success': False, 'message': 'Username should not contain spaces'}, status=400)
        
        if re.search(r'\s', password):
            return JsonResponse({'success': False, 'message': 'Password should not contain spaces'}, status=400)
        
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
            expiration_time = current_datetime + timedelta(minutes=5)


            image_link = blob.generate_signed_url(
                version='v4',
                expiration=expiration_time,
                method='GET',
            )

            # videos of the user
            videos = Video.objects.filter(user_profile=user_profile).order_by('video_id')

            video_data = []
            for video in videos:
                video_data.append({
                    'video_name': video.video_name,
                    'country': video.country,
                    'city': video.city,
                    'nr_likes': video.nr_likes,
                    'description': video.description,
                })

            # likes/upvotes for the user
            data = json.loads(request.body)
            current_username = data.get('username')

            current_user_profile = get_object_or_404(UserProfile, user__username=current_username)
            upvotes = Upvote.objects.filter(user_profile=current_user_profile, video_id__in=videos)
            
   
            upvotes_to_send = []
            for upvote in upvotes:
                upvote_info = {
                    'video_name': upvote.video_id.video_name,
                }
                upvotes_to_send.append(upvote_info)

            return JsonResponse({
                'username': username,
                'image_link': image_link,
                'videos': video_data,
                'upvotes': upvotes_to_send,
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

            videos = Video.objects.filter(user_profile=user_profile).order_by('-timestamp')

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
            user_id=user.id

            # delete DB
            video = Video.objects.get(user_profile=user_profile, video_name=video_name)
            video.delete()

            # delete cloud
            video_blob = storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{video_name}')
            video_blob.delete()

            gpx_name = video_name[:-3] + 'gpx'
            gpx_blob = storage_client.bucket(bucket_name).blob(f'uploads/{user_id}/{gpx_name}')
            gpx_blob.delete()

            return JsonResponse({'success': True, 'message': 'Video deleted successfully'}, status=200)
        
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
        
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User profile not found'}, status=404)
        
        except Video.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Video not found'}, status=404)
    
    else:
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed'}, status=405)


def upload_upvote(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            video_name = data.get('video_name')
            video_user = data.get('video_user')

            user_profile = UserProfile.objects.get(user__username=username)
            video = Video.objects.get(video_name=video_name, user_profile__user__username=video_user)

            upvote, created = Upvote.objects.get_or_create(user_profile=user_profile, video_id=video)

            if not created:
                upvote.delete()
                video.nr_likes -= 1
                video.save()
                return JsonResponse({'success': True, 'message': 'Upvote deleted successfully'}, status=200)
            else:
                video.nr_likes += 1
                video.save()
                return JsonResponse({'success': True, 'message': 'Upvote added successfully'}, status=200)
            

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

def display_search_users(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            order_by = data.get('order_by','nr_videos')
            is_ascending = data.get('is_ascending',False)     

            if order_by not in ['nr_videos', 'nr_upvotes']:
                return JsonResponse({"error": "Invalid order_by field."}, status=400) 

            # determine order
            if (is_ascending):
                order_prefix = ''
            else:
                order_prefix = '-'

            user_profiles = UserProfile.objects.filter(user__username__startswith=name)

            # find total number of videos/ upvotes per user
            user_profiles = user_profiles.annotate(
                nr_videos=Count('video')
            )

            user_profiles = user_profiles.annotate(
                nr_upvotes=Coalesce(Sum('video__nr_likes'), Value(0))
            )

            # order data accordingly
            if order_by == 'nr_videos':
                user_profiles = user_profiles.order_by(f"{order_prefix}nr_videos")
            elif order_by == 'nr_upvotes':
                user_profiles = user_profiles.order_by(f"{order_prefix}nr_upvotes")
          

            user_profiles_list = []
        
            for user_profile in user_profiles:
                
                # generate image links
                if user_profile.has_picture:
                    file_path = f'images/{user_profile.user.id}/ppicture.png'
                else:
                    file_path = 'images/0/ppicture.png'

                blob = storage_client.bucket(bucket_name).blob(file_path)
                current_datetime = datetime.now()
                expiration_time = current_datetime + timedelta(minutes=5)

                image_link = blob.generate_signed_url(
                    version='v4',
                    expiration=expiration_time,
                    method='GET',
                )

                nr_videos = getattr(user_profile, 'nr_videos', 0)
                if(nr_videos==0):
                    nr_upvotes = 0
                else:
                    nr_upvotes = getattr(user_profile, 'nr_upvotes', 0)

                user_profiles_list.append({
                    'name': user_profile.user.username,
                    'nr_videos': nr_videos,
                    'nr_upvotes':  nr_upvotes,
                    'image_link': image_link
                })


            return JsonResponse(user_profiles_list, safe=False, status=200) 

        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

def display_search_videos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_name = data.get('video_name')
            order_by = data.get('order_by','time')
            is_ascending = data.get('is_ascending',False) 
            time_period = data.get('time_period')
            username=data.get('username')
            

            if order_by not in ['time', 'nr_upvotes']:
                return JsonResponse({"error": "Invalid order_by field."}, status=400) 
                
            if time_period not in ['today', 'last_week','last_month','last_year','']:
                return JsonResponse({"error": "time_period field."}, status=400) 
            

            # filter by name
            videos = Video.objects.filter(video_name__startswith=video_name)

            # filter by time period
            now = timezone.now()
            if time_period == 'today':
                start_time = now - timedelta(days=1)
            elif time_period == 'last_week':
                start_time = now - timedelta(weeks=1)
            elif time_period == 'last_month':
                start_time = now - timedelta(days=30)
            elif time_period == 'last_year':
                start_time = now - timedelta(days=365)
            else:
                start_time = None
            
            if start_time:
                videos = videos.filter(timestamp__gte=start_time)

            # determine order
            if (is_ascending):
                order_prefix = ''
            else:
                order_prefix = '-'

            # filter time or nr_upvotes
            if order_by == "time":
                videos = videos.order_by(f'{order_prefix}timestamp')
            if order_by == 'nr_upvotes':
                 videos = videos.order_by(f'{order_prefix}nr_likes')

            # add image link 
            video_data = []
            for video in videos:
                user_profile = video.user_profile

                if user_profile.has_picture:
                    file_path = f'images/{user_profile.user.id}/ppicture.png'
                else:
                    file_path = 'images/0/ppicture.png'

                # Generate signed URL
                blob = storage_client.bucket(bucket_name).blob(file_path)
                current_datetime = datetime.now()
                expiration_time = current_datetime + timedelta(minutes=5)
                image_link = blob.generate_signed_url(
                    version='v4',
                    expiration=expiration_time,
                    method='GET',
                )

                video_data.append({
                    'video_name': video.video_name,
                    'country': video.country,
                    'city': video.city,
                    'nr_likes': video.nr_likes,
                    'description': video.description,
                    'image_link': image_link,
                    'username': user_profile.user.username
                })

            # send upvotes
            current_user_profile = get_object_or_404(UserProfile, user__username=username)
            upvotes = Upvote.objects.filter(user_profile=current_user_profile, video_id__in=videos)  
   
            upvotes_to_send = []
            for upvote in upvotes:
                upvote_info = {
                    'video_name': upvote.video_id.video_name,
                }
                upvotes_to_send.append(upvote_info)

            return JsonResponse({'succes':True, 'videos': video_data, 'upvotes':upvotes_to_send}, status=200)


        except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)