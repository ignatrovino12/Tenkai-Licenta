from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('is_logged/', views.is_logged, name='is_logged'),
    path('update_picture/',views.update_picture, name='update_picture'),
    path('update_credentials/', views.update_credentials, name='update_credentials'),
    path('profile/<str:username>', views.profile_view, name='profile'),

]