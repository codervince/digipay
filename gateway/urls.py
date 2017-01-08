from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from payments.views import HomeView
from payments.views import TransactionView
from api.views import TransactionAPIView

admin.site.site_header = settings.ADMIN_SITE_HEADER


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^api/v1/transaction/$', TransactionAPIView.as_view(),
        name='transaction_api'),
    url(r'^(?P<uuid>.{32})/$', TransactionView.as_view(), name='transaction'),
]
