import uuid
import decimal
import json
import datetime
import moneywagon
import requests
from django.core.validators import URLValidator
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
from payments.utils import check
from site_ext.models import SiteExt
from .forms import CallbackForm
from payments.tasks import send_receipt
from payments.tasks import send_webhook
from .tasks import check_transaction


class TransactionAPIView(CSRFExemptMixin, View):
    """Create transaction view.

    Request:
    {
        "token": "...",
        "project_code": "...",
        "amount_btc": 10.12,
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

        if not data.get('amount_btc'):
            error(_('amount_btc is required'))
        
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
        try:
            data = self.get_data()
        except:
            return JsonResponse(
                    {'errors': "wrong request body. It must be json"},
                    status=400)

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
                amount_btc=data['amount_btc'],
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
        return JsonResponse(errors, status=400)


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
        if data['secret'] != settings.SECRET:
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
        send_webhook.apply_async(kwargs=context)
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
        id = request.GET.get('id')
        if not id:
            return JsonResponse({'message': ""})

        # Add to the queue
        # queue = cache.get('payment_status_queue', set([]))
        # if not queue:
        #     queue = set([id])
        # cache.set('payment_status_queue', queue, 60 * 60 * 24)

        # We don't make calls to the API due to API limit on 2 req/minute
        transaction = Transaction.objects.get(id=id)

        message = mapping[transaction.status]
        if transaction.txid:
            message += ' %s' % transaction.txid
        return JsonResponse({
            "message": message
        })


class TransactionsLatestAPIView(View):
    """Returns the latest confirmed transactions for the last
    settings.LATEST_TX_NU minutes
    """

    def prepare(self, tx):
        """Prepare data per transaction
        """
        return {
            'project_code': tx.project_code,
            'email': tx.email,
            'status': tx.get_status_display(),
            'transaction_id': tx.id.hex,
            'txid': tx.txid
        }

    def is_authenticated(self):
        secret = self.request.GET.get('secret')
        if any([not secret, secret != settings.SECRET]):
            return False
        return True

    def get_transactions(self, token):
        gte = timezone.now() - datetime.timedelta(
            minutes=settings.LATEST_TX_NU)

        params = {
            'updated_at__gte': gte,
            'status': Transaction.STATUS_CONFIRMED,
            'site__site_ext__token': token
        }

        return Transaction.objects.filter(**params)

    def get(self, request, *args, **kwargs):
        if not self.is_authenticated():
            return JsonResponse(data={
                "error": _("Invalid secret key")
            }, status=400)

        try:
            token = uuid.UUID(self.request.GET.get('token'))
        except:
            return JsonResponse(data={
                "error": "Invalid token supplied"}, status=400)
        if not SiteExt.objects.filter(token=token).count():
            return JsonResponse(data={
                "error": "There is no valid token"}, status=400)

        transactions = self.get_transactions(token)
        data = {
            'transactions': [self.prepare(tx) for tx in transactions]
        }
        return JsonResponse(data)
