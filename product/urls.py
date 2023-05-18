from django.urls import path
from . import views


# pymongo urls
urlpatterns = [
    path('addfields',views.create_new_field, name = 'newfield'),
    path('addtaxonomy',views.create_taxonomy, name = 'taxonomy'),
    # path('allrecords', views.get_all, name = "getallrecords"),
    path('addorganization', views.create_organization, name = 'new_org'),
    path('adduser', views.add_user_to_organisation, name = 'adduse\r'),
    path('addrecords', views.add_taxonomy_records, name = 'taxnomy_records'),
    path('records', views.get_records_by_taxonomy, name = 'taxonomy_records'),
    # path('addfields', views.create_taxonomy_fields, name = 'fields'),
    path('createadmin', views.create_admin_user, name = 'admin_user'),
    path('gettaxonomies', views.get_taxonomy_by_organization, name = 'get_taxonomy'),
    path('gettaxonomyfields', views.get_all_field_by_taxonomy, name = 'taxonomy_fields'),
    path("addpropertygroup", views.add_property_group, name = 'property_group')
]

# urlpatterns = [
#     path('add', views.insert_user, name= 'adduser')
# ]