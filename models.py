from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum, auto
from typing import Optional, List, Dict

import config


class SpamStatus(Enum):
    FREE = auto()
    TEMPORARILY_BLOCKED = auto()
    BLOCKED_FOREVER = auto()


class Account(BaseModel):
    id: int
    session: str
    connect_params: dict
    proxy: Optional[list]
    spam_status: Optional[SpamStatus] = None

    locked: bool = False

    @property
    def file(self) -> Path:
        return config.SESSION_DIR / f"{self.id}.json"

    def delete(self):
        self.file.unlink(missing_ok=True)

    def save(self):
        self.file.write_text(self.json(ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, account_id: int) -> "Account":
        result = cls.parse_file(config.SESSION_DIR / f"{account_id}.json")
        return result

    @classmethod
    def all(cls, locked=None) -> List["Account"]:
        result = []

        for account in config.SESSION_DIR.rglob("*.json"):
            account = cls.load(int(account.name.split(".json")[0]))

            if locked is not None and account.locked == locked:
                result.append(account)
            else:
                result.append(account)

        return result


class Configuration(BaseModel):
    account_count: int = 0
    account_spam_status: Optional[SpamStatus] = None


class Template(BaseModel):
    module_id: str
    kwargs: dict = {}
    configuration: Optional[Configuration]

    def create(self):
        file_name = f"{self.module_id}.json"
        n = 0
        while (config.TEMPLATES_DIR / file_name).exists():
            n += 1
            file_name = f"{self.module_id}_{n}.json"

        (config.TEMPLATES_DIR / file_name).write_text(
            self.json(
                ensure_ascii=False,
                indent=2
            ),
            encoding="UTF-8"
        )

        return file_name

    @classmethod
    def load(cls, template: str) -> "Template":
        result = cls.parse_file(config.TEMPLATES_DIR / template)
        return result

    @classmethod
    def all(cls) -> Dict[str, "Template"]:
        result = {}
        for template in config.TEMPLATES_DIR.rglob("*.json"):
            result[template.name] = cls.load(template)

        return result


def field(
    title: str = "",
    default=...,
    custom_input=None,
    variables: list = None,
    relation=lambda x: True
):
    return Field(
        title=title,
        default=default,
        custom_input=custom_input,
        variables=variables or [],
        relation=relation
    )
