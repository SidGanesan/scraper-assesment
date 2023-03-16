import click
from pathlib import Path

from structlog import get_logger

from app.support.serialise import csv_to_attrs
from app.support.similarweb import SimilarWebConverter, SimilarWebIn

log = get_logger(name=__name__)


@click.group("ingest", help="Commands for the ingesting of data to the DB")
def ingest():
    pass


@ingest.command(
    "load_similar_web", help="Loads specified file from local input directory"
)
@click.argument("filename")
def load_similar_web(filename: str):
    import app.models as m

    assert (
        "similarweb" in filename
    ), "This command is only intended to ingest similarweb scraped pages"

    load_path = Path("app") / "local" / "input" / filename
    if not load_path.exists():
        raise NameError("No such file exists")

    # Check to see if we have processed this file before
    if m.Event.query.filter_by(path=str(load_path)).one_or_none():
        log.warn("Duplicate file found", file=load_path)
        return

    # Create a new event for the file being ingested
    event = m.Event.create(path=str(load_path))
    m.db.session.flush()

    # We don't check headers as this class has a complex structuring strategy
    content = load_path.read_bytes()
    parsed_content = csv_to_attrs(
        SimilarWebIn, SimilarWebConverter, content, check_headers=False
    )

    # persist to model layer
    for page in parsed_content:
        m.PageScrape.create_from_similar_web(event=event, sw_page=page)

    m.db.session.commit()


@ingest.command("load_all_similar_web")
def load_all_similar_web():
    import app.models as m

    load_path = Path("app/local") / "input"
    if not load_path.exists():
        raise NameError("No such file exists")

    # TODO: Refactor this so there isnt code duplication
    for file in load_path.glob("similarweb*"):
        log.info("Found SimilarWeb file to ingest", file=file)

        # Check to see if we have processed this file before
        if m.Event.query.filter_by(path=str(file)).one_or_none():
            log.warn("Duplicate file found", file=file)
            continue

        # Create a new event for the file being ingested
        event = m.Event.create(path=str(file))
        m.db.session.flush()

        # We don't check headers as this class has a complex structuring strategy
        content = file.read_bytes()
        parsed_content = csv_to_attrs(
            SimilarWebIn, SimilarWebConverter, content, check_headers=False
        )

        # persist to model layer
        for page in parsed_content:
            m.PageScrape.create_from_similar_web(event=event, sw_page=page)

        m.db.session.commit()
