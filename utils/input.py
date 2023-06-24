from misc import c
from typing import Optional


def base_input(title="Input", mk=True):
    return c.input(f"{'[bold]' if mk else ''}{title} -{'[/]' if mk else ''} ")


def int_input(title="Input"):
    result = base_input(title)
    while not result.isdigit():
        c.print("[red]Not a number[/]")
        result = base_input(title)

    return int(result)


def bool_input(title="Input"):
    while True:
        result = base_input(title + " (y/n)")
        if result == "y":
            return True
        elif result == "n":
            return False
        else:
            c.print("[red]Wrong input[/]")


def int_selection_input(titles: list):
    page_ids = [n + 1 for n in range(len(titles))]

    pages = zip(page_ids, titles)
    for page in pages:
        c.print(f"{page[0]}) {page[1]}")

    result = int_input("Select")
    while result not in page_ids:
        c.print("[red]Wrong page number[/]")
        result = int_input("Select")

    return result


def str_selection_input(page_ids: list, titles: list):
    pages = zip(page_ids, titles)
    for page in pages:
        c.print(f"[blue]{page[0]}[/]) {page[1]}")

    result = base_input("Select")
    while result not in page_ids:
        c.print("[red]Wrong page id[/]")
        result = base_input("Select")

    return result


def list_selection_input(variables: list, title="Select"):
    for variable in variables:
        c.print(f"[blue]*[/]) {variable}")

    result = base_input(title)
    while result not in variables:
        c.print("[red]Wrong variable[/]")
        result = base_input(title)

    return result


def dict_int_selection_input(page_values: list, titles: list):
    page_ids = {n + 1: page_values[n] for n in range(len(page_values))}

    pages = zip(page_ids.keys(), titles)
    for page in pages:
        c.print(f"[blue]{page[0]}[/]) {page[1]}")

    result = int_input("Select")
    while result not in page_ids.keys():
        c.print("[red]Wrong select[/]")
        result = int_input("Select")

    return page_ids[result]


def list_input(item_input, title="Input"):
    values = []
    while True:
        values.append(
            item_input(title)
        )

        if not bool_input("Add one more value?"):
            break

    return values


def proxy_input() -> Optional[tuple]:
    while True:
        result = base_input(
            "[bold]Input proxy[/]\n"
            "Example: type,addr,port,user,pass\n",
            mk=False
        )
        if result:
            values = result.split(",")
            if not len(values) >= 3:
                c.print(f"[red]Wrong proxy format[/]")
                continue
            proxy_type, addr, port, *credentials = values

            if not port.isdigit() or int(port) > 65535:
                c.print(f"[red]Wrong port format[/]")
                continue

            if credentials and len(credentials) < 2:
                c.print(f"[red]Wrong credentials format[/]")
                continue

            return proxy_type, addr, int(port), *credentials
        else:
            return None
