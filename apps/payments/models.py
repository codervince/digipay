from django.db import models
from core.models import BaseModel


class Transaction(BaseModel):
   """Transactions storing data
   """
   email = models.EmailField(null=True)
   hash = models.UUIDField(null=True)
   project_code = models.CharField(max_length=255, null=True)
   amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
   amount_btc = models.DecimalField(max_digits=10, decimal_places=2)
   to_address = models.TextField(null=True, blank=True)

   class Meta:
       db_table = 'transactions'

