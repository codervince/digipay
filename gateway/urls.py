from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from payments.views import HomeView
from payments.views import TransactionView
from payments.views import PaymentSentView
from api.views import TransactionAPIView
from api.views import TransactionsLatestAPIView
from api.views import CallbackAPIView
from api.views import ExchangeRateAPIView
from api.views import PaymentStatusAPIView

admin.site.site_header = settings.ADMIN_SITE_HEADER


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^(?P<uuid>.{32})/sent/$', PaymentSentView.as_view(),
        name='payment_sent'),
    url(r'^api/v1/callback/$', CallbackAPIView.as_view(), name='callback_api'),
    url(r'^api/v1/transaction/$', TransactionAPIView.as_view(),
        name='transaction_api'),
    url(r'^api/v1/transaction/status/$', PaymentStatusAPIView.as_view(),
        name='payment_status_api'),
    url(r'^api/v1/exchange/$', ExchangeRateAPIView.as_view(),
        name='exchange_api'),
    url(r'^(?P<uuid>.{32})/$', TransactionView.as_view(), name='transaction'),
    url(r'^api/v1/transactions/latest/$', TransactionsLatestAPIView.as_view(),
        name='transactions_latest_api')
]
