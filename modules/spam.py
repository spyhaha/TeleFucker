import asyncio
import random

from telethon import TelegramClient, functions, errors
from loguru import logger
from typing import Optional, List

from .base import BaseModule
from models import field
from utils import text_with_cyrillic_characters_obfuscated


class Spam(BaseModule):
    TITLE = "Spammer"
    ID = "spam"

    class Kwargs(BaseModule.Kwargs):
        target_type: str = field("Target type", variables=["user", "chat", "discussion"])
        target_peer: str = field("Target peer")
        join_link: Optional[str] = field(
            "Join link",
            relation=lambda x: x["target_type"] != "user",
            default=None
        )

        text: Optional[str] = field("Spam text")
        media: Optional[str] = field("Spam media")
        count: int = field("Message count")
        sleep: int = field("Sleep", default=10)

        tagall: bool = field("Tagall", default=False, relation=lambda x: x["target_type"] == "chat")
        obfuscation: bool = field("Obfuscation", default=False)

    async def init(self):
        self.coroutines = [
            self.task(client)
            for client in await self.get_client(self.configuration.account_count)
        ]

    async def task(self, client: TelegramClient):
        client_id = client._self_id

        if self.kwargs.target_type != "user":
            try:
                await self._join_chat(client, self.kwargs.join_link)
            except self.CHANGE_EXCEPTIONS:
                await self.change_client(self.task)

        participants = []
        if self.kwargs.tagall:
            async for p in client.iter_participants(self.kwargs.target_peer, limit=500):
                if (
                    # isinstance(p.participant, (types.ChannelParticipant, types.ChatParticipant))
                    not (p.deleted or p.bot)
                ):
                    participants.append(str(p.id))
                    await asyncio.sleep(0.02)
        print(participants)
        for i in range(self.kwargs.count):
            try:

                await client.send_message(
                    self.kwargs.target_peer,
                    self._text + self._participants_to_urls(participants),
                    file=self.kwargs.media
                )

                logger.success(f'{client_id} sent a message! №{i+1}')

            except Exception as e:
                logger.error(f'{client._self_id} Error occurred: {e}')

            await asyncio.sleep(self.kwargs.sleep)

    async def _join_chat(self, client: TelegramClient, link: str):
        if self.kwargs.target_type == "chat":
            link = link.replace("+", "joinchat/")
            if "joinchat" in link:
                link_hash = link.split("joinchat/")[1]

                try:
                    await client(functions.messages.ImportChatInviteRequest(link_hash))
                except errors.UserAlreadyParticipantError:
                    pass

            else:
                await client(functions.channels.JoinChannelRequest(link))

    @staticmethod
    def _participants_to_urls(participants: List[str]) -> str:
        return '\u2060'.join([
            f'<a href="tg://user?id={participant}">\u2060</a>' for
            participant in random.choices(participants, k=5)
        ])

    @property
    def _text(self):
        if self.kwargs.obfuscation:
            return text_with_cyrillic_characters_obfuscated(self.kwargs.text)

        return self.kwargs

