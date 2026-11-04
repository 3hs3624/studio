from django.urls import path
from django.contrib.auth.views import LogoutView
from desk import api, views

handler404 = 'desk.api.not_found'
handler500 = 'desk.api.server_error'
urlpatterns = [
    path('',views.home),path('login/',views.StudioLoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('portal/incidents',views.listing),path('portal/incidents/new',views.new_incident),
    path('portal/incidents/<uuid:id>',views.detail),
    path('work/incidents',views.listing,{'work':True}),
    path('work/incidents/<uuid:id>',views.detail,{'work':True}),
    path('assets',views.inventory),path('assets/<uuid:id>',views.inventory),
    path('cis',views.inventory,{'ci':True}),path('cis/<uuid:id>',views.inventory,{'ci':True}),path('admin/access',views.admin_access),
    path('api/v1/me',api.me),path('api/v1/incidents',api.incidents),
    path('api/v1/incidents/<uuid:id>',api.incident),path('api/v1/incidents/<uuid:id>/assign',api.assign),
    path('api/v1/incidents/<uuid:id>/transitions',api.transitions),
    path('api/v1/incidents/<uuid:id>/comments',api.comments),path('api/v1/incidents/<uuid:id>/activity',api.activity),
    path('api/v1/incidents/<uuid:id>/resources',api.resources),
    path('api/v1/incidents/<uuid:id>/resources/<uuid:link_id>',api.resource_delete),
    path('api/v1/assets',api.assets),path('api/v1/assets/<uuid:id>',api.assets),
    path('api/v1/cis',api.cis),path('api/v1/cis/<uuid:id>',api.cis),
    path('api/v1/admin/access',api.access),path('api/v1/admin/groups',api.groups),
    path('api/v1/admin/groups/<uuid:id>/members/<uuid:person_id>',api.members),
    path('api/v1/admin/persons/<uuid:id>/roles',api.grants),
]
