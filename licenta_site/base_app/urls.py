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
    path('display_videos_profile/',views.display_videos_profile, name='display_videos_profile'),
    path('delete_video/',views.delete_video,name='delete_video'),
    path('upload_upvote/',views.upload_upvote, name='upload_upvote'),
    path('display_search_users/',views.display_search_users, name='display_search_users')

]