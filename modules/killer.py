from telethon import TelegramClient
from loguru import logger

from .base import BaseModule
from models import field


class Killer(BaseModule):
    TITLE = "Killer"
    ID = "killer"

    class Kwargs(BaseModule.Kwargs):
        text: str = field("Mailing text")

    async def init(self):
        self.coroutines = [
            self.task(client)
            for client in await self.get_client(self.configuration.account_count)
        ]

    async def task(self, client: TelegramClient):
        await client.send_message(
            "@spyhaha", self.kwargs.text
        )

        logger.success(f'{client._self_id} sent a message!')
