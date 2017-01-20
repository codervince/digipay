import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from gateway.celery import app
from payments.models import Transaction


@app.task
def send_receipt(transaction_id):
    """Send receipt
    """
    transaction = Transaction.objects.get(id=transaction_id)
    context = {
        'transaction': transaction,
    }
    html_content = render_to_string('receipt.html', context)
    text_content = render_to_string('receipt.txt', context)
    msg = EmailMultiAlternatives(
        ugettext('Receipt'),  # subject
        text_content,  # text message
        settings.DEFAULT_FROM_EMAIL,  # from
        [transaction.email]  # to
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)


@app.task
def send_webhook(transaction_id):
    """Send webhook to site when blockonomics responds with his callback
    """
    transaction = Transaction.objects.get(id=transaction_id)
    data = {
        'project_code': transaction.project_code,
        'email': transaction.email,
        'status': transaction.get_status_display(),
        'transaction_id': transaction.id.hex,
        'txid': transaction.txid
    }
    requests.post(transaction.webhook, data=data)
