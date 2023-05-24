from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from .models import  Organization, Super_user, User
import pymongo
import uuid
from django.utils import timezone 
from .validations.validation import validateInputTaxonomyData
from .utilities.utils import MyException

COLLECTION_PER_ORG = ['Properties', 'Taxonomies', 'Validation', 'Fields_associated', 'Property_groups']

response_message = {}

def create_organization(request):
    try:
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
        response_message['status'] = 'Ok'

        return JsonResponse(response_message, status=200)
    except:
        return JsonResponse({"Exception":"Some exception occured"})


def taxonomies(request):
    try:
        requestBody  = JSONParser().parse(request)
        organization_id = requestBody['organization_id']

        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        taxonomy_collection = mydb['Taxonomies']

        if request.method == 'GET':
            all_taxonomies = mydb['Taxonomies'].find({},{'taxonomy_name':1, '_id':0})
            taxonomy_list = []
            for taxonomy in list(all_taxonomies):
                taxonomy_list.append(taxonomy['taxonomy_name'])
            response_message['taxonomies'] = taxonomy_list

        if request.method == 'POST':
        
            requestBody['taxonomy_id']= str(uuid.uuid4())
            taxonomy_collection.insert_one(requestBody)

            mydb.create_collection(requestBody['taxonomy_name'])

            response_message['message'] = 'Taxonomy created successfully'
            response_message['status'] = 'Ok'

        elif request.method == 'DELETE':

            taxonomy_id = requestBody['taxonomy_id']
            taxonomy_collection.delete_one({'taxonomy_id':taxonomy_id})

            response_message['message'] = 'Taxonomy deleted successfully'
            response_message['status'] = 'Ok'
        
        return JsonResponse(response_message, status = 200)
    except:
        return JsonResponse({"Exception":"Some exception occured...Please try again"})


def taxonomy_records(request):

    requestBody  = JSONParser().parse(request)
    taxonomy_id = request.GET.get('tid')
    organization_id = request.GET.get('org_id')

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'taxonomy_name':1,'_id':0})

    if request.method == 'GET':
        if request.GET.get('record_id', None):
            record_id = request.GET['record_id']
            record_data  = mydb[my_taxonomy_collection_name['taxonomy_name']].find_one({'record_id':record_id},{'_id':0, 'validations':0})
            response_message['data'] = record_data
        else:
            all_record_data  = list(mydb[my_taxonomy_collection_name['taxonomy_name']].find_one({},{'_id':0, 'validations':0}))
            response_message['data'] = all_record_data
        return JsonResponse(response_message, safe=False ,status = 200)

    elif request.method == 'DELETE':
        record_id = request.GET['record_id']
        mydb[my_taxonomy_collection_name['taxonomy_name']].delete_one({'record_id':record_id})
        response_message['message'] = "Record deleted successfully"
        response_message['status'] = 'Ok'

    else:
        all_associated_fields_ids = list(mydb['Fields_associated'].find({'taxonomy_id':taxonomy_id},{'field_id':1,'_id':0}))
        all_properties = []

        for field in all_associated_fields_ids:
            all_properties.append(mydb['Properties'].find_one({'field_id':field['field_id']},{'_id':0,'created_at':0,'created_by':0, 'field_id':0,'taxonomy_id':0,'property_group':0}))  

        if request.GET.get('record_id',None):
            record_id = request.GET['record_id']
            validateInputTaxonomyData(requestBody['data'], all_properties)
            mydb[my_taxonomy_collection_name['taxonomy_name']].update_one({'record_id':record_id},{'$set':requestBody['data']})
            response_message['message'] = 'Data updated successfully'
            response_message['status'] = 'Ok'   

        else:
            validateInputTaxonomyData(requestBody['data'], all_properties)
            requestBody['data']['record_id'] = str(uuid.uuid4())
            mydb[my_taxonomy_collection_name['taxonomy_name']].insert_one(requestBody['data'])

            response_message['message'] = 'Data inserted successfully'
            response_message['status'] = 'Ok'

    return JsonResponse(response_message,status=200)



def fields(request):
    organization_id = request.GET['org_id']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']
    properties_collection = mydb['Properties']

    if request.method == 'DELETE':
        field_id = request.GET['field_id']
        properties_collection.delete_one({'field_id':field_id})
        field_association_collection = mydb['Fields_associated']
        field_association_collection.delete_many({'field_id':field_id})

        response_message['message'] = 'Property deleted successfully'
        response_message['status'] = 'Ok'

    elif request.method == 'GET':
        all_fields = list(mydb['Properties'].find({},{'_id':0,'created_at':0, 'created_by':0}))
        return JsonResponse(all_fields, safe=False)

    else:
        requestBody = JSONParser().parse(request)
        if request.GET.get('field_id',None):
            field_id = request.GET['field_id']
            properties_collection.update_one({'field_id':field_id},{'$set':requestBody})
            response_message['message'] = 'Property updated successfully'
            response_message['status'] = 'Ok'
        
        else:
            field_unique_id = str(uuid.uuid4())
            requestBody['created_at'] = timezone.now()
            requestBody['field_id'] = field_unique_id
            properties_collection.insert_one(requestBody)

            field_association_collection = mydb['Fields_associated']
            field_association_collection.insert_one({'field_id':field_unique_id})

            response_message['message'] = 'Property created successfully'
            response_message['status'] = 'Ok'

    return JsonResponse(response_message, status = 200)


