from django.urls import path
from . import views

urlpatterns = [
    path('upload_video/', views.upload_video, name='upload_video'),
    path('display_gpx/', views.display_gpx, name='display_gpx'),
    path('convert_gpx/', views.convert_gpx, name='convert_gpx'),
    path('download_video/', views.get_video_by_name, name='download_video'),
    path('upload_video_gpx/',views.upload_video_gpx, name='upload_video_gpx'),
    path('update_city_country/',views.update_city_country, name='update_city_country'),
    path('display_city_country/',views.display_city_country, name='display_city_country'),
    path('make_comment/',views.make_comment, name='make_comment'),
    path('display_profile_picture/', views.display_profile_picture,name='display_profile_picture'),
    path('delete_comment/',views.delete_comment,name='delete_comment'),
    ]