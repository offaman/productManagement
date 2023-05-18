from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from .models import  Organization, Super_user, User
import pymongo
from bson import json_util
import json
import uuid
from django.utils import timezone 

COLLECTION_PER_ORG = ['Properties', 'Taxonomies', 'Validation', 'Fields_associated', 'Property_groups']

response_message = {}

def create_admin_user(request):
    requestBody  = JSONParser().parse(request)
    user_name = requestBody['user_name']
    user_email = requestBody['email_id']
    user_password = requestBody['password']
    newSuperUser = Super_user(user_name = user_name, user_email = user_email, password = user_password)
    newSuperUser.save()

    response_message['message'] = 'Admin user created successfully'
    response_message['status'] = 'ok'

    return JsonResponse( response_message,status=200)


def create_organization(request):
    requestBody  = JSONParser().parse(request)
    # create organization with specified name
    org_unique_id = str(uuid.uuid4())
    organization_added = Organization(organization_id = org_unique_id, organization_name = requestBody['organization_name'], create_by = requestBody['creator'])
    organization_added.save()

    # create a new collection with recent added org_id_pxm_database and create diff collection into it.
    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{org_unique_id}_pxm_database']
    for collection in COLLECTION_PER_ORG:
        mydb.create_collection(collection)

    response_message['message'] = 'Organization created successfully'
    response_message['status'] = 'ok'

    return JsonResponse(response_message, status=200)


# Create your views here.
def create_taxonomy(request):
    requestBody  = JSONParser().parse(request)
    organization_id = requestBody['organization_id']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    taxonomy_collection = mydb['Taxonomies']

    requestBody['taxonomy_id']= str(uuid.uuid4())
    taxonomy_collection.insert_one(requestBody)

    mydb.create_collection(requestBody['taxonomy_name'])

    response_message['message'] = 'Taxonomy user created successfully'
    response_message['status'] = 'ok'

    return JsonResponse(response_message, status = 200)


def add_taxonomy_records(request):
    requestBody  = JSONParser().parse(request)

    taxonomy_id = requestBody['taxonomy_id']
    organization_id = requestBody['organization_id']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    
    my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'taxonomy_name':1,'_id':0})

    requestBody['data']['id'] = str(uuid.uuid4())
    mydb[my_taxonomy_collection_name['taxonomy_name']].insert_one(requestBody['data'])

    response_message['message'] = 'Data inserted successfully'
    response_message['status'] = 'ok'

    return JsonResponse(response_message,status=200)


def get_records_by_taxonomy(request):
    
    taxonomy_id =request.GET['tid']
    organization_id = request.GET['orgid']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    
    my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'taxonomy_name':1,'_id':0})

    taxonomy_records =  list(mydb[my_taxonomy_collection_name['taxonomy_name']].find({},{'_id':0}))
    return JsonResponse(taxonomy_records, safe=False, status = 200)


def add_user_to_organisation(request):
    requestBody = JSONParser().parse(request)

    new_user = User(organization_id = requestBody['organization_id'], user_name = requestBody["user_name"], 
                    email_id = requestBody['email_id'], password = requestBody['password'], 
                    user_permission = requestBody['user_permission'], 
                    created_by = requestBody['created_by'])
    new_user.save()

    response_message['message'] = 'User created successfully'
    response_message['status'] = 'ok'

    return JsonResponse(response_message, status = 200)


def create_new_field(request):
    requestBody = JSONParser().parse(request)

    organization_id = request.GET['org_id']
    taxonomy_id = requestBody['taxonomy_id']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    
    properties_table = mydb['Properties']
    field_unique_id = str(uuid.uuid4())

    requestBody['created_at'] = timezone.now()
    requestBody['field_id'] = field_unique_id
    properties_table.insert_one(requestBody)

    field_association_collection = mydb['Fields_associated']
    field_association_collection.insert_one({'taxonomy_id':taxonomy_id, 'field_id':field_unique_id, 'property_group':requestBody['property_group']})

    response_message['message'] = 'Property created successfully'
    response_message['status'] = 'ok'

    return JsonResponse(response_message, status = 200)


def get_taxonomy_by_organization(request):
    organization_id = request.GET['org_id']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    all_taxonomies = mydb['Taxonomies'].find({},{'taxonomy_name':1, '_id':0})

    taxonomy_list = []
    for taxonomy in list(all_taxonomies):
        taxonomy_list.append(taxonomy['taxonomy_name'])
    return JsonResponse({'taxonomies':taxonomy_list}, safe=False, status=200)


def add_property_group(request):

    requestBody = JSONParser().parse(request)

    organization_id = request.GET['org_id']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']

    requestBody['property_group_id'] = str(uuid.uuid4())

    mydb['Property_groups'].insert_one(requestBody)

    response_message['message'] = 'Property group created successfully'
    response_message['status'] = 'ok'

    return JsonResponse(response_message, status=200)


def get_all_field_by_taxonomy(request):

    organization_id = request.GET['org_id']
    taxonomy_id = request.GET['tid']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']

    all_fields_with_that_taxonomy = []

    associated_field_ids = list(mydb['Fields_associated'].find({'taxonomy_id':taxonomy_id},{'field_id':1,'_id':0}))

    for field in associated_field_ids:
        field_info = list(mydb['Properties'].find({'field_id':field['field_id']},{'_id':0,'created_at':0,'created_by':0, 'field_id':0,'taxonomy_id':0}))
        all_fields_with_that_taxonomy.append((field_info))

    all_property_groups  = list(mydb['Property_groups'].find({},{'property_group_name':1, '_id':0}))

    property_group_list = []

    for group in all_property_groups:
        property_group_list.append(group['property_group_name'])

    fields_with_property_groups = {}

    for p_groups in property_group_list:
        fields_with_property_groups[f"{p_groups}"] = list(mydb['Properties'].find({'property_group':p_groups, 'taxonomy_id':taxonomy_id},{'_id':0,'created_at':0,'created_by':0, 'field_id':0,'taxonomy_id':0}))

    return JsonResponse(fields_with_property_groups, status = 200)

