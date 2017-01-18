import json
import requests
import decimal
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
    SATOSHI = decimal.Decimal("0.00000001")
    if transaction.status in (
            transaction.STATUS_UNCONFIRMED,
            transaction.STATUS_INITIATED) and record['confirmed'] == 0:
        if delete:
            transaction.delete()
    else:
        # Get txid
        r = requests.post("https://www.blockonomics.co/api/searchhistory",
                          data=json.dumps({'addr': transaction.to_address}))
        try:
            txid = json.loads(r.content.decode('utf-8'))['history'][0]['txid']
        except:
            return

        # Get and update status
        r = requests.post("https://www.blockonomics.co/api/tx_detail",
                          params={'txid': txid})
        data = json.loads(r.content.decode('utf-8'))['status']
        mapping = {
            'Confirmed': Transaction.STATUS_CONFIRMED,
            'Partially Confirmed': Transaction.STATUS_PARTIALLY_CONFIRMED,
            'Unconfirmed': Transaction.STATUS_UNCONFIRMED
        }
        transaction.status = mapping[data['status']]
        for item in data['vout']:
            if item['address'] == transaction.to_address:
                transaction.amount_paid = item['value'] * SATOSHI
        transaction.save()
