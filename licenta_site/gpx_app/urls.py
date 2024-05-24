from django.urls import path
from . import views

urlpatterns = [
    path('upload_video/', views.generate_signed_url_video, name='upload_video'),
    path('upload_gpx/', views.generate_signed_url_gpx, name='upload_gpx'),
    path('display_gpx/', views.display_gpx, name='display_gpx'),
    ]