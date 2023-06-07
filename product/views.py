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
RECORDS_PER_PAGE = 3


class Organization(View):
    response_message = {}

    def post(self,request):
        requestBody  = JSONParser().parse(request)
            # create organization with specified name
        org_unique_id = str(uuid.uuid4())
        organization_added = Organisation(organization_id = org_unique_id, organization_name = requestBody['organization_name'], create_by = requestBody['creator'])
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
        

class Taxonomies(View):
    response_message = {}
    def get(self, request):

        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        if request.GET.get('t_id',None):
            taxonomy_id = request.GET['t_id']
            taxonomy_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'_id':0, 'taxonomy_name':1})

            client.close()
            return JsonResponse(taxonomy_name,safe=False, status=200)
        else:
            all_taxonomies = list(mydb['Taxonomies'].find({},{'_id':0}))

            client.close()
            return JsonResponse(all_taxonomies,safe=False ,status = 200)
        # self.response_message['data'] = all_taxonomies
        
        # for taxonomy in list(all_taxonomies):
        #     # taxonomy_list.append(taxonomy['taxonomy_name'])
        #     taxonomies_list_object[taxonomy['taxonomy_name']] = taxonomy['taxonomy_id']
    def post(self, request):
        requestBody = JSONParser().parse(request)
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        mydb['Taxonomies'].insert_one({"taxonomy_name":requestBody['taxonomy_name'], 'taxonomy_id':str(uuid.uuid4())})

        mydb.create_collection(requestBody['taxonomy_name'])

        taxonomy_name = requestBody['taxonomy_name']
        taxonomy_id = mydb['Taxonomies'].find_one({'taxonomy_name': taxonomy_name},{"_id":0, 'taxonomy_id':1})
        properties_collection = mydb['Properties']

        if requestBody.get('Field_names',None):
            field_names = requestBody.get('Field_names')
            field_array = []
            for field_name in field_names:
                field_array.append(properties_collection.find_one({'field_name':field_name},{'_id':0, 'field_id':1}))
            
            field_association_collection = mydb['Fields_associated']

            associate_field_to_insert = []

            for field_id in field_array:
                associate_field_to_insert.append({
                    'taxonomy_id':taxonomy_id['taxonomy_id'],
                    'field_id':field_id['field_id']
                })

            field_association_collection.insert(associate_field_to_insert)

        self.response_message['message'] = 'Taxonomy created successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)
    
    def put(self, request):
        requestBody = JSONParser().parse(request)
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        taxonomy_name = requestBody['taxonomy_name']
        taxonomy_id = mydb['Taxonomies'].find_one({'taxonomy_name': taxonomy_name},{"_id":0, 'taxonomy_id':1})
        properties_collection = mydb['Properties']

        field_names = requestBody.get('Field_names',[])
        field_array = []
        for field_name in field_names:
            field_array.append(properties_collection.find_one({'field_name':field_name},{'_id':0, 'field_id':1}))
        
        field_association_collection = mydb['Fields_associated']
        associate_field_to_insert = []

        for field_id in field_array:
            associate_field_to_insert.append({
                'taxonomy_id':taxonomy_id['taxonomy_id'],
                'field_id':field_id['field_id']
            })

        field_association_collection.delete_many({'taxonomy_id':taxonomy_id['taxonomy_id']})

        if associate_field_to_insert:
            field_association_collection.insert(associate_field_to_insert)

        self.response_message['message'] = 'Fields associated successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)


    def delete(self,request):
        organization_id = request.GET['org_id']
        taxonomy_name = request.GET['taxonomy_name']

        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        taxonomy_id_delete = mydb['Taxonomies'].find_one({'taxonomy_name':taxonomy_name}, {'_id':0, 'taxonomy_id':1})

        mydb.drop_collection(taxonomy_name)
        mydb['Taxonomies'].delete_one({'taxonomy_name':taxonomy_name})
        mydb['Fields_associated'].delete_many({'taxonomy_id':taxonomy_id_delete['taxonomy_id']})

        self.response_message['message'] = 'Taxonomy deleted successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)
    
    def options(self, request) -> HttpResponse:
        return HttpResponse(status= 200)

