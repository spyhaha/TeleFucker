from models import Account


def unlocker():
    for account in Account.all():
        if account.locked:
            account.locked = False
            account.save()
