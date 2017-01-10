import json
from django.views import View
from django.http import JsonResponse
from core.views import CSRFExemptMixin
from payments.models import Transaction
from site_ext.models import SiteExt


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
        "error": "error message"
    }
    """
    def get_data(self):
        """
        Extract request body data as JSON
        """
        return json.loads(self.request.body.decode('utf-8'))

    def post(self, request, *args, **kwargs):
        """Create transaction
        """
        data = self.get_data()
        site = SiteExt.objects.get(token=data['token']).site

        transaction = Transaction(
            status=Transaction.STATUS_UNCONFIRMED,
            site=site,
            email=data['email'],
            project_code=data['project_code'],
            amount_usd=data['amount_usd'],
        )
        transaction.save()
        url = '{scheme}://{host}{url}'.format(
            scheme=request.scheme,
            host=request.get_host(),
            url=transaction.get_absolute_url()
        )
        return JsonResponse({"url": url})
