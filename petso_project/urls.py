from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Swagger API Documentation & Testing Interface
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', SpectacularSwaggerView.as_view(url_name='schema'), name='api-root'),
    
    # API Apps
    path('api/auth/', include('apps.users.urls')),
    path('api/farmers/', include('apps.farmers.urls')),
    path('api/vets/', include('apps.vets.urls')),
    path('api/companies/', include('apps.companies.urls')),
    path('api/ecommerce/', include('apps.ecommerce.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/medical/', include('apps.medical.urls')),
    path('api/social/', include('apps.social.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/system/', include('apps.system.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG or getattr(settings, 'SERVE_MEDIA_FROM_DJANGO', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
