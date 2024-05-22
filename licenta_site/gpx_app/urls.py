from django.urls import path
from . import views

urlpatterns = [
    path('upload_video/', views.generate_signed_url, name='upload_video'),
    path('display_gpx/', views.display_gpx, name='display_gpx'),
    ]