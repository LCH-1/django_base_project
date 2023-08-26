from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView

from base_project import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include("user.urls")),
    path('api/fileserver/', include('fileserver.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        path('scheme/', SpectacularAPIView.as_view(), name='schema'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

else:
    urlpatterns += static(settings.STATIC_URL, view=views.static_view, document_root=settings.STATIC_ROOT)
