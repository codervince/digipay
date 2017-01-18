import uuid
import decimal
import json
import datetime
import moneywagon
import requests
from django.core.cache import cache
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
from django.utils import timezone
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
            code = data.get('project_code')
            email = data.get('email')
            previous = Transaction.objects.filter(project_code=code)\
                .order_by('-created_at').first()
            if previous and previous.email != email:
                error(_('project code is already used by another email'))
            elif previous and previous.created_at + datetime.timedelta(minutes=settings.HOLD_TIMEOUT) > timezone.now():
                error(_('try again later'))

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
            eta = lambda x: transaction.ends_at() + datetime.timedelta(minutes=x)
            # 1 minute after transaction creation
            check_transaction.apply_async(
                kwargs={
                    'transaction_id': transaction.id,
                    'delete': False
                },
                eta=eta(1))
            # 3 minutes after transaction creation
            check_transaction.apply_async(
                kwargs={
                    'transaction_id': transaction.id,
                    'delete': False
                },
                eta=eta(3))
            # 5 minutes after transaction creation
            check_transaction.apply_async(
                kwargs={
                    'transaction_id': transaction.id,
                    'delete': False
                },
                eta=eta(5))
            # 7 minutes after transaction creation
            check_transaction.apply_async(
                kwargs={
                    'transaction_id': transaction.id,
                    'delete': False
                },
                eta=eta(7))
            # 10 minutes after transaction creation
            check_transaction.apply_async(
                kwargs={
                    'transaction_id': transaction.id,
                    'delete': False
                },
                eta=eta(10))
            # When settings.TIMER is out
            check_transaction.apply_async(
                kwargs={
                    'transaction_id': transaction.id,
                    'delete': False
                },
                eta=transaction.ends_at())
            # When settings.TIMER + settings.EXTRA_TIME is out
            check_transaction.apply_async(
                kwargs={ 'transaction_id': transaction.id}, eta=eta(settings.EXTRA_TIME))
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
        "rate": 905.99,
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


class PaymentStatusAPIView(View):
    """Payment status API endpoint

    GET request:
    /api/v1/transaction/status/?id=j234jk123j4kj1234kj

    Response:
    {
        "message": "Paid",
    }
    """
    def get(self, request, *args, **kwargs):
        mapping = {
            Transaction.STATUS_CONFIRMED: 'Paid',
            Transaction.STATUS_UNCONFIRMED: 'Awaiting payment',
            Transaction.STATUS_PARTIALLY_CONFIRMED: 'Partially paid'
        }
        transaction = Transaction.objects.get(id=request.GET.get('id'))

        data = '{"addr":"%s"}' % transaction.to_address
        r = requests.post('https://www.blockonomics.co/api/balance',
                          data=data)
        response = json.loads(r.content.decode('utf-8'))
        record = response['response'][0]
        if record['confirmed'] and not record['unconfirmed']:
            transaction.status = transaction.STATUS_CONFIRMED
        else:
            transaction.status = transaction.STATUS_PARTIALLY_CONFIRMED
        transaction.save()

        return JsonResponse({
            "message": mapping[transaction.status]
        })