class Fields(View):
    response_message = {}
    def get(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        if request.GET.get('t_id', None):
            taxonomy_id = request.GET['t_id']
            taxonomy =  mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'taxonomy_id':1,'_id':0})
            taxonomy_id = taxonomy['taxonomy_id']
            all_associated_fields = list(mydb['Fields_associated'].find({'taxonomy_id':taxonomy_id},{'field_id':1,'_id':0}))
            all_property_groups  = list(mydb['Property_groups'].find({},{'property_group_name':1, '_id':0}))

            property_group_list = []
            for group in all_property_groups:
                property_group_list.append(group['property_group_name'])

            property_group_mapped_fields = {}

            for p_group in property_group_list:
                property_group_mapped_fields[f"{p_group}"] = []
                for field in all_associated_fields:
                    if (mydb['Properties'].find_one({'property_group':p_group, 'field_id':field['field_id']})):
                        property_group_mapped_fields[f"{p_group}"].append(mydb['Properties'].find_one({'property_group':p_group, 'field_id':field['field_id']},{'_id':0,'created_at':0,'created_by':0,'taxonomy_id':0,'property_group':0})) 

            client.close()
            return JsonResponse(property_group_mapped_fields, safe=False)
        
        elif request.GET.get('field_id',None):
            field_id = request.GET['field_id']
            field_info = mydb['Properties'].find_one({'field_id':field_id},{'_id':0})
            if mydb['Fields_associated'].find({'field_id':field_id},{'_id':0}):
                associated_taxonomy_ids = list(mydb['Fields_associated'].find({'field_id':field_id},{'_id':0}))
                taxonomies_names = []
                for taxonomy_id in associated_taxonomy_ids:
                    taxonomy_name = mydb['Taxonomies'].find_one({'taxonomy_id': taxonomy_id['taxonomy_id']},{'_id':0})
                    taxonomies_names.append(taxonomy_name['taxonomy_name'])
                
                # for taxonomy_name in taxonomies_names:
                # taxonomies_names.append(taxonomy_name['taxonomy_name'])
                field_info['taxonomy_names'] = ", ".join(taxonomies_names)
            return JsonResponse(field_info, safe=False, status = 200)
        else:
            all_fields = list(mydb['Properties'].find({},{'_id':0,'created_at':0, 'created_by':0}))
            return JsonResponse(all_fields, safe=False)

    def post(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        properties_collection = mydb['Properties']
        requestBody = JSONParser().parse(request)

        field_unique_id = str(uuid.uuid4())
        requestBody['created_at'] = timezone.now()
        requestBody['field_id'] = field_unique_id
        properties_collection.insert_one(requestBody)
        self.response_message['message'] = 'Property created successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)
    

    def put(self, request):
        requestBody = JSONParser().parse(request)
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        field_id = request.GET['field_id']
        mydb['Properties'].update_one({'field_id':field_id},{'$set':requestBody})
        self.response_message['message'] = 'Property updated successfully'
        self.response_message['status'] = 'Ok'

        return JsonResponse(self.response_message, status = 200)

    def delete(self,request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        properties_collection = mydb['Properties']
        field_association_collection = mydb['Fields_associated']
        field_id = request.GET['field_id']

        field_id_todelete = properties_collection.find_one({'field_id':field_id},{'_id':0,'field_id':1})
        
        field_association_collection.delete_many({'field_id':field_id_todelete['field_id']})
        properties_collection.delete_one({'field_id':field_id})

        self.response_message['message'] = 'Property deleted successfully'
        self.response_message['status'] = 'Ok'
        
        client.close()
        return JsonResponse(self.response_message, status = 200)
    
    def options(self, request) -> HttpResponse:
        return HttpResponse(status= 200)
    
class Taxonomy_records(View):
    response_message = {}

    def get(self, request):
        taxonomy_id = request.GET.get('t_id')
        organization_id = request.GET.get('org_id')
        page_number = int(request.GET.get('page',1))
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        
        if page_number <= 0:
            page_number = 1
        records_to_skip = (int(page_number)-1)*RECORDS_PER_PAGE

        my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'taxonomy_name':1,'_id':0})

        baseURL = "http://172.16.3.214:8000/taxonomy-records?org_id={org_id}&t_id={taxonomy_id}&page={page_index}"

        if request.GET.get('record_id', None):
            record_id = request.GET['record_id']
            record_data  = mydb[my_taxonomy_collection_name['taxonomy_name']].find_one({'record_id':record_id},{'_id':0, 'validations':0})
            self.response_message = record_data
        else:
            total_records = mydb[my_taxonomy_collection_name['taxonomy_name']].find().count()
            paginated_Urls_object = paginate(organization_id, page_number, RECORDS_PER_PAGE, total_records, baseURL, taxonomy_id)
            self.response_message['meta_data'] = {}
            self.response_message['meta_data']['previous_page'] =  paginated_Urls_object['previous_page']
            self.response_message['meta_data']['next_page'] =  paginated_Urls_object['next_page']
            self.response_message['meta_data']['total_pages'] = math.ceil(total_records/RECORDS_PER_PAGE)
            self.response_message['meta_data']['records_per_page'] = RECORDS_PER_PAGE
            self.response_message['meta_data']['from_record_number'] = records_to_skip + 1
            if records_to_skip + RECORDS_PER_PAGE > total_records:
                self.response_message['meta_data']['to_record_number'] = total_records
            else:
                self.response_message['meta_data']['to_record_number'] = records_to_skip + RECORDS_PER_PAGE

            all_record_data  = list(mydb[my_taxonomy_collection_name['taxonomy_name']].find({},{'_id':0, 'validations':0}).skip(records_to_skip).limit(RECORDS_PER_PAGE))
            self.response_message['data'] = all_record_data

        client.close()
        return JsonResponse(self.response_message, safe=False ,status = 200)
    
    def post(self,request):

        requestBody = JSONParser().parse(request)
        taxonomy_name = requestBody['taxonomy_name']
        organization_id = request.GET.get('org_id')
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_name':taxonomy_name},{'taxonomy_name':1,'taxonomy_id':1,'_id':0})
        requestBody['taxonomy_id'] = my_taxonomy_collection_name['taxonomy_id']

        mydb['Records'].insert_one({'taxonomy_id':my_taxonomy_collection_name['taxonomy_id'],'record_id':requestBody['record_id']})

        # all_associated_fields_ids = list(mydb['Fields_associated'].find({'taxonomy_name':taxonomy_name},{'field_id':1,'_id':0}))
        # all_properties = []

        # for field in all_associated_fields_ids:
        #     all_properties.append(mydb['Properties'].find_one({'field_id':field['field_id']},{'_id':0,'created_at':0,'created_by':0, 'field_id':0,'taxonomy_id':0,'property_group':0})) 

        # validateInputTaxonomyData(requestBody, all_properties)
        # requestBody['record_id'] = str(uuid.uuid4())

        mydb[my_taxonomy_collection_name['taxonomy_name']].insert_one(requestBody)
        self.response_message['message'] = 'Data inserted successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)
    
    def put(self, request):
        requestBody = JSONParser().parse(request)
        taxonomy_name = requestBody['taxonomy_name']
        organization_id = request.GET.get('org_id')
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        record_id = request.GET['record_id']

        my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_name':taxonomy_name},{'taxonomy_name':1,'_id':0})
            # validateInputTaxonomyData(requestBody, all_properties)
        mydb[my_taxonomy_collection_name['taxonomy_name']].update_one({'record_id':record_id},{'$set':requestBody})
        self.response_message['message'] = 'Data updated successfully'
        self.response_message['status'] = 'Ok' 

        client.close()
        return JsonResponse(self.response_message, status = 200)

    def delete(self, request):
        requestBody = JSONParser().parse(request)
        taxonomy_name = requestBody['taxonomy_name']
        organization_id = request.GET.get('org_id')
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        record_id = request.GET['record_id']

        my_taxonomy_collection_name = mydb['Taxonomies'].find_one({'taxonomy_name':taxonomy_name},{'taxonomy_name':1,'_id':0})
        mydb[my_taxonomy_collection_name['taxonomy_name']].delete_one({'record_id':record_id})
        mydb['Records'].delete_one({'record_id':record_id})
        self.response_message['message'] = 'Data deleted successfully'
        self.response_message['status'] = 'Ok' 

        client.close()
        return JsonResponse(self.response_message, status = 200)       

    def options(self, request) -> HttpResponse:
        return HttpResponse(status= 200)

