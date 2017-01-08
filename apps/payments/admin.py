from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'project_code', 'amount_usd',
                    'amount_btc', 'from_address', 'to_address',)
    list_filter = ('status', 'created_at', 'updated_at')
    fields = (
        'site', 'project', 'email', 'from_address', 'to_address', 'amount_usd'
    )

    def project_code(self, obj):
        return obj.project.code.hex
