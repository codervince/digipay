import uuid
import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from core.models import BaseModel


class Transaction(BaseModel):
    """Transactions storing data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_UNCONFIRMED = 0
    STATUS_PARTIALLY_CONFIRMED = 1
    STATUS_CONFIRMED = 2
    STATUS_CHOICES = (
        (STATUS_UNCONFIRMED, _('Unconfirmed')),
        (STATUS_PARTIALLY_CONFIRMED, _('Partially Confirmed')),
        (STATUS_CONFIRMED, _('Confirmed')),
    )

    payment_sent = models.BooleanField(default=False, blank=True)
    site = models.ForeignKey(Site, null=True)
    email = models.EmailField(null=True)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    amount_btc = models.DecimalField(max_digits=10, decimal_places=2,
                                     editable=False, null=True)
    from_address = models.CharField(max_length=34, null=True)
    to_address = models.CharField(max_length=34, null=True)
    project_code = models.UUIDField(default=uuid.uuid4, editable=False,
                                    null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True,
                                 editable=False)

    def __str__(self):
        return '{0}: {1}'.format(self.from_address, self.to_address)

    def get_absolute_url(self):
        return reverse('transaction', args=(self.id.hex,))

    def ends_at(self):
        return self.created_at + datetime.timedelta(minutes=settings.TIMER)

    class Meta:
        db_table = 'transactions'
        unique_together = (('project_code', 'email'),)
