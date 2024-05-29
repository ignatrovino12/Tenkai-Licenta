from django.urls import path
from . import views

urlpatterns = [
    path('upload_video/', views.generate_signed_url_video, name='upload_video'),
    path('display_gpx/', views.display_gpx, name='display_gpx'),
    path('convert_gpx/', views.convert_gpx, name='convert_gpx'),
    path('download_video/', views.get_video_by_name, name='download_video'),
    # path('task-status/<str:task_id>/', views.task_status, name='task_status'),
    ]