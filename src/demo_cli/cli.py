import os
from importlib.metadata import version as pkg_version
from pathlib import Path

import tomllib
import typer

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
DEFAULTS = {"app": {"name": "demo-cli"}}


def _read_config_file() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _env_value(env_name: str) -> str | None:
    val = os.getenv(env_name)
    if val is None:
        return None
    s = val.strip()
    return s if s else None


def _get_app_name() -> str:
    # Priority: defaults < config file < env var
    name = DEFAULTS["app"]["name"]
    file_cfg = _read_config_file()
    file_name = file_cfg.get("app", {}).get("name") if isinstance(file_cfg.get("app"), dict) else None
    if isinstance(file_name, str) and file_name.strip():
        name = file_name.strip()
    env_name = _env_value("DEMO_CLI_APP_NAME")
    if env_name is not None:
        name = env_name
    return name


def _upsert_app_name(name: str) -> None:
    safe_name = name.strip()
    if not safe_name:
        raise typer.BadParameter("value cannot be empty")

    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    content = f"""# demo-cli user config
# This file is stored in your home directory and is not overwritten by package upgrades.

[app]
name = \"{safe_name.replace('\\', '\\\\').replace('"', '\\"')}\"
"""
    CONFIG_PATH.write_text(content, encoding="utf-8")
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass


@app.command()
def hello(name: str = typer.Argument("world")) -> None:
    """Say hello."""
    app_name = _get_app_name()
    typer.echo(f"[{app_name}] Hello, {name}!")


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


@config_app.command("get")
def config_get(key: str = typer.Argument(..., help="Config key, currently supports: app.name")) -> None:
    """Read an effective config value (applies env override)."""
    if key != "app.name":
        typer.echo("Unsupported key. Supported keys: app.name")
        raise typer.Exit(code=2)
    typer.echo(_get_app_name())


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key, currently supports: app.name"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a config value in ~/.demo-cli/config.toml."""
    if key != "app.name":
        typer.echo("Unsupported key. Supported keys: app.name")
        raise typer.Exit(code=2)
    _upsert_app_name(value)
    typer.echo(f"Set {key}={value}")


if __name__ == "__main__":
    app()
