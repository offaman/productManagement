from django.db import models
import uuid
from django.utils import timezone


class Organisation(models.Model):
    organization_id = models.CharField(default=uuid.uuid4, primary_key=True, max_length=100)
    organization_name = models.CharField(max_length= 300)
    created_at = models.TimeField(default= timezone.localtime())
    create_by = models.EmailField(max_length=200)

    class Meta:
        db_table = "Organization"

    def __str__(self):
        return self.organization_name
    

class Super_user(models.Model):
    user_id = models.CharField(default= uuid.uuid4, max_length=100)
    user_name = models.CharField(max_length=200)
    user_email = models.EmailField(max_length=200, primary_key=True)
    password = models.CharField(max_length=200, blank=False, null= False)
    created_at = models.TimeField(default= timezone.localtime())


    class Meta:
        db_table = "Super_user"

    def __str__(self) -> str:
        return self.user_name


class User(models.Model):
    organization_id = models.CharField(blank=False, max_length=100)
    user_id = models.CharField(default = uuid.uuid4, primary_key= True, max_length=100)
    user_name = models.CharField(max_length=400)
    email_id = models.EmailField(max_length=500)
    password = models.CharField(max_length=150)
    user_permission = models.CharField(max_length=50)
    created_at = models.TimeField(default= timezone.now)
    created_by = models.EmailField(max_length=200)
 
    class Meta:
        db_table = "User"