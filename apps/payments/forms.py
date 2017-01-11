from django import forms
from .models import Transaction
from .models import Payment


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['amount_usd', 'email', 'to_address']


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ['txid', 'amount_paid']
