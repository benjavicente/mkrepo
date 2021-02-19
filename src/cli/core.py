"Core functions of the CLI"


from typing import MutableMapping, Any
from pathlib import Path
from shutil import copyfile
import toml

import typer

import logger as log
import utils

CLI_PATH = Path(__file__).parent.parent
DEFAULT_TEMPLATES_DIR = CLI_PATH.joinpath("templates")
DEFAULT_CONFIG_FILE = CLI_PATH.joinpath("default_userconfig.toml")
USER_CONFIG_DIR = Path.home().joinpath(".mkrepo")

Toml = MutableMapping[str, Any]


def repair() -> None:
    "Repairs mkrepo user directory"
    USER_CONFIG_DIR.mkdir(exist_ok=True)

    template_path = USER_CONFIG_DIR.joinpath("templates")
    template_path.mkdir(exist_ok=True)

    for template in filter(lambda t: t.is_file(), DEFAULT_TEMPLATES_DIR.iterdir()):
        copyfile(template, USER_CONFIG_DIR.joinpath("templates", template.name))

    user_config = USER_CONFIG_DIR.joinpath("config.toml")
    if not user_config.is_file():
        copyfile(DEFAULT_CONFIG_FILE, user_config)

    raise typer.Exit(0)


def get_userconfig() -> Toml:
    "Gets user configuration"
    userconfig_path = USER_CONFIG_DIR.joinpath("config.toml")
    if not userconfig_path.is_file():
        log.error(".mkrepo/config.toml does not exist in the user directory")
        log.info("Use --repair to fix this problem")
        raise typer.Exit(1)

    return toml.load(userconfig_path)


def get_template(name: str) -> Toml:
    "Gets the template file from the template direcory"
    # TODO: urls?
    file_name = utils.to_file_name(name)
    template_path = USER_CONFIG_DIR.joinpath("templates", file_name).resolve()
    print(template_path)
    if not template_path.is_file():
        log.error("The template does not exist")
        raise typer.Exit(1)

    return toml.load(template_path)


def list_templates() -> None:
    "List available templates"
    template_dir = Path.home().joinpath(".mkrepo", "templates")

    if not template_dir.is_dir():
        log.error(".mkrepo/templates/ does not exist in the user directory")
        log.info("Use --repair to fix this problem")
        raise typer.Exit(1)

    templates = [
        utils.to_template_name(element.name)
        for element in template_dir.iterdir()
        if element.is_file()
    ]

    log.columns(templates)

    raise typer.Exit()


def create_repository(template_name: str, directory: str, force: bool = False) -> None:
    "Interface function for creating a repository"
    dir_path = (Path.cwd() / Path(directory)).resolve()

    if not force and dir_path.is_file():
        log.error("There is a file created with the same name of the directory")
        raise typer.Exit(0)

    if not force and dir_path.exists() and any(dir_path.iterdir()):
        log.error("The directory already exists and is not empty")
        raise typer.Exit(0)

    _create_repository(get_template(template_name), dir_path, get_userconfig())


def _add_files(files: dict, directory: Path, data: Toml, mode="w") -> None:
    for file_name, content in files.items():
        file_path = directory.joinpath(file_name).resolve()
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, mode=mode, encoding="utf-8") as file:
            file.write(utils.template_substitutions(content, data=data))


def _create_repository(template: Toml, directory: Path, config: Toml) -> None:
    data = dict(template) | dict(config)
    data["repo"] = {"name": directory.name}

    # Check if user has requirements
    for requirement in template["requires"] + [config["vcs"]["use"]]:
        if not utils.command_exists(requirement):
            log.error(f"{requirement} is not available in PATH")
            raise typer.Exit(1)

    # Write Files
    directory.mkdir(exist_ok=True)
    if "write" in template:
        _add_files(template["write"], directory, data)
    if "write" in config:
        _add_files(config["write"], directory, data)
    if "append" in config:
        _add_files(config["append"], directory, data, mode="a")
    if config["write_setup_help"]:
        _add_files({"docs/setup.md": data["setup"]}, directory, {})

    # Initialize VCS
    # TODO: other vcs
    utils.run_command(f"{config['vcs']['use']} init {directory}")

    # Run commands
    for command in template["run"]:
        # Check if a comand is a template
        parsed_comand = utils.template_substitutions(command, data)
        if parsed_comand == command:
            # The comand is the same, continue
            log.info(f"Running `{command}`...")
            utils.run_command(command, cwd=str(directory))
        else:
            # The comand should changed, and might be multiple commands
            commands: list[str] = parsed_comand.split(";")
            for sub_command in filter(None, commands):
                log.info(f"Running `{sub_command}`...")
                utils.run_command(sub_command, cwd=str(directory))
