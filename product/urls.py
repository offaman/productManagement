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


# urlpatterns = [
#     path('fields',views1.fields, name = 'newfield'),
#     path('taxonomies',views1.taxonomies, name = 'taxonomy'),
#     path('organizations', views1.create_organization, name = 'new_org'),
#     path('records', views1.taxonomy_records, name = 'taxnomy_records'),
#     path('taxonomy-fields', views1.get_all_field_by_taxonomy, name = 'taxonomy_fields'),
#     path("property-groups", views1.property_groups, name = 'property_group'),
#     path('associatefields', views1.associate_field_to_taxonomy, name = 'associatefieldwithtaxonomy'),
# ]


urlpatterns = [
    path('organizations', views.Organization.as_view(), name = 'organizations'),
    path('taxonomies', views.Taxonomies.as_view(), name = 'taxonomies'),
    path('fields', views.Fields.as_view(), name = 'fields'),
    path('taxonomy-records', views.Taxonomy_records.as_view(), name = 'taxonomy-records'),
    path('property-groups', views.Property_groups.as_view(), name = 'property-groups'),
    path('associate-field', views.Fields_association.as_view(),name = 'field-association'),
    path('records', views.All_records.as_view(), name = 'all-records'),
    path('findrecord', views.Search.as_view()),
    path('taxonomy-fields',views.Fields_by_taxonomy.as_view()),
    # path('test/<slug:org_id>', views.Test_view.as_view())
]