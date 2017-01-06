from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('email', 'hash', 'project_code', 'amount_usd',
                    'amount_btc', 'to_address',)
    list_filter = ('created_at', 'updated_at')
