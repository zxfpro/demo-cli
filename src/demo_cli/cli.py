import typer
from importlib.metadata import version as pkg_version
from pathlib import Path

app = typer.Typer(
    help="A minimal Typer-based CLI starter.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)
config_app = typer.Typer(help="Manage local user config.")
app.add_typer(config_app, name="config")

CONFIG_DIR = Path.home() / ".demo-cli"
CONFIG_PATH = CONFIG_DIR / "config.toml"
DEFAULT_CONFIG = """# demo-cli user config
# This file is stored in your home directory and is not overwritten by package upgrades.

[app]
name = "demo-cli"
"""


@app.command()
def hello(name: str = typer.Argument("world")) -> None:
    """Say hello."""
    typer.echo(f"Hello, {name}!")

@app.command()
def add(x: int, y: int) -> None:
    typer.echo(x + y)

@app.command()
def version() -> None:
    """Print CLI version."""
    typer.echo(pkg_version("demo-cli"))

@config_app.command("path")
def config_path() -> None:
    """Print config file path."""
    typer.echo(str(CONFIG_PATH))

@config_app.command("init")
def config_init(force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config.")) -> None:
    """Create default user config at ~/.demo-cli/config.toml."""
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    if CONFIG_PATH.exists() and not force:
        typer.echo(f"Config already exists: {CONFIG_PATH}")
        typer.echo("Use --force to overwrite.")
        raise typer.Exit(code=0)
    CONFIG_PATH.write_text(DEFAULT_CONFIG, encoding="utf-8")
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass
    typer.echo(f"Initialized config: {CONFIG_PATH}")

@config_app.command("show")
def config_show() -> None:
    """Print config file content."""
    if not CONFIG_PATH.exists():
        typer.echo(f"Config not found: {CONFIG_PATH}")
        typer.echo("Run: demo config init")
        raise typer.Exit(code=1)
    typer.echo(CONFIG_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app()
