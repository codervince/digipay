import json
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
def send_callback(transaction_id):
    """Send callback to site when blockonomics responds with his callback
    """
    transaction = Transaction.objects.get(id=transaction_id)
    data = {
        'project_code': transaction.project_code,
        'email': transaction.email,
        'status': transaction.status,
        'transaction_id': trasnaction.id.hex
    }
    requests.post(transaction.site.site_ext.callback, data=data)


@app.task
def check_transaction(transaction_id, delete=True):
    """if transaction is still unconfirmed then delete it.
    """
    transaction = Transaction.objects.using('default').get(id=transaction_id)
    data = '{"addr":"%s"}' % transaction.to_address
    r = requests.post('https://www.blockonomics.co/api/balance',
                      data=data)
    response = json.loads(r.content.decode('utf-8'))
    record = response['response'][0]
    if transaction.status == transaction.STATUS_UNCONFIRMED and record['confirmed'] == 0:
        if delete:
            transaction.delete()
    else:
        if record['confirmed'] and not record['unconfirmed']:
            transaction.status = transaction.STATUS_CONFIRMED
        else:
            transaction.status = transaction.STATUS_PARTIALLY_CONFIRMED
        transaction.save()
