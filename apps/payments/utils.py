import decimal
import json
import requests
from .models import Transaction
from payments.tasks import send_webhook
from payments.tasks import send_receipt


SATOSHI = decimal.Decimal(0.00000001)


def set_tx_details(history_data, transaction):
    """Does check for 1 transaction"""
    txid = None
    for item in history_data:
        if item['addr'][0] == transaction.to_address:
            txid = item['txid']

    if not txid:
        return

    mapping = {
        'Confirmed': Transaction.STATUS_CONFIRMED,
        'Partially Confirmed': Transaction.STATUS_PARTIALLY_CONFIRMED,
        'Unconfirmed': Transaction.STATUS_UNCONFIRMED
    }

    r = requests.get("https://www.blockonomics.co/api/tx_detail",
                     params={'txid': txid})
    tx_detail = json.loads(r.content.decode('utf-8'))
    status = tx_detail['status']
    for item in tx_detail['vout']:
        if item['address'] == transaction.to_address:
            value = decimal.Decimal(item['value'])
            amount = value * SATOSHI
            amount = round(amount, 8)

    if transaction.status != mapping[status]:
        send_webhook.apply_async(kwargs={'transaction_id': transaction.id})

    if mapping[status] == Transaction.STATUS_CONFIRMED:
        send_receipt.apply_async(kwargs={'transaction_id': transaction.id})

    transaction.txid = txid
    transaction.status = mapping[status]
    transaction.amount_paid = amount
    transaction.save()


def check(transaction):
    """check transaction status based on to_address"""
    if not isinstance(transaction, Transaction):
        transaction = Transaction.objects.get(id=transaction)

    r = requests.post("https://www.blockonomics.co/api/searchhistory",
                      data=json.dumps({"addr": transaction.to_address}))
    try:
        history_data = json.loads(r.content.decode('utf-8'))['history'][0]
    except:
        return

    set_tx_details(history_data, transaction)


def checks(transactions):
    """check transactions status based on to_address"""
    txs = transactions.values_list('to_address', flat=True)
    addrs = ' '.join([tx for tx in txs if tx])
    r = requests.post("https://www.blockonomics.co/api/searchhistory",
                      data=json.dumps({"addr": addrs}))

    try:
        history_data = json.loads(r.content.decode('utf-8'))['history']
    except:
        return

    [set_tx_details(history_data, transaction) for transaction in transactions]
