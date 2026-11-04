from django.urls import path
from django.contrib.auth.views import LogoutView
from desk import api, views, asset_views

handler404 = 'desk.api.not_found'
handler500 = 'desk.api.server_error'
urlpatterns = [
    path('',views.home),path('login/',views.StudioLoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('portal/incidents',views.listing),path('portal/incidents/new',views.new_incident),
    path('portal/incidents/<uuid:id>',views.detail),
    path('work/incidents',views.listing,{'work':True}),
    path('work/incidents/<uuid:id>',views.detail,{'work':True}),
    path('assets',asset_views.listing),path('assets/new',asset_views.new),path('assets/<uuid:id>',asset_views.detail),
    path('my-assets',asset_views.mine),
    path('cis',views.inventory,{'ci':True}),path('cis/<uuid:id>',views.inventory,{'ci':True}),path('admin/access',views.admin_access),
    path('api/v1/me',api.me),path('api/v1/incidents',api.incidents),
    path('api/v1/incidents/<uuid:id>',api.incident),path('api/v1/incidents/<uuid:id>/assign',api.assign),
    path('api/v1/incidents/<uuid:id>/transitions',api.transitions),
    path('api/v1/incidents/<uuid:id>/comments',api.comments),path('api/v1/incidents/<uuid:id>/activity',api.activity),
    path('api/v1/incidents/<uuid:id>/resources',api.resources),
    path('api/v1/incidents/<uuid:id>/resources/<uuid:link_id>',api.resource_delete),
    path('api/v1/assets',api.assets),path('api/v1/assets/<uuid:id>',api.assets),
    path('api/v1/assets/<uuid:id>/actions',api.asset_actions),path('api/v1/assets/<uuid:id>/history',api.asset_history),
    path('api/v1/my/assets',api.my_assets),path('api/v1/my/asset-history',api.my_asset_history),
    path('api/v1/cis',api.cis),path('api/v1/cis/<uuid:id>',api.cis),
    path('api/v1/admin/access',api.access),path('api/v1/admin/groups',api.groups),
    path('api/v1/admin/groups/<uuid:id>/members/<uuid:person_id>',api.members),
    path('api/v1/admin/persons/<uuid:id>/roles',api.grants),
    path('work/sla',views.sla_settings),path('notifications',views.notifications),
    path('api/v1/sla/calendars',api.sla_calendars),path('api/v1/sla/policies',api.sla_policies),
    path('api/v1/notifications',api.notifications),path('api/v1/notifications/<uuid:id>/read',api.notification_read),
    path('catalog',views.catalog_listing),path('catalog/items/<uuid:id>',views.catalog_detail),
    path('work/catalog',views.catalog_manage),path('portal/requests',views.request_listing),
    path('work/requests',views.request_listing,{'work':True}),path('approvals',views.request_listing,{'approvals':True}),
    path('portal/requests/<uuid:id>',views.request_detail),
    path('api/v1/catalog/items',api.catalog_items),path('api/v1/catalog/items/<uuid:id>',api.catalog_items),
    path('api/v1/catalog/versions',api.catalog_versions),path('api/v1/requests',api.service_requests),
    path('api/v1/requests/<uuid:id>',api.service_request),path('api/v1/requests/<uuid:id>/assign',api.request_assignment),
    path('api/v1/requests/<uuid:id>/actions',api.request_action),path('api/v1/requests/<uuid:id>/decision',api.request_decision),
    path('api/v1/requests/<uuid:id>/comments',api.request_comments),path('api/v1/approvals',api.approvals),
]