class Property_groups(View):
    response_message = {}
    def get(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        property_groups  = list(mydb['Property_groups'].find({},{'_id':0}))

        # for p_group in property_groups:
        #     self.response_message[p_group['property_group_name']] =  p_group['property_group_id']
        client.close()
        return JsonResponse(property_groups, safe=False, status = 200)
    

    def post(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        requestBody = JSONParser().parse(request)

        requestBody['property_group_id'] = str(uuid.uuid4())
        mydb['Property_groups'].insert_one(requestBody)

        self.response_message['message'] = 'Property group created successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)
    
    def put(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        requestBody = JSONParser().parse(request)
        property_group_id = request.GET['pgroup_id']

        old_property_group_name = mydb['Property_groups'].find_one({'property_group_id':property_group_id},{'property_group_name':1, '_id':0})

        mydb['Property_groups'].update_one({'property_group_id':property_group_id},{'$set':{'property_group_name':requestBody['property_group_name']}})

        mydb['Properties'].update_many({'property_group':old_property_group_name['property_group_name']},{'$set':{'property_group':requestBody['property_group_name']}})

        self.response_message['message'] = 'Property group updated successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200)   

    def delete(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        property_group_id = request.GET['pgroup_id']
        property_group_name = mydb['Property_groups'].find_one({'property_group_id':property_group_id})
        property_group = mydb['Property_groups'].delete_one({'property_group_id':property_group_id})

        mydb['Properties'].update_many({'property_group':property_group_name['property_group_name']},{'$set':{"property_group":"Unassigned"}})

        self.response_message['message'] = 'Property group deleted successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status = 200) 

    def options(self, request) -> HttpResponse:
        return HttpResponse(status= 200)

class Fields_association(View):
    response_message = {}
    def post(self, request):
        requestBody = JSONParser().parse(request)
        organization_id = request.GET['org_id']
        # taxonomy_id = requestBody['taxonomy_id']
        taxonomy_name = requestBody['taxonomy_name']

        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        taxonomy_id = mydb['Taxonomies'].find_one({'taxonomy_name': taxonomy_name},{"_id":0, 'taxonomy_id':1})

        properties_collection = mydb['Properties']
        field_names = requestBody['field_names']
        field_array = []

        for field_name in field_names:
            field_array.append(properties_collection.find_one({'field_name':field_name},{'_id':0, 'field_id':1}))
        
        field_association_collection = mydb['Fields_associated']

        associate_field_to_insert = []

        for field_id in field_array:
            associate_field_to_insert.append({
                'taxonomy_id':taxonomy_id['taxonomy_id'],
                'field_id':field_id['field_id']
            })

        field_association_collection.delete_many({'taxonomy_id':taxonomy_id})

        field_association_collection.insert(associate_field_to_insert)

        self.response_message['message'] = 'Field associated to taxonomy successfully'
        self.response_message['status'] = 'Ok'
        
        client.close()
        return JsonResponse(self.response_message, status=200)
    
    def options(self, request) -> HttpResponse:
        return HttpResponse(status= 200)

class All_records(View):
    response_message = {}
    def get(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        page_number = int(request.GET.get('page',1))
        if page_number <= 0:
            page_number = 1
        
        records_to_skip = (page_number-1) * RECORDS_PER_PAGE  

        if request.GET.get('record_id',None):
            record_id = request.GET['record_id']
            taxonomy_info = mydb['Records'].find_one({'record_id':record_id},{'taxonomy_id':1,'_id':0})
            taxonomy_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_info['taxonomy_id']})
            taxonomy_record = mydb[taxonomy_name['taxonomy_name']].find_one({'record_id':record_id},{'_id':0})
            client.close()
            return JsonResponse(taxonomy_record, safe= False)
        
        else:
            total_records = mydb['Records'].find().count()
            # my_taxonomy_collection_names = list(mydb['Taxonomies'].find({},{'_id':0, 'taxonomy_name':1}))
            # all_taxonomy_names = []
            # for taxonomy in my_taxonomy_collection_names:
            #     all_taxonomy_names.append(taxonomy['taxonomy_name'])

            # all_taxonomy_records =  []

            # # baseURL = "http://127.0.0.1:8000/records?org_id={org_id}&page={page_index}"

            # # pagingURL = {
            # #     'previous_page':baseURL.format(org_id  = organization_id,page_index = page_number + 1),
            # #     'next_page':baseURL.format(org_id  = organization_id, page_index=page_number - 1)
            # # }
            # # print(paginate(organization_id,page_number,RECORDS_PER_PAGE,total_records))


            # paginated_Urls_object = paginate(organization_id,page_number,RECORDS_PER_PAGE,total_records)


            # # if (paginated_Urls_object['previous_page']):
            # # if (paginated_Urls_object['next_page']):

            # self.response_message['previous_page'] =  paginated_Urls_object['previous_page']
            # self.response_message['next_page'] =  paginated_Urls_object['next_page']
            # self.response_message['total_pages'] = math.ceil(total_records/RECORDS_PER_PAGE)
            # self.response_message['records_per_page'] = RECORDS_PER_PAGE
            
            # current_taxonomy = all_taxonomy_names[0]
            # for taxonomy_name in all_taxonomy_names:
            #     if current_taxonomy == taxonomy_name:
            #         records = list(mydb[taxonomy_name].find({},{'_id':0}).skip(records_to_skip).limit(RECORDS_PER_PAGE))
            #     else:
            #         records = list(mydb[taxonomy_name].find({},{'_id':0}).limit(RECORDS_PER_PAGE))
            #         current_taxonomy = taxonomy_name
                
            #     [all_taxonomy_records.append(record) for record in records]

            #     if len(all_taxonomy_records) >= RECORDS_PER_PAGE:
            #         all_taxonomy_records = all_taxonomy_records[:RECORDS_PER_PAGE]
            #         self.response_message['data'] = all_taxonomy_records

            #         client.close()
            #         return JsonResponse(self.response_message, safe=False, status = 200)
                
            # self.response_message['data'] = all_taxonomy_records
            # return JsonResponse(self.response_message, safe=False, status = 200)
            records_to_fetch  = list(mydb['Records'].find({},{'_id':0}).skip(records_to_skip).limit(RECORDS_PER_PAGE))
            records_to_send  = []
            baseURL = "http://172.16.3.214:8000/records?org_id={org_id}&page={page_index}"


            paginated_Urls_object = paginate(organization_id,page_number,RECORDS_PER_PAGE,total_records, baseURL)
            self.response_message['meta_data'] = {}
            self.response_message['meta_data']['previous_page'] =  paginated_Urls_object['previous_page']
            self.response_message['meta_data']['next_page'] =  paginated_Urls_object['next_page']
            self.response_message['meta_data']['total_pages'] = math.ceil(total_records/RECORDS_PER_PAGE)
            self.response_message['meta_data']['records_per_page'] = RECORDS_PER_PAGE
            self.response_message['meta_data']['from_record_number'] = records_to_skip + 1
            if records_to_skip + RECORDS_PER_PAGE > total_records:
                self.response_message['meta_data']['to_record_number'] = total_records
            else:
                self.response_message['meta_data']['to_record_number'] = records_to_skip + RECORDS_PER_PAGE

            for record_info in records_to_fetch:
                record_id = record_info['record_id']
                taxonomy_id = record_info['taxonomy_id']
                taxonomy_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'_id':0,'taxonomy_name':1})
                record = mydb[taxonomy_name['taxonomy_name']].find_one({'record_id':record_id},{'_id':0})
                records_to_send.append(record)

            self.response_message['data'] = records_to_send
            return JsonResponse(self.response_message, safe=False)

    def put(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        record_id = request.GET['record_id']
        requestBody = JSONParser().parse(request)

        taxonomy_id = mydb['Records'].find_one({'record_id':record_id},{'_id':0, 'taxonomy_id':1})
        
        taxonomy_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id['taxonomy_id']},{'_id':0,'taxonomy_name':1})

        mydb[taxonomy_name['taxonomy_name']].update_one({'record_id':record_id},{'$set':requestBody})
        
        self.response_message['message'] = 'Record updated successfully'
        self.response_message['status'] = 'Ok'

        client.close()
        return JsonResponse(self.response_message, status=200)

    def delete(self, request):
        organization_id = request.GET['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        record_id = request.GET['record_id']

        taxonomy_id = mydb['Records'].find_one({'record_id':record_id},{'_id':0, 'taxonomy_id':1})
        taxonomy_name = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id['taxonomy_id']},{'_id':0,'taxonomy_name':1})
        mydb[taxonomy_name['taxonomy_name']].delete_one({'record_id':record_id})
        mydb['Records'].delete_one({'record_id':record_id})
        self.response_message['message'] = 'Record deleted successfully'
        self.response_message['status'] = 'Ok'
        return JsonResponse(self.response_message, safe= False)
    
    def options(self, request) -> HttpResponse:
        return HttpResponse(status= 200)

