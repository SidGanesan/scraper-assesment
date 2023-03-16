import click

from pathlib import Path
from flask.cli import with_appcontext
from structlog import get_logger

from .scrape import scrape
from .ingest import ingest
from .summary import summary

log = get_logger(name=__name__)


@click.group(help="CLI commands for web scraping worker")
@with_appcontext
def cli() -> None:
    pass


@cli.command("create_tables", help="Create all SQLite tables")
def create_tables() -> None:
    import app.models as m

    local_path = Path("app") / "local"
    if not local_path.exists():
        log.info("Creating local directory for file storage")
        local_path.mkdir(parents=True)

    db_path = Path("app") / "local" / "database.db"
    if db_path.exists():
        log.warn(
            "DB file already exists, removing exisiting to create a new fresh db",
            path=db_path,
        )
        db_path.unlink()

    log.info("Creating all tables")
    m.db.create_all()
    log.info("Completed!")


@cli.command("tear_down", help="Deletes the database.db file")
def tear_down() -> None:
    log.info("Attempting to delete database.db file")
    db_path = Path("app") / "local" / "database.db"

    if not db_path.exists():
        log.warn("No file to delete found ending process")
        return

    db_path.unlink()
    log.info("Completed!")


cli.add_command(scrape)
cli.add_command(ingest)
cli.add_command(summary)
