from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import UserProfile
import json

class CSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for a specific URL or view  and skip it
        if request.path == '/login/' or request.path=="/signup/" or request.path.startswith('/admin/') or request.path=="/convert_gpx/" or request.path=="/set_cookies/" or request.path.startswith('/accounts') :
            return self.get_response(request)

        # Get the username and CSRF token from the request
        try:
            data = json.loads(request.body)
            if 'username' in data and 'csrf_token' in data:
                username = data.get('username')
                csrf_token  = data.get('csrf_token')
            else:
                return JsonResponse({'success': False, 'message': 'Missing username or CSRF token'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format'}, status=400)


        # Verify the CSRF token
        if username and csrf_token:
            try:
                user = User.objects.get(username=username)
                profile = UserProfile.objects.get(user=user)
                if profile.csrf_token != csrf_token:
                    return JsonResponse({'success': False, 'message': 'Invalid CSRF token'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
        else:
            return JsonResponse({'success': False, 'message': 'Missing username or CSRF token'}, status=400)
        
        # Continue processing the request
        response = self.get_response(request)
        return response
