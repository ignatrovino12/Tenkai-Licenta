from django.contrib import admin
from base_app.models import UserProfile
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from allauth.account.models import EmailAddress 

admin.site.register(UserProfile)

# admin.site.unregister(SocialAccount)
# admin.site.unregister(SocialApp)
# admin.site.unregister(SocialToken)
# admin.site.unregister(Site)
# admin.site.unregister(EmailAddress)