class Search(View):
    def get(self, request):
        organization_id = request.GET['org_id']
        page_number = int(request.GET.get('page',1))
        requestBody = JSONParser().parse(request)
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']
        records_to_skip = page_number-1

        if request.GET.get('t_id',None):
            taxonomy_id = request.GET['t_id']
            my_taxonomy = mydb['Taxonomies'].find_one({'taxonomy_id':taxonomy_id},{'_id':0, 'taxonomy_name':1})
            
            matched_records = list(mydb[my_taxonomy['taxonomy_name']].find({'record_id':{'$regex' : f'^{requestBody["text_to_search"]}.*'}},{'_id':0}).skip(records_to_skip).limit(RECORDS_PER_PAGE))
            client.close()
            return JsonResponse(matched_records, safe=False)
        
        else:
            my_taxonomy_collection_names = list(mydb['Taxonomies'].find({},{'_id':0, 'taxonomy_name':1}))
            all_taxonomy_names = []
            for taxonomy in my_taxonomy_collection_names:
                all_taxonomy_names.append(taxonomy['taxonomy_name'])
            matched_taxonomy_records = []

            for taxonomy in all_taxonomy_names:
                records = list(mydb[taxonomy].find({},{'_id':0}).skip(records_to_skip).limit(RECORDS_PER_PAGE))
                [matched_taxonomy_records.append(record) for record in records]

                if len(matched_taxonomy_records) == RECORDS_PER_PAGE:
                    client.close()
                    matched_taxonomy_records = matched_taxonomy_records[records_to_skip: records_to_skip + RECORDS_PER_PAGE]
            
            client.close()
            return JsonResponse(matched_taxonomy_records, safe=False, status = 200)


