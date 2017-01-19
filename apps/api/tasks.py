from gateway.celery import app
from payments.models import Transaction
from payments.utils import check


@app.task
def check_transaction(transaction_id, delete=True):
    """if transaction is still unconfirmed then delete it.
    """
    transaction = Transaction.objects.get(id=transaction_id)
    check(transaction_id)

    if transaction.status in (Transaction.STATUS_INITIATED,
                              Transaction.STATUS_UNCONFIRMED) and delete:
        transaction.delete()
