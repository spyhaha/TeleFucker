import config
import functions

from misc import c
from manager import create_new_task, run_existing_task
from models import Account, SpamStatus
from utils import clear, int_selection_input


def app():
    while True:
        clear()

        c.print(config.LOGO)
        summary = free = blocked_forever = temporarily_blocked = no_info = locked = 0
        for a in Account.all():
            summary += 1

            if a.spam_status is SpamStatus.FREE:
                free += 1
            elif a.spam_status is SpamStatus.BLOCKED_FOREVER:
                blocked_forever += 1
            elif a.spam_status is SpamStatus.TEMPORARILY_BLOCKED:
                temporarily_blocked += 1
            else:
                no_info += 1

            if a.locked:
                locked += 1

        c.print(
            "[bold]Stats:[/]\n"
            f"SUMMARY: {summary}\n"
            f"FREE: {free}\n"
            f"BLOCKED_FOREVER: {blocked_forever}\n"
            f"TEMPORARILY_BLOCKED: {temporarily_blocked}\n"
            f"NO_INFO: {no_info}\n"
            f"LOCKED: {locked}\n"
        )

        result = int_selection_input(
            [
                "New task",
                "Load template",
                "Account unlocker",
                "Exit",
            ]
        )

        if result == 1:
            create_new_task()
        elif result == 2:
            run_existing_task()
        elif result == 3:
            functions.unlocker()
        else:
            return


if __name__ == "__main__":
    app()
