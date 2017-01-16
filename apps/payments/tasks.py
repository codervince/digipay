from gateway.celery import app


@app.task
def check_transaction(transaction):
    """if transaction is still unconfirmed then delete it.
    """
    if transaction.status == transaction.STATUS_UNCONFIRMED:
        transaction.delete()
