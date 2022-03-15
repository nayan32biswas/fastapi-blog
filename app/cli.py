import typer

from app.odm.create_migrations import create_migrations
from app.odm.apply_migrations import apply_migrations

app_typer = typer.Typer()


@app_typer.command()
def migrate(name: str):
    apply_migrations()


@app_typer.command()
def createmigrations():
    create_migrations()
