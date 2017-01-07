from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

admin.site.site_header = settings.ADMIN_SITE_HEADER


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name="home.html"), name="home"),
]
