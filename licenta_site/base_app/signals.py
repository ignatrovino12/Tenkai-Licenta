from django.dispatch import receiver
from django.db.models.signals import post_save
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.db import models
from .models import UserProfile
from django.contrib.auth.signals import user_logged_in


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        request = kwargs.get('request')  
        if request:
            csrf_token = get_token(request)
            profile = UserProfile.objects.create(user=instance, csrf_token=csrf_token)
            profile.save()
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(user_logged_in)
def set_csrf_token(sender, request, user, **kwargs):
    csrf_token = get_token(request)
    profile = user.userprofile
    profile.csrf_token = csrf_token
    profile.save()