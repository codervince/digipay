import json
from django.views import View
from django.http import JsonResponse
from django.utils.translation import ugettext as _
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

        print(data)
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
            url = '{scheme}://{host}{url}'.format(
                scheme=request.scheme,
                host=request.get_host(),
                url=transaction.get_absolute_url()
            )
            return JsonResponse({"url": url})
        return JsonResponse(errors)
