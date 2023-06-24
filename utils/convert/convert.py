import struct

from typing import List, Optional
from pydantic import BaseModel, error_wrappers
from telethon import sessions, crypto


from ._tdata import convert_tdata
from config import DC_TABLE

TELETHON_STRUCT_PREFORMAT = '>B{}sH256s'


class AuthData(BaseModel):
    dc_id: int
    ip: str
    port: int
    key: bytes


class Convert:
    @staticmethod
    def tdata_to_auth(tdata: str) -> List[AuthData]:
        auths = []
        try:
            for auth in convert_tdata(tdata):
                auths.append(AuthData(**auth))
        except Exception:
            pass

        return auths

    @staticmethod
    def sql_session_to_auth(session: str) -> List[AuthData]:
        try:
            s = sessions.SQLiteSession(session)
            cur = s._cursor()

            result = cur.execute("select * from sessions").fetchall()
            auths = []
            if result:
                for auth in result:
                    try:
                        if DC_TABLE.get(auth[0]):
                            ip, port = DC_TABLE[auth[0]]
                            auths.append(
                                AuthData(dc_id=auth[0], ip=ip, port=port, key=auth[3])
                            )
                    except error_wrappers.ValidationError:
                        continue

            if s._conn is not None:
                s._conn.close()

            return auths
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def string_session_to_auth(session: str) -> Optional[AuthData]:
        string = session[1:]
        ip_len = 4 if len(string) == 352 else 16

        try:
            dc_id, ip, port, key = struct.unpack(
                TELETHON_STRUCT_PREFORMAT.format(ip_len), sessions.StringSession.decode(string))
        except Exception:
            return None

        if DC_TABLE.get(dc_id):
            ip, port = DC_TABLE[dc_id]

            return AuthData(dc_id=dc_id, ip=ip, port=port, key=key)

        return None

    @staticmethod
    def auth_to_string_session(auth: AuthData) -> sessions.StringSession:
        s = sessions.StringSession()

        s.set_dc(auth.dc_id, auth.ip, auth.port)
        s.auth_key = crypto.AuthKey(auth.key)

        return s

    # @staticmethod
    # async def p_sql_session_to_auth(session: str) -> Optional[AuthData]:
    #     try:
    #         path, session = ("/".join(session.split("/")[:-1]),session.split("/")[-1])
    #         session = file_storage.FileStorage(session.replace(".session", ""), Path(path))
    #         await session.open()
    #
    #         dc_id = await session.dc_id()
    #         auth_key = await session.auth_key()
    #
    #         if dc_id and auth_key:
    #             ip, port = config.meta.dc_table[dc_id]
    #             return AuthData(dc_id=dc_id, ip=ip, port=port, key=auth_key)
    #         else:
    #             return None
    #     except Exception as e:
    #         print("Pyroconverter:", e)
    #         return None
    # @staticmethod
    # async def p_string_session_to_auth(session: str):
    #     try:
    #         session = memory_storage.MemoryStorage('big', session)
    #         await session.open()
    #
    #         dc_id = await session.dc_id()
    #         auth_key = await session.auth_key()
    #
    #         if dc_id and auth_key:
    #             ip, port = config.meta.dc_table[dc_id]
    #             return AuthData(dc_id=dc_id, ip=ip, port=port, key=auth_key)
    #         else:
    #             return None
    #     except Exception as e:
    #         print(e)
    #         return None
