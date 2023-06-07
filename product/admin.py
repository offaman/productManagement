from django.contrib import admin
from .models import  Organisation,Super_user

# Register your models here.
admin.site.register([Organisation, Super_user])