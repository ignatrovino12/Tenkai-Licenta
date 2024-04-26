from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect,csrf_exempt,requires_csrf_token
import json
from django.middleware.csrf import get_token
from .models import UserProfile


@csrf_exempt
def user_login(request):
    csrf_token_header = request.META.get('HTTP_X_CSRFTOKEN', None)
    csrf_token_cookie = request.COOKIES.get('csrftoken',None)
    # print(request.COOKIES.get())


    print(csrf_token_cookie)
    print(csrf_token_header)

    if csrf_token_header == csrf_token_cookie:
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
                return JsonResponse({'success': False, 'message': 'Invalid username or password.'}, status=401)
        
        return JsonResponse({'success': False, 'message': 'This method only supports POST requests.'}, status=405)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid CSRF token'}, status=403)

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            user = form.save()
            user.refresh_from_db()  # Pentru a obține câmpurile suplimentare, de exemplu, email
            user.email = email
            user.save()
            # Autentificarea automată după înregistrare
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirecționează utilizatorul către pagina principală sau alta pagină după înregistrare
                return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('index')  # Schimbă 'index' cu numele paginii la care dorești să redirecționezi utilizatorii după deconectare

