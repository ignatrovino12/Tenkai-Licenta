from django.urls import path
from . import views

urlpatterns = [
    path('upload_video/', views.upload_video, name='upload_video'),
    path('display_gpx/', views.display_gpx, name='display_gpx'),
    path('convert_gpx/', views.convert_gpx, name='convert_gpx'),
    path('download_video/', views.get_video_by_name, name='download_video'),
    path('upload_video_gpx/',views.upload_video_gpx, name='upload_video_gpx'),
    # path('task-status/<str:task_id>/', views.task_status, name='task_status'),
    ]