from django import forms
from payments.models import Transaction


class CallbackForm(forms.Form):
    """Form used to validate and serialize callback data into python objects
    """

    txid = forms.CharField()
    status = forms.ChoiceField(choices=Transaction.STATUS_CHOICES)
    addr = forms.CharField(max_length=255)
    value = forms.IntegerField()
    secret = forms.CharField()
