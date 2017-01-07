from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from payments.views import HomeView

admin.site.site_header = settings.ADMIN_SITE_HEADER


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),
]
