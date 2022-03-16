import typer

from app.odm.create_indexes import create_indexes
from app.odm.apply_indexes import apply_indexes

app_typer = typer.Typer()


@app_typer.command()
def applyindexes():
    apply_indexes()


@app_typer.command()
def createindexes():
    create_indexes()
