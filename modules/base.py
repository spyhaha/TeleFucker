import asyncio

from telethon import TelegramClient, sessions, errors
from typing import Optional, List, Tuple, Dict, Callable, Any
from loguru import logger

from models import BaseModel, Account, Configuration


class BaseModule:
    TITLE = "BaseModule"
    ID = "base"

    CONFIGURATION = True

    CHANGE_EXCEPTIONS = (
        errors.UserBannedInChannelError, errors.AuthKeyDuplicatedError, errors.FloodWaitError,
        errors.ChatWriteForbiddenError, errors.PeerFloodError, errors.ChannelsTooMuchError,
        errors.SessionPasswordNeededError
    )

    class Kwargs(BaseModel):
        class Schema(BaseModel):
            title: str
            type: str
            items: dict = {}
            default: Any = None
            custom_input: Optional[Callable] = None
            variables: list = []
            relation: Callable = lambda x: True

        @classmethod
        def blanks(cls) -> Dict[str, Schema]:
            props = {}

            for key, value in cls.schema()['properties'].items():
                props[key] = cls.Schema(**value)

            return props

    def __init__(self, kwargs: Optional[Kwargs], configuration: Optional[Configuration]):
        self.kwargs = kwargs
        self.configuration = configuration

        self.coroutines = []

        self.used_account_ids: List[int] = []
        self.active_clients: List[Tuple[TelegramClient, Account]] = []

        self.account_filters = [lambda x: not x.locked]

    def set_kwargs(self, kwargs: Kwargs):
        self.kwargs = kwargs

    def set_configuration(self, configuration: Configuration):
        self.configuration = configuration

    def start(self):
        asyncio.run(
           self.run()
        )

    async def init(self):
        pass

    async def run(self):
        await self.init()

        responses = []
        while self.coroutines:
            to_do = self.coroutines
            self.coroutines = []

            logger.info(f"Running {len(to_do)} coroutines")

            response = await asyncio.gather(*to_do, return_exceptions=True)
            logger.info(f"Reponses: \n{response}")
            responses += response

        await self.disconnect_clients()

        return responses

    async def change_client(self, coro, *args, **kwargs) -> None:
        """
            Adds a new task into list of coroutines with the new client
        """
        client = await self.get_client()
        if client:
            logger.info(f'Got new client: {client[0]._self_id}')
            self.coroutines.append(coro(client[0], *args, **kwargs))

    async def get_client(self, count: int = 1) -> List[TelegramClient]:
        """
            Returns list of TelegramClient
        """
        accounts = self.get_account(count)

        clients = [
            client for client in
            await asyncio.gather(*[self.connect_client(account) for account in accounts])
            if isinstance(client, TelegramClient)
        ]

        return clients

    async def connect_client(self, account: Account) -> Optional[TelegramClient]:
        """
            Returns connected TelegramClient or None
        """
        is_authorized = False
        client = None

        while not is_authorized:
            if not account:
                return None

            account.locked = True
            account.save()

            client = self.account_to_client(account)

            await asyncio.gather(
                client.connect(),
                return_exceptions=True
            )  # FIXME

            if (
                client.is_connected() and await client.is_user_authorized()
                and not await client.is_bot()
            ):  # To handle asyncio loop error
                is_authorized = True
                self.active_clients.append((client, account))
            else:
                await client.disconnect()

                account.locked = False
                account.save()

                account = account[0] if (account := self.get_account(1)) else None

        return client

    async def disconnect_clients(self):
        for client, account in self.active_clients:
            await client.disconnect()

            account.locked = False
            account.save()

    def get_account(self, count: int = 1) -> List[Account]:
        accounts = list(filter(
            lambda x: (x.id not in self.used_account_ids) and (False not in [
                f(x) for f in self.account_filters
            ]),
            Account.all()
        ))[:count]

        self.used_account_ids += [a.id for a in accounts]

        return list(accounts)

    @staticmethod
    def account_to_client(account: Account) -> TelegramClient:
        """
            Converting Session into TelegramClient class
        """
        client = TelegramClient(
            sessions.StringSession(account.session),
            **account.connect_params,
            proxy=account.proxy
        )

        client.parse_mode = 'html'

        return client