def property_groups(request):
    organization_id = request.GET['org_id']
    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']

    if request.method == 'GET':
        all_fields  = list(mydb['Property_groups'].find())
        all_fields_object = {}
        all_fields_object['property_groups'] = []
        for field in all_fields:
            all_fields_object['property_groups'].append(field['property_group_name'])
        return JsonResponse(all_fields_object, status = 200)

    elif request.method == 'DELETE':
        prop_group_name = request.GET['property_group_name']
        mydb['Property_groups'].delete_one({'property_group_name':prop_group_name})

        response_message['message'] = 'Property group deleted successfully'
        response_message['status'] = 'Ok'

    else:
        requestBody = JSONParser().parse(request)
        requestBody['property_group_id'] = str(uuid.uuid4())
        mydb['Property_groups'].insert_one(requestBody)

        response_message['message'] = 'Property group created successfully'
        response_message['status'] = 'Ok'

    return JsonResponse(response_message, status=200)


def get_all_field_by_taxonomy(request):

    organization_id = request.GET['org_id']
    taxonomy_id = request.GET['tid']

    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']

    all_associated_fields = list(mydb['Fields_associated'].find({'taxonomy_id':taxonomy_id},{'field_id':1,'_id':0}))

    all_property_groups  = list(mydb['Property_groups'].find({},{'property_group_name':1, '_id':0}))

    property_group_list = []
    for group in all_property_groups:
        property_group_list.append(group['property_group_name'])

    property_group_mapped_fields = {}

    for p_group in property_group_list:
        property_group_mapped_fields[f"{p_group}"] = []
        for field in all_associated_fields:
            property_group_mapped_fields[f"{p_group}"].append(mydb['Properties'].find_one({'property_group':p_group, 'field_id':field['field_id']},{'_id':0,'created_at':0,'created_by':0, 'field_id':0,'taxonomy_id':0,'property_group':0}))  

    return JsonResponse(property_group_mapped_fields, status = 200)


def associate_field_to_taxonomy(request):
    requestBody = JSONParser().parse(request)
    organization_id = request.GET['org_id']
    # field_array = requestBody['fields']
    taxonomy_id = requestBody['taxonomy_id']
    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client[f'{organization_id}_pxm_database']


    properties_collection = mydb['Properties']
    field_names = requestBody['field_names']
    field_array = []
    for field_name in field_names:
        field_array.append(properties_collection.find_one({'field_name':field_name},{'_id':0, 'field_id':1}))
    
    field_association_collection = mydb['Fields_associated']

    associate_field_to_insert = []

    for field_id in field_array:
        associate_field_to_insert.append({
            'taxonomy_id':taxonomy_id,
            'field_id':field_id['field_id']
        })

    field_association_collection.delete_many({'taxonomy_id':taxonomy_id})

    field_association_collection.insert(associate_field_to_insert)

    response_message['message'] = 'Field associated to taxonomy successfully'
    response_message['status'] = 'Ok'

    return JsonResponse(response_message, status=200)






# def create_admin_user(request):
#     try:
#         requestBody  = JSONParser().parse(request)
#         user_name = requestBody['user_name']
#         user_email = requestBody['email_id']
#         user_password = requestBody['password']
#         newSuperUser = Super_user(user_name = user_name, user_email = user_email, password = user_password)
#         newSuperUser.save()

#         response_message['message'] = 'Admin user created successfully'
#         response_message['status'] = 'Ok'

#         return JsonResponse( response_message,status=200)
#     except Exception:
#         return JsonResponse({"Exception":"Some exception occured"})


# def add_user_to_organisation(request):
#     requestBody = JSONParser().parse(request)

#     new_user = User(organization_id = requestBody['organization_id'], user_name = requestBody["user_name"], 
#                     email_id = requestBody['email_id'], password = requestBody['password'], 
#                     user_permission = requestBody['user_permission'], 
#                     created_by = requestBody['created_by'])
#     new_user.save()

#     response_message['message'] = 'User created successfully'
#     response_message['status'] = 'Ok'

#     return JsonResponse(response_message, status = 200)