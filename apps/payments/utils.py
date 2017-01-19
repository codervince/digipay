import decimal
import json
import requests
from .models import Transaction


SATOSHI = decimal.Decimal(0.00000001)


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

    txid = history_data['txid']
    r = requests.get("https://www.blockonomics.co/api/tx_detail",
                     params={'txid': txid})
    tx_detail = json.loads(r.content.decode('utf-8'))
    status = tx_detail['status']
    for item in tx_detail['vout']:
        if item['address'] == addr:
            value = decimal.Decimal(item['value'])
            amount = value * SATOSHI
            amount = round(amount, 8)

    mapping = {
        'Confirmed': Transaction.STATUS_CONFIRMED,
        'Partially Confirmed': Transaction.STATUS_PARTIALLY_CONFIRMED,
        'Unconfirmed': Transaction.STATUS_UNCONFIRMED
    }

    transaction.txid = txid
    transaction.status = mapping[status]
    transaction.amount_paid = amount
    transaction.save()
