from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'project_code', 'amount_usd',
                    'amount_btc', 'to_address', 'payment_sent')
    list_filter = ('status', 'created_at', 'updated_at')
    fields = (
        'site', 'project_code', 'email', 'to_address',
        'amount_usd'
    )
