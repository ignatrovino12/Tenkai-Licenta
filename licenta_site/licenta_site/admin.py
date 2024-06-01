from django.contrib import admin
from base_app.models import UserProfile
from gpx_app.models import Video

admin.site.register(UserProfile)
admin.site.register(Video)