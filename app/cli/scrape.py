import click

from datetime import datetime
from pathlib import Path
from structlog import get_logger
from bs4 import BeautifulSoup

from app.support.scrape import scrape_similarweb_data
from app.support.serialise import attrs_to_csv, dict_to_attrs
from app.support.similarweb import SimilarWebConverter, SimilarWebRaw

log = get_logger(name=__name__)


@click.group("scrape", help="Commands for scraping data")
def scrape():
    pass


@scrape.command("parse_all_pages")
def parse_all_pages():
    # TODO: Check if local parameter set, if not scrape actual web page
    path = Path("app/local") / "scraped_pages"
    if not path.exists():
        raise NameError(f"Local scraping directory does not exist")

    # Collect all of the required data points from the locally stored pages
    data_points = []
    for file in path.glob("*.html"):
        log.info("Attempting to scrape page", file=file)
        # Access a local copy of the html pages
        page_file = open(file, "r")
        page = BeautifulSoup(page_file, "html.parser")

        # Retrieve all of the required data points for the pages
        scraped_attributes = scrape_similarweb_data(page)
        scraped_attributes["Path"] = str(file)
        scraped_attributes["Scraped At"] = datetime.utcnow().isoformat()
        data_points.append(scraped_attributes)

    # Output the files to a CSV locally
    # Serialse into a structured format
    log.info("Serialising scraped data", format="SimilarWebRaw")
    page_data = dict_to_attrs(SimilarWebRaw, data_points)

    # Encode using converter
    content = attrs_to_csv(SimilarWebRaw, SimilarWebConverter, page_data)

    # write file locally
    write_path = Path("app/local") / "input"
    if not write_path.exists():
        log.info("Creating local directory for saving scraped data", parents=True)
        write_path.mkdir(parents=True)

    write_file_name = write_path / datetime.utcnow().strftime(
        "similarweb_%Y%m%d_%H%M%S.csv"
    )

    log.info(
        "Writing scraped data locally", directory=write_path, filename=write_file_name
    )
    write_file_name.write_bytes(content)


@scrape.command(
    "parse_similarweb_page", help="Extract data from similarweb for a given page"
)
def parse_similarweb_page(location: str, local: bool = True):
    # TODO: make this work for live websites
    if not local:
        assert "https://www.similarweb.com/website/" in location
        raise NotImplementedError()

    # Read the local path
    path = Path("local") / "scraped_pages" / location
    if not path.exists():
        raise NameError(f"{location} does not exist")

    # Gather page data with BeautifulSoup
    page_file = open(path, "r")
    page = BeautifulSoup(page_file, "html.parser")

    # Store all of the attributes we are required to scrape
    scraped_attributes = scrape_similarweb_data(page)
    scraped_attributes["Path"] = location
    scraped_attributes["Scraped At"] = datetime.utcnow().isoformat()

    # Output the files to a CSV locally
    # Serialse into a structured format
    data = dict_to_attrs(SimilarWebRaw, [scraped_attributes])

    # Encode using converter
    content = attrs_to_csv(SimilarWebRaw, SimilarWebConverter, data)

    # write file locally
    write_path = Path("local") / "input"
    if not write_path.exists():
        write_path.mkdir(parents=True)

    write_file_name = (
        write_path / f"similarweb_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    )
    write_file_name.write_bytes(content)
