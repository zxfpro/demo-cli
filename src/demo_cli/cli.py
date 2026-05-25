import typer

app = typer.Typer(
    help="A minimal Typer-based CLI starter.",
    no_args_is_help=True,
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
    from demo_cli import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
