from django.db import models
from base_app.models import UserProfile
from django.utils import timezone

# Create your models here.
class Video(models.Model):
    video_id = models.AutoField(primary_key=True)
    video_name = models.CharField(max_length=100)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)  
    nr_likes = models.IntegerField(default=0) 

    def __str__(self):
        return self.video_name