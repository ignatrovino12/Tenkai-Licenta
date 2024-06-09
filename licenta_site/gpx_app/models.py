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
    country = models.CharField(max_length=50,default="")
    city = models.CharField(max_length=50,default="")
    description = models.TextField(max_length=201,default="")

    def __str__(self):
        return self.video_name
    
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

class Upvote(models.Model):
    upvote_id = models.AutoField(primary_key=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Upvote {self.upvote_id} for Video {self.video_id}"