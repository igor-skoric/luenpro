from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('', include('apps.website.urls')),
    path('', include('apps.portal.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
