"""
URL configuration for LEX REGIS.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints will go here
    path('api/v1/documents/', include('apps.documents.api.urls')),
    path('api/v1/cases/', include('apps.cases.api.urls')),
    path('api/v1/accounts/', include('apps.accounts.api.urls')),
    path('api/v1/hearings/', include('apps.hearings.api.urls')),
    
    # Web UI Paths
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('cases/', include('apps.cases.urls', namespace='cases_ui')),
    path('documents/', include('apps.documents.urls', namespace='documents_ui')),
    path('hearings/', include('apps.hearings.urls', namespace='hearings_ui')),
    path('ai/', include('apps.ai.urls', namespace='ai')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('statistics/', include('apps.analytics.urls', namespace='analytics')),
    path('communication/', include('apps.communication.urls', namespace='communication')),
    path('law-firm/dashboard/', include(('apps.dashboard.urls', 'dashboard'), namespace='law_firm_dashboard')), # Placeholder
    path('consult/', include('apps.intake.urls', namespace='intake')),
    path('portal/lawyer/dashboard/', include('apps.lawyer_portal.urls', namespace='lawyer_portal')),
    path('client/dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('', include('apps.public_site.urls', namespace='public_site')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'apps.common.presentation.views.custom_permission_denied_view'
handler404 = 'apps.common.presentation.views.custom_page_not_found_view'
handler500 = 'apps.common.presentation.views.custom_server_error_view'
