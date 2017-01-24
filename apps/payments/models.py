import sys
import uuid
import datetime
import decimal
import qrcode
import qrcode.image.svg
import io
import moneywagon
import requests
import urllib
from django.core.cache import cache
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from core.models import BaseModel


class Payment(BaseModel):
    """Storing payments
    """
    STATUS_UNCONFIRMED = 0
    STATUS_PARTIALLY_CONFIRMED = 1
    STATUS_CONFIRMED = 2
    STATUS_INITIATED = 3
    STATUS_CHOICES = (
        (STATUS_INITIATED, _('Initiated')),
        (STATUS_UNCONFIRMED, _('Unconfirmed')),
        (STATUS_PARTIALLY_CONFIRMED, _('Partially Confirmed')),
        (STATUS_CONFIRMED, _('Confirmed')),
    )
    txid = models.CharField(max_length=255, null=True)
    transaction = models.ForeignKey('Transaction', null=True)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=8,
                                      null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True,
                                 editable=False)


class Transaction(BaseModel):
    """Transactions storing data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    txid = models.CharField(max_length=255, blank=True, null=True)
    STATUS_UNCONFIRMED = 0
    STATUS_PARTIALLY_CONFIRMED = 1
    STATUS_CONFIRMED = 2
    STATUS_INITIATED = 3
    STATUS_CHOICES = (
        (STATUS_INITIATED, _('Initiated')),
        (STATUS_UNCONFIRMED, _('Unconfirmed')),
        (STATUS_PARTIALLY_CONFIRMED, _('Partially Confirmed')),
        (STATUS_CONFIRMED, _('Confirmed')),
    )

    payment_sent = models.BooleanField(default=False, blank=True)
    site = models.ForeignKey(Site, null=True)
    email = models.EmailField(null=True)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2,
                                     blank=True, null=True)
    amount_btc = models.DecimalField(max_digits=18, decimal_places=8,
                                     editable=False, null=True)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=8,
                                      default=decimal.Decimal('0'),
                                      null=True)
    to_address = models.CharField(max_length=34, null=True)
    webhook = models.URLField(blank=True, null=True)
    project_code = models.UUIDField(default=uuid.uuid4, editable=False,
                                    null=True)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_INITIATED, null=True,
                                 editable=False)
    is_emailed = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return '{0}'.format(self.id.hex)

    def get_rate(self):
        if not cache.has_key('rate'):
            try:
                current_price = moneywagon.get_current_price('btc', 'usd')[0]
            except:
                current_price = moneywagon.get_current_price('btc', 'usd')
            cache.set('rate', current_price)
        return decimal.Decimal(cache.get('rate'))

    def qr(self):
        """Generate QR code for bitcoins
        https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki#Examples
        """
        schema = 'bitcoin:{to_address}?amount={amount}&label={label}'
        parsed = schema.format(
            to_address=self.to_address,
            amount=self.amount_btc,
            label=urllib.parse.urlencode({
                "label": "{site}:{project_code}".format(
                    site=self.site.domain,
                    project_code=self.project_code
                )
            })[6:]
        )
        qr = qrcode.make(parsed, image_factory=qrcode.image.svg.SvgImage)
        buffer = io.BytesIO()
        qr.save(buffer)
        return buffer.getvalue()

    def qr_schema(self):
        schema = 'bitcoin:{to_address}?label={label}&amount='
        parsed = schema.format(
            to_address=self.to_address,
            label=urllib.parse.urlencode({
                "label": "{site} {project_code}".format(
                    site=self.site.domain,
                    project_code=self.project_code
                )
            })[6:]
        )
        return parsed

    def save(self):
        first = Transaction.objects.filter(
            project_code=self.project_code).first()

        # Don't allow to save new transaction for other email if project_code
        # was used with another email initially
        if first and first.email != self.email:
            return

        if not self.amount_btc:
            self.amount_btc = round(
                decimal.Decimal(self.amount_usd)/self.get_rate(), 8)

        if not self.to_address:
            url = 'https://www.blockonomics.co/api/new_address';
            api_key = self.site.site_ext.api_key
            if api_key:
                headers = {'Authorization': "Bearer " + api_key}
                r = requests.post(url, headers=headers)
                self.to_address = r.json().get('address')
        return super(Transaction, self).save()

    def get_absolute_url(self):
        return reverse('transaction', args=(self.id.hex,))

    def ends_at(self):
        return self.created_at + datetime.timedelta(minutes=settings.TIMER)

    class Meta:
        db_table = 'transactions'
