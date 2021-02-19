"Module with helpers to log messages"

from rich.console import Console
from rich.columns import Columns


CONSOLE = Console()


def error(message: str) -> None:
    "Log an error message and exit"
    CONSOLE.print(message, style="red")


def info(message: str) -> None:
    "Log an information mesage"
    CONSOLE.print(message, style="blue")


def columns(items: list) -> None:
    "Log a list of items in columns"
    CONSOLE.print(Columns(items))
