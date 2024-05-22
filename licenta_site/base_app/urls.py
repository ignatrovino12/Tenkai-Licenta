from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('is_logged/', views.is_logged, name='is_logged'),
    # path('display_gpx/', views.display_gpx, name='display_gpx'),
]