from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from core.models import BaseModel


class Transaction(BaseModel):
    """Transactions storing data
    """
    STATUS_UNCONFIRMED = 0
    STATUS_PARTIALLY_CONFIRMED = 1
    STATUS_CONFIRMED = 2
    STATUS_CHOICES = (
        (STATUS_UNCONFIRMED, _('Unconfirmed')),
        (STATUS_PARTIALLY_CONFIRMED, _('Partially Confirmed')),
        (STATUS_CONFIRMED, _('Confirmed')),
    )

    site = models.ForeignKey(Site, null=True)
    email = models.EmailField(null=True)
    project_code = models.CharField(max_length=34, null=True)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    amount_btc = models.DecimalField(max_digits=10, decimal_places=2,
                                     editable=False)
    from_address= models.CharField(max_length=34, null=True)
    to_address = models.CharField(max_length=34, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True,
                                 editable=False)

    def __str__(self):
        return '{0}: {1}'.format(self.from_address, self.to_address)

    class Meta:
       db_table = 'transactions'

