import math

from pathlib import Path
from loguru import logger
from typing import List
from telethon import TelegramClient
from telethon.sessions import StringSession

import config

from .base import BaseModule
from models import field, Account
from utils import Convert, AccountDeterminer


class Check(BaseModule):
    TITLE = "Account checker"
    ID = "check"

    CONFIGURATION = False

    class Kwargs(BaseModule.Kwargs):
        treads: int = field("Treads", default=10)

    async def init(self):
        accounts = Account.all(locked=False)
        step = math.ceil(len(accounts) / self.kwargs.treads) or 1

        chunked_accounts = [
            accounts[i:i + step] for i
            in range(0, len(accounts), step)
        ]

        self.coroutines = [
            self.task(accs) for accs in chunked_accounts
        ]

    async def task(self, accounts: List[Account]):
        for account in accounts:
            client = TelegramClient(
                StringSession(account.session),
                **account.connect_params,
                proxy=account.proxy
            )

            try:
                await client.connect()
                logger.info("Connecting to client")
            except Exception as e:
                logger.error(f"{account.id=} Error conneting to client: {e}")
                continue

            if not client.is_connected() or not await client.is_user_authorized() or await client.is_bot():
                await client.disconnect()
                account.delete()

                logger.error(f"{account.id=} invalid")
                continue

            spam_status = await AccountDeterminer(client).determine()
            logger.info(f"{account.id=} spam status: {spam_status}")
            account.spam_status = spam_status

            account.save()

            logger.success(f"{account.id} Rechecked")

        return True