class Test_view(View):
    response_message = {}
    def get(self, request, *args , **kwargs):
        organization_id = self.kwargs['org_id']
        client = pymongo.MongoClient('mongodb://localhost:27017')
        mydb = client[f'{organization_id}_pxm_database']

        all_taxonomies = list(mydb['Taxonomies'].find({},{'_id':0}))

        # self.response_message['data'] = all_taxonomies
        # for taxonomy in list(all_taxonomies):
        #     # taxonomy_list.append(taxonomy['taxonomy_name'])
        #     taxonomies_list_object[taxonomy['taxonomy_name']] = taxonomy['taxonomy_id']
        client.close()
        return JsonResponse(all_taxonomies,safe=False ,status = 200)
    
class Fields_by_taxonomy(View):
        response_message = {}
        def get(self, request):
            organization_id = request.GET['org_id']
            taxonomy_id = request.GET['t_id']
            client = pymongo.MongoClient('mongodb://localhost:27017')
            mydb = client[f'{organization_id}_pxm_database']

            all_associated_fields = list(mydb['Fields_associated'].find({'taxonomy_id':taxonomy_id},{'field_id':1,'_id':0}))

            all_fields = []
            for field in all_associated_fields:
                all_fields.append(mydb['Properties'].find_one({'field_id':field['field_id']},{'_id':0}))
            
            client.close()
            return JsonResponse(all_fields,safe=False ,status = 200)