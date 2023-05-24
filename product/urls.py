from django.urls import path
from . import views


# # pymongo urls
# urlpatterns = [
#     path('addfields',views.create_new_field, name = 'newfield'),
#     path('taxonomy',views.taxonomies, name = 'taxonomy'),
#     path('addorganization', views.create_organization, name = 'new_org'),
#     # path('adduser', views.add_user_to_organisation, name = 'adduse\r'),
#     path('addrecords', views.add_taxonomy_records, name = 'taxnomy_records'),
#     path('records', views.get_records_by_taxonomy, name = 'taxonomy_records'),
#     # path('createadmin', views.create_admin_user, name = 'admin_user'),
#     path('gettaxonomies', views.get_taxonomy_by_organization, name = 'get_taxonomy'),
#     path('gettaxonomyfields', views.get_all_field_by_taxonomy, name = 'taxonomy_fields'),
#     path("addpropertygroup", views.add_property_group, name = 'property_group'),
#     path('deleterecords', views.delete_taxonomy_records, name = 'deletetaxonomyrecords'),
#     # path('removefieldfromtaxonomy', views.dis_associate_field_from_taxonomy,name='disassociatefieldfromtaxonomy'),
#     path('associatefield', views.associate_field_to_taxonomy, name = 'associatefieldwithtaxonomy'),
#     path('allfields', views.get_all_properties, name = 'getallfields')
# ]

urlpatterns = [
    path('fields',views.fields, name = 'newfield'),
    path('taxonomies',views.taxonomies, name = 'taxonomy'),
    path('organizations', views.create_organization, name = 'new_org'),
    path('records', views.taxonomy_records, name = 'taxnomy_records'),
    path('taxonomy-fields', views.get_all_field_by_taxonomy, name = 'taxonomy_fields'),
    path("property-groups", views.property_groups, name = 'property_group'),
    path('associatefields', views.associate_field_to_taxonomy, name = 'associatefieldwithtaxonomy'),
]