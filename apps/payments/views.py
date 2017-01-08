import uuid
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from .models import Transaction


class HomeView(TemplateView):
    """View to show landing page and create transaction via API
    """
    template_name = 'home.html'


class TransactionView(TemplateView):
    """Page to handle transaction payments
    """
    template_name = 'transaction.html'

    def test_func(self):
        if self.get_object().end_date() > timezone.now():
            return True
        return False

    def get_id(self):
        return uuid.UUID(self.kwargs['uuid'])

    def get_object(self):
        return get_object_or_404(Transaction, id=self.get_id())

    def get_context_data(self, **kwargs):
        kwargs.update({
            'transaction': self.get_object()
        })
        return super(TransactionView, self).get_context_data(**kwargs)

    def dispatch(self, *args, **kwargs):
        if not self.test_func():
            raise Http404()
        return super(TransactionView, self).dispatch(*args, **kwargs)
