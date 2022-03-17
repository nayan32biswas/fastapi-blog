import typer

from app.odm.apply_indexes import apply_indexes

cli_app = typer.Typer()


@cli_app.command()
def applyindexes():
    apply_indexes()


@cli_app.command()
def demo():
    print("demo")
