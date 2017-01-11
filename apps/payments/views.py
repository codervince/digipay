import uuid
from django.core.cache import cache
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from .forms import TransactionForm
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
        if self.get_object().ends_at() > timezone.now():
            return True
        return False

    def get_form(self):
        return TransactionForm(data=self.request.POST or None,
                               instance=self.get_object())

    def get_id(self):
        return uuid.UUID(self.kwargs['uuid'])

    def get_object(self):
        return get_object_or_404(Transaction, id=self.get_id())

    def get_context_data(self, **kwargs):
        kwargs.update({
            'transaction': self.get_object(),
            'form': self.get_form()
        })
        return super(TransactionView, self).get_context_data(**kwargs)

    def dispatch(self, *args, **kwargs):
        if not self.test_func():
            raise Http404()

        if self.get_object().payment_sent:
            return HttpResponseRedirect(
                reverse('payment_sent', args=(self.get_object().id.hex,)))

        return super(TransactionView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid()

    def form_invalid(self, form):
        context = self.get_context_data(**self.kwargs)
        context.update({
            'form': form
        })
        return self.render_to_response(context)

    def form_valid(self, form):
        transaction = form.save()
        transaction.payment_sent = True
        transaction.save()
        # TODO integration with blockonomics happens here
        return HttpResponseRedirect(
            reverse('payment_sent', args=(transaction.id.hex,)))


class PaymentSentView(TemplateView):
    template_name = 'sent.html'

    def get_id(self):
        return uuid.UUID(self.kwargs['uuid'])

    def get_object(self):
        return get_object_or_404(Transaction, id=self.get_id())

    def get_context_data(self, **kwargs):
        kwargs.update({
            'transaction': self.get_object(),
        })
        return super(PaymentSentView, self).get_context_data(**kwargs)


# TODO callback endpoint
# TODO receipt sending via celery
