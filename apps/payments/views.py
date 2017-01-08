from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Transaction


class HomeView(TemplateView):
    """View to show landing page and create transaction via API
    """
    template_name = 'home.html'


class TransactionView(TemplateView):
    """Page to handle transaction payments
    """
    template_name = 'transaction.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'transaction': get_object_or_404(Transaction, id=kwargs['uuid'])
        })
        return super(TransactionView, self).get_context_data(**kwargs)
