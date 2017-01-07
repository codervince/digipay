from django.views.generic import TemplateView
from .models import Transaction


class HomeView(TemplateView):
    """View to show landing page and create transaction via API
    """
    template_name = 'home.html'

    # def post(self, request, *args, **kwargs):

