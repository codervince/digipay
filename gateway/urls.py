from django.conf.urls import url
from django.contrib import admin
from django.conf import settings

admin.site.site_header = settings.ADMIN_SITE_HEADER


urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
