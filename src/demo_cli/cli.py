import typer
from importlib.metadata import version as pkg_version

app = typer.Typer(
    help="A minimal Typer-based CLI starter.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)


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


if __name__ == "__main__":
    app()
