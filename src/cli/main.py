"CLI for mkrepo"

from typing import Optional

import typer

import core


app_settings = {"context_settings": {"help_option_names": ["-h", "--help"]}}


app = typer.Typer(**app_settings)  # type: ignore


def _repair(run: bool) -> None:
    if run:
        core.repair()


def _list_templates(run: bool) -> None:
    if run:
        core.list_templates()


option_list = typer.Option(
    None,
    "--list",
    "-ls",
    help="List available templates and exit.",
    show_default=False,
    callback=_list_templates,
)

option_repair = typer.Option(
    None, "--repair", help="Repair mkdir", show_default=False, callback=_repair
)


@app.command(**app_settings)  # type: ignore
def main(
    template: str,
    directory: str,
    _list: Optional[bool] = option_list,
    _repair: Optional[bool] = option_repair,
) -> None:
    "mkrepo CLI"
    core.create_repository(template, directory)


if __name__ == "__main__":
    app()
