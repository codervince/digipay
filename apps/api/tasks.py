from django.core.cache import cache
from gateway.celery import app
from payments.models import Transaction
from payments.utils import check
from payments.utils import checks


@app.task
def check_transaction(transaction_id, delete=True):
    """if transaction is still unconfirmed then delete it.
    """
    transaction = Transaction.objects.get(id=transaction_id)
    check(transaction_id)

    if transaction.status in (Transaction.STATUS_INITIATED,
                              Transaction.STATUS_UNCONFIRMED) and delete:
        transaction.delete()


@app.task
def check_transactions():
    """if transaction is still unconfirmed then delete it.
    """
    ids = cache.get('payment_status_queue', [])

    unconfirmed = Transaction.objects\
        .exclude(status=Transaction.STATUS_CONFIRMED)\
        .values_list('id', flat=True)

    # Due to blockonomics limitations we take only first 50 transactions
    transactions = Transaction.objects.filter(id__in=ids)[:50]
    if transactions:
        checks(transactions)
