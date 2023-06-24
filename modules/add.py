import math

from pathlib import Path
from loguru import logger
from typing import List, Optional
from telethon import TelegramClient
from telethon.sessions import StringSession

import config

from .base import BaseModule
from models import field, Account
from utils import Convert, AccountDeterminer, proxy_input


class Add(BaseModule):
    TITLE = "Account adder"
    ID = "add"

    CONFIGURATION = False

    class Kwargs(BaseModule.Kwargs):
        path: str = field("Session path")
        treads: int = field("Treads")
        new_session: bool = field("New session", default=False)
        proxy: Optional[tuple] = field(
            "Proxy", default=None, custom_input=proxy_input
        )

    async def init(self):
        path = Path(self.kwargs.path)

        auths = [
            auth for p in path.rglob("key_datas")
            for auth in Convert.tdata_to_auth(str(p.parent))
        ] + [
            auth for f in path.rglob("*.session")
            for auth in Convert.sql_session_to_auth(str(f))
        ]

        sessions = [Convert.auth_to_string_session(auth) for auth in auths]
        step = math.ceil(len(sessions) / self.kwargs.treads) or 1

        chunked_sessions = [
            sessions[i:i + step] for i
            in range(0, len(sessions), step)
        ]

        self.coroutines = [
            self.task(sessions) for sessions in chunked_sessions
        ]

    async def task(self, sessions: List[StringSession]):
        for session in sessions:
            client = TelegramClient(session, **config.CONNECT_PARAMS, proxy=self.kwargs.proxy)

            try:
                await client.connect()
                logger.info("Connecting to client")
            except Exception as e:
                logger.error(f"Error conneting to client: {e}")
                continue

            if not client.is_connected() or not await client.is_user_authorized() or await client.is_bot():
                await client.disconnect()
                logger.error("Account invalid")
                continue

            spam_status = await AccountDeterminer(client).determine()
            logger.info(f"Account spam status: {spam_status}")
            if self.kwargs.new_session:
                pass

            account = Account(
                id=client._self_id,
                session=session.save(),
                proxy=self.kwargs.proxy,
                connect_params=config.CONNECT_PARAMS,
                spam_status=spam_status
            )

            account.save()

            logger.success(f"New session saved {account.id}.json")

        return True
