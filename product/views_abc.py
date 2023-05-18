from pymodm.connection import connect
from pymongo.write_concern import WriteConcern
from pymodm import MongoModel, fields
from django.http import HttpResponse

# Connect to MongoDB and call the connection "my-app".
connect("mongodb://localhost:27017/50681e8e-f57b-4fb8-bdee-b238f94530f9_pxm_database", alias="my-app")

class User(MongoModel):
    email = fields.EmailField(primary_key=True)
    first_name = fields.CharField()
    last_name = fields.CharField()

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'my-app'

def insert_user(request):

    new_obj = User()
    # new_obj.new_field = fields.BooleanField()
    # User('user@email.com', True, 'Ross',True).save()

    # print(new_obj.new_field)
    print(new_obj.first_name)
    return HttpResponse("Added")