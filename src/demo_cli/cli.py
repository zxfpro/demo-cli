import os
from importlib.metadata import version as pkg_version
from pathlib import Path
import json
from copy import deepcopy

import typer
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # Python 3.10 and below
import tomli_w

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


def _deep_merge(base: dict, override: dict) -> dict:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _effective_config() -> dict:
    # Priority: defaults < config file < env var
    cfg = _deep_merge(DEFAULTS, _read_config_file())
    env_name = _env_value("DEMO_CLI_APP_NAME")
    if env_name is not None:
        cfg.setdefault("app", {})
        if isinstance(cfg["app"], dict):
            cfg["app"]["name"] = env_name
    return cfg


def _get_by_dotted(data: dict, dotted_key: str):
    cur = data
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(dotted_key)
        cur = cur[part]
    return cur


def _set_by_dotted(data: dict, dotted_key: str, value) -> None:
    parts = dotted_key.split(".")
    if any(not part for part in parts):
        raise ValueError("invalid key")
    cur = data
    for part in parts[:-1]:
        nxt = cur.get(part)
        if nxt is None:
            cur[part] = {}
            nxt = cur[part]
        if not isinstance(nxt, dict):
            raise ValueError(f"cannot set child key under non-table: {part}")
        cur = nxt
    cur[parts[-1]] = value


def _parse_value(raw: str):
    text = raw.strip()
    if text == "":
        return ""
    lowered = text.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
            return int(text)
        return float(text) if any(ch in text for ch in ".eE") else text
    except ValueError:
        pass
    if (text.startswith("[") and text.endswith("]")) or (text.startswith("{") and text.endswith("}")):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return raw
    return raw


def _write_config_file(data: dict) -> None:
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    content = tomli_w.dumps(data)
    CONFIG_PATH.write_text(content, encoding="utf-8")
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass


def _get_app_name() -> str:
    cfg = _effective_config()
    value = cfg.get("app", {}).get("name") if isinstance(cfg.get("app"), dict) else DEFAULTS["app"]["name"]
    if isinstance(value, str) and value.strip():
        return value.strip()
    return DEFAULTS["app"]["name"]


def _upsert_app_name(name: str) -> None:
    safe_name = name.strip()
    if not safe_name:
        raise typer.BadParameter("value cannot be empty")

    data = _read_config_file()
    _set_by_dotted(data, "app.name", safe_name)
    _write_config_file(data)


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
def config_get(key: str = typer.Argument(..., help="Config key, e.g. app.name")) -> None:
    """Read an effective config value (supports dotted keys)."""
    try:
        value = _get_by_dotted(_effective_config(), key)
    except KeyError:
        typer.echo(f"Config key not found: {key}")
        raise typer.Exit(code=2)
    if isinstance(value, (dict, list)):
        typer.echo(json.dumps(value, ensure_ascii=False))
    else:
        typer.echo(str(value))


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key, e.g. app.name"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a config value in ~/.demo-cli/config.toml (supports dotted keys)."""
    if not key or key.startswith(".") or key.endswith(".") or ".." in key:
        typer.echo(f"Invalid key: {key}")
        raise typer.Exit(code=2)
    data = _read_config_file()
    try:
        _set_by_dotted(data, key, _parse_value(value))
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2)
    _write_config_file(data)
    typer.echo(f"Set {key}={value}")


if __name__ == "__main__":
    app()
