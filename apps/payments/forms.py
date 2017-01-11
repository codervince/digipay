from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['amount_usd', 'email', 'to_address',
                  'from_address']