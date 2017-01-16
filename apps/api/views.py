import uuid
import decimal
import json
import moneywagon
from django.core.cache import cache
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.utils.cache import get_cache_key
from core.views import CSRFExemptMixin
from payments.models import Transaction
from site_ext.models import SiteExt
from .forms import CallbackForm
from .tasks import send_receipt
from .tasks import send_callback
from .tasks import check_transaction


class TransactionAPIView(CSRFExemptMixin, View):
    """Create transaction view.

    Request:
    {
        "token": "...",
        "project_code": "...",
        "amount_usd": 10.12,
        "email": "..."
    }
    Response:
    {
        "url": "http://<gateway.com>/<transaction uuid4>/"
    }
    or
    {
        "errors": ["email required", "wrong project_code"]
    }
    """
    def get_data(self):
        """
        Extract request body data as JSON
        """
        return json.loads(self.request.body.decode('utf-8'))

    def verify(self, data):
        """Verification happens here
        """
        errors = {
            'errors': []
        }
        error = lambda x: errors['errors'].append(x)

        if not data.get('email'):
            error(_('email is required'))

        if not data.get('project_code'):
            error(_('project_code is required'))

        if not data.get('token'):
            error(_('token is required'))

        if not data.get('amount_usd'):
            error(_('amount_usd is required'))

        if data.get('project_code') and data.get('email'):
            if Transaction.objects.filter(project_code=data.get('project_code'),
                                          email=data.get('email')).count():
                error(_('project_code and email already exist'))

        if errors['errors']:
            return errors, False
        return errors, True

    def post(self, request, *args, **kwargs):
        """Create transaction
        """
        data = self.get_data()

        errors, is_verified = self.verify(data)

        try:
            site = SiteExt.objects.get(token=data['token']).site
        except:
            errors['errors'].append('site/token pair does not exist')
            is_verified = False

        if is_verified:
            transaction = Transaction(
                status=Transaction.STATUS_UNCONFIRMED,
                site=site,
                email=data['email'],
                project_code=data['project_code'],
                amount_usd=data['amount_usd'],
            )
            transaction.save()
            check_transaction.apply_async(kwargs={
                                            'transaction_id': transaction.id},
                                          eta=transaction.ends_at())
            url = '{scheme}://{host}{url}'.format(
                scheme=request.scheme,
                host=request.get_host(),
                url=transaction.get_absolute_url()
            )
            return JsonResponse({"url": url})
        return JsonResponse(errors)


class CallbackAPIView(CSRFExemptMixin, View):
    """Receive notification from blockonomics on transaction success
    """
    def get_form(self):
        return CallbackForm(data=self.request.GET or None)

    def get(self, request, *args, **kwargs):
        """Support for https://www.blockonomics.co/views/api.html#httpcallback
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return HttpResponse(status=400)

    def form_valid(self, form):
        data = form.cleaned_data
        if data['secret'] != '45c75bd587ab4a5b94163c7c741c1dec':
            return HttpResponse(status=400)

        try:
            transaction = Transaction.objects.get(to_address=data['addr'])
        except Transaction.DoesNotExist:
            return HttpResponse(status=400)

        transaction.status = data['status']
        transaction.txid = data['txid']
        SATOSHI = decimal.Decimal("0.00000001")
        transaction.amount_paid += SATOSHI * data['value']
        transaction.save()

        context = {'transaction_id': transaction.id}
        send_receipt.apply_async(kwargs=context)
        send_callback.apply_async(kwargs=context)
        return HttpResponse()


class ExchangeRateAPIView(View):
    """Get the latest exchange rate btc <-> usd

    GET request:
    /api/v1/exchange/

    Response:
    {
        "rate": 905.99
    }
    """
    def get(self, request, *args, **kwargs):
        if not cache.has_key('rate'):
            try:
                current_price = moneywagon.get_current_price('btc', 'usd')[0]
            except:
                current_price = moneywagon.get_current_price('btc', 'usd')
            cache.set('rate', current_price)
        rate = cache.get('rate')

        return JsonResponse({
            "rate": rate
        })
