from telethon import TelegramClient, functions
from typing import Optional

from models import SpamStatus


class AccountDeterminer:
    _spambot_messages = {
        "Good news, no limits are currently applied to your account": SpamStatus.FREE,
        "Ваш аккаунт свободен от каких-либо ограничений.": SpamStatus.FREE,
        "Unfortunately, your account is now limited.": SpamStatus.BLOCKED_FOREVER,
        "Теперь Ваш аккаунт ограничен:": SpamStatus.BLOCKED_FOREVER,
        "The moderators have confirmed the report and your account is now limited until": SpamStatus.TEMPORARILY_BLOCKED,
        "Ваш аккаунт временно ограничен:": SpamStatus.TEMPORARILY_BLOCKED
    }

    def __init__(self, client: TelegramClient) -> None:
        self.client = client

    async def determine(self) -> Optional[SpamStatus]:
        try:
            await self.client(functions.contacts.UnblockRequest(id="SpamBot"))
        except Exception as e:  # FIXME
            return None

        return await self._get_spambot_status()

    async def _get_spambot_status(self) -> Optional[SpamStatus]:
        try:
            async with self.client.conversation("SpamBot") as conv:
                await conv.send_message("/start")
                response = await conv.get_response()
        except Exception:
            return None

        for message, status in self._spambot_messages.items():
            if message in response.message:
                return status

        return None
