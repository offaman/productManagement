from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from .models import  Organisation
import pymongo
import uuid
from django.utils import timezone 
from .validations.validation import validateInputTaxonomyData
from .utilities.utils import MyException
from django.views import View
from .pagination import paginate
import math


COLLECTION_PER_ORG = ['Properties', 'Taxonomies', 'Validation', 'Fields_associated', 'Property_groups', 'Records']
RECORDS_PER_PAGE = 2

class Organization(View):
    response_message = {}

    def post(self,request):
        requestBody  = JSONParser().parse(request)
            # create organization with specified name
        org_unique_id = str(uuid.uuid4())
        organization_added = Organisation(_id = org_unique_id, organization_name = requestBody['organization_name'], create_by = requestBody['creator'])
        organization_added.save()
            # create a new collection with recent added org_id_pxm_database and create diff collection into it.
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{org_unique_id}_pxm_database']
        for collection in COLLECTION_PER_ORG:
            mydb.create_collection(collection)
    
        self.response_message['message'] = 'Organization created successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status=200)