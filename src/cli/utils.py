"Utilities"

from typing import Mapping
import subprocess
import platform
import os
import jinja2

DEVNULL = subprocess.DEVNULL

JINJA_ENV = jinja2.Environment(keep_trailing_newline=True)

def command_exists(command: str) -> bool:
    "Check if the command exists in PATH"
    exist_command = "where" if platform.system() == "Windows" else "which"
    return subprocess.call([exist_command, command], stdout=subprocess.DEVNULL) == 0


def to_file_name(template_name: str) -> str:
    "Returns the corresponding name of the file for the template name"
    return template_name.strip().replace(":", "_") + ".toml"


def to_template_name(file_name: str) -> str:
    "Returns the corresponding name of the template for the file name"
    return file_name.replace("_", ":").rpartition(".")[0]


def run_command(command: str, cwd: str = os.getcwd(), stdout=DEVNULL) -> None:
    "Runs a command in the background"
    subprocess.call(command.split(), stdout=stdout, cwd=cwd)

def template_substitutions(template: str, data: Mapping[str, object]) -> str:
    "Uses Jinja for string templating in templates and config files"
    return JINJA_ENV.from_string(template).render(data)
