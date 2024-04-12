import typing

from telethon import functions, TelegramClient, types
from typing import Optional, List, Tuple, Any
from loguru import logger

import struct


class CustomInitConnectionRequest(functions.InitConnectionRequest):
    """
        Мега ультра конекшн из под айпи павла дурова
    """

    def __init__(
        self,
        api_id: int,
        device_model: str,
        system_version: str,
        app_version: str,
        system_lang_code: str,
        lang_pack: str,
        lang_code: str,
        query: 'TypeX',
        proxy: Optional['TypeInputClientProxy'] = None,
        params: Optional[List[Tuple[str, Any]]] = None,
        pretend_package_name_is_real: bool = False
    ):
        self.api_id = api_id
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version
        self.system_lang_code = system_lang_code
        self.lang_code = lang_code
        self.query = query
        self.proxy = proxy

        self.lang_pack = lang_pack
        self.pretend_package_name_is_real = pretend_package_name_is_real

        if params:
            self.params = types.JsonObject([])

            for key, value in params:
                if isinstance(value, str):
                    json_object_value_value = types.JsonString(value)
                elif isinstance(value, int):
                    json_object_value_value = types.JsonNumber(value)
                else:
                    raise RuntimeError(type(value))

                this_value = types.JsonObjectValue(
                    key=key,
                    value=json_object_value_value
                )
                self.params.value.append(this_value)

            logger.debug(f"InitConnection params: {self.params.stringify()}")
        else:
            self.params = None

    def _bytes(self):
        logger.debug(f"pretend_package_name_is_real={self.pretend_package_name_is_real}")

        unpacked_flags = (
                (0 if self.proxy is None or self.proxy is False else 1) |
                (0 if self.params is None or self.params is False else 2) |
                (0 if not self.pretend_package_name_is_real else 2048)
        )

        flags = struct.pack('<I', unpacked_flags)
        logger.debug(f"unpacked_flags={unpacked_flags}")

        return b''.join((
            b'\xa9^\xcd\xc1',
            flags,
            struct.pack('<i', self.api_id),
            self.serialize_bytes(self.device_model),
            self.serialize_bytes(self.system_version),
            self.serialize_bytes(self.app_version),
            self.serialize_bytes(self.system_lang_code),
            self.serialize_bytes(self.lang_pack),
            self.serialize_bytes(self.lang_code),
            b'' if self.proxy is None or self.proxy is False else (self.proxy._bytes()),
            b'' if self.params is None or self.params is False else (self.params._bytes()),
            self.query._bytes(),
        ))

    @staticmethod
    def prepare_cli(
        client: TelegramClient,
        lang_pack: str = None,
    ) -> TelegramClient:
        init_params: functions.InitConnectionRequest = client._init_request
        lang_pack = lang_pack or init_params.lang_pack

        params, pretend_package_name_is_real = CustomInitConnectionRequest.get_params(lang_pack)

        client._init_request = CustomInitConnectionRequest(
            init_params.api_id,
            init_params.device_model,
            init_params.system_version,
            init_params.app_version,
            init_params.system_lang_code,
            lang_pack,
            init_params.lang_code,
            init_params.query,
            init_params.proxy,
            params,
            pretend_package_name_is_real
        )

        return client

    @staticmethod
    def create_cli(session, **kwargs) -> TelegramClient:
        lang_pack = kwargs.pop("lang_pack")
        client = TelegramClient(
            session=session,
            **kwargs
        )

        return CustomInitConnectionRequest.prepare_cli(client, lang_pack)

    @staticmethod
    def get_params(lang_pack: str) -> typing.Tuple[list, bool]:
        if lang_pack == "tdesktop":
            return [("tz_offset", 10800)], False
        else:
            return [], False

