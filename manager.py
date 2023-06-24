from typing import Type, Optional

from misc import c
from utils import (
    str_selection_input, base_input, int_input,
    dict_int_selection_input, bool_input, list_selection_input, list_input
)
from modules import BaseModule
from models import SpamStatus, Configuration, Template


def create_new_task():
    ids = []
    titles = []
    for m in BaseModule.__subclasses__():
        ids.append(m.ID)
        titles.append(m.TITLE)

    result = str_selection_input(
        ids, titles
    )

    module = [m for m in BaseModule.__subclasses__() if m.ID == result][0]

    kwargs = set_kwargs(module)

    configuration = None
    if module.CONFIGURATION:
        accounts_count = int_input("Input accounts count")
        account_spam_status = dict_int_selection_input(
            [SpamStatus.FREE, SpamStatus.TEMPORARILY_BLOCKED, SpamStatus.BLOCKED_FOREVER, None],
            ["FREE", "TEMPORARILY_BLOCKED", "BLOCKED_FOREVER", "DOESN'T MATTER"]
        )

        configuration = Configuration(account_count=accounts_count, account_spam_status=account_spam_status)

    result = bool_input("Save setting to template?")
    if result:
        file_name = Template(module_id=module.ID, kwargs=kwargs, configuration=configuration).create()
        c.print(f"[bold]Done![/] ([blue]{file_name}[/])")

    result = bool_input(f"Run {module.TITLE}?")
    if result:
        run_module(module, kwargs, configuration)


def run_existing_task():
    templates = Template.all()

    result = list_selection_input(
        [k.split(".")[0] for k in templates.keys()],
        "Select template"
    )

    template = Template.load(result + ".json")
    module = [m for m in BaseModule.__subclasses__() if m.ID == template.module_id][0]

    result = bool_input(f"Run {module.TITLE}?")

    if result:
        run_module(module, module.Kwargs(**template.kwargs), template.configuration)


def run_module(
    module: Type[BaseModule],
    kwargs: BaseModule.Kwargs,
    configuration: Optional[Configuration]
):
    instant = module(
        kwargs,
        configuration
    )

    print(module, kwargs, configuration)
    instant.start()

    input("Done!")


def set_kwargs(module: Type[BaseModule]):
    kwargs = {}

    inputs = {
        "boolean": bool_input,
        "integer": int_input,
        "string": base_input
    }

    for key, meta in module.Kwargs.blanks().items():
        if meta.relation(kwargs):
            if meta.custom_input:
                value = meta.custom_input()
            else:
                if meta.variables:
                    value = list_selection_input(meta.variables, f"Select {meta.title}")
                else:
                    if meta.type == "array":
                        item_type = meta.items.get("type", "string")
                        value = list_input(
                            inputs[item_type], f"Input {meta.title} [blue]({item_type})[/]"
                        )
                    else:
                        value = inputs[meta.type](
                            f"Input {meta.title} [blue]({meta.type})[/]"
                        )

            kwargs[key] = value or meta.default
        else:
            kwargs[key] = meta.default

    return module.Kwargs(**kwargs)
