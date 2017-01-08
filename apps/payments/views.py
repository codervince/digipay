from django.views.generic import TemplateView
from .models import Transaction


class HomeView(TemplateView):
    """View to show landing page and create transaction via API
    """
    template_name = 'home.html'


class TransactionView(TemplateView):
    """Page to handle transaction payments
    """
    template_name = 'transaction.html'

    def get_object(self):
        import ipdb; ipdb.set_trace()
