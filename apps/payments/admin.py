from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'project_code', 'amount_usd',
                    'amount_btc', 'to_address', 'txid', 'amount_paid')
    list_filter = ('status', 'created_at', 'updated_at')
    fields = (
        'site', 'email', 'to_address', 'amount_usd'
    )
