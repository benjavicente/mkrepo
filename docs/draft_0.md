# Draft

This is a draft used to plan the (short) development of mkrepo.

- [Language used](#languaje-used)
- [CLI](#cli)
- [Template](#template)
  - [File format](#file-format)
- [Initialize scripts (run)](#initializar-scripts-run)
- [User configuration](#user-configuration)


## Language used

MkRepo will use Python, because it's a mainstream language that is
easy to setup in different OS.

## CLI

```txt
mkrepo [template] [directory] [options]

template:
  the template to use to create the repository
  it can be a template url or name

directory:
  project directory and name

options:
  -l, --list  list available templates and exit
  -h, --help  show this message and exit and exit
```

## Template

A repository usually involves:

- Version control system (vcs)
- Directory structure (dir)
- README (docs)
- Environments (env)
- Dependencies (dep)

So, a template should contain a sequence of commands to setup the
project, file structure and environments.

There are already commands to create and manage repositories, like:

- [`cargo`] (rust)
- [`poetry`] (python)
- [`npm`] (javascript)

[`cargo`]: https://doc.rust-lang.org/cargo/index.html
[`poetry`]: https://python-poetry.org/docs/basic-usage/
[`npm`]: https://github.com/npm/cli

This project should use those tools to create and manage repositories.
After all, must of them are necessary to manage dependencies and to
run the project.

Templates should have:

- A list of requirements to build the repository (ex: `npm`).
- A list of commands to run sequentially to setup the repository.
- A list of additional files and directories to create.
- Instructions indicating how to setup the development environment
  (beginner friendly).


With that requirements, the `toml` format seems reasonable thanks to
multiline strings, groups, and list support.

For example:

```toml
name = "python:poetry"

description = "Python project with Poetry"
requires = ["python", "poetry"]

setup = """
# SetUp

This project uses poetry. You can install it
[here](https://python-poetry.org/docs/#installation)

Run `poetry install` to download the dependencies and
`poetry shell` to enter the virtual environment. Run the code
with `python src/main.py`. Use `exit` to exit.
"""

run = [
    "poetry init",
    # More about this later
    "[python.dep|name,dep] poetry add #{name}@#{dep}",
    "[python.dev-dep|name,dep] poetry add #{name}@#{dep} -D"
]

[python.dep]
numpy = "1.20.1"

[python.dev-dep]
black = "*"

[write]
".gitignore" = """
*.env
__pycache__/
dist/
"""
"tmp/.keep" = ""
```

## Initializer scripts (run)

In the template file, every script in the `run` list should run a
valid command, whatever the shell (Bash, PowerShell, etc).

To archive this, the available commands would be limited to only
programs or commands in the `requires` list, and special characters,
like `$`, `;` and `#` should not be available.

Because adding such limitation makes complex commands impossible,
helpers should be added, mainly to add iteration and interpolation.

## User configuration

Templates don't cover VCS and READMEs. That task is for the user
configuration.

User configuration usually involves:

- Default entries to add to `ignore` files
- Editor configuration files for a project
- The default version control system to use

An example of a user configuration file would be:

```toml
[vcs]
use = "git"

[append]
".gitignore" = """
.vscode/
*lock*  # Ignore lock files in the beginning of a project
"""

# Deb dependencies to add in all projects
[python.dev-dep]
mypy = "^0.8"

[write]
".vscode/settings.json" = "{\n}"
"readme.md" = "# #{repo.name}\n"
```
