from django.contrib import admin
from .models import  Organization,Super_user

# Register your models here.
admin.site.register([Organization, Super_user])