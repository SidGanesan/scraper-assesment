from rich.console import Console
import pandas as pd
import matplotlib.pyplot as plt
import app.models as m

from datetime import datetime
from structlog import get_logger


log = get_logger(name=__name__)
console = Console()


def _parse_date(month: int, year: int) -> datetime:
    return datetime.strptime(f"{month}{year}", "%m%Y")


def _monthly_growth(df: pd.DataFrame) -> pd.DataFrame:
    # Get the date and set as index to make graphing easier
    df["date"] = df.apply(lambda x: _parse_date(x.month, x.year), axis=1)
    df.set_index("date", inplace=True)

    df["last_traffic"] = df.traffic.shift()
    df["mom_traffic_growth"] = df.traffic / df.last_traffic - 1
    return df


def all_analysis() -> None:
    # Get db connection to execute SQL and load query from file
    connection = m.db.engine.connect().connection
    query = """
    -- month-on-month-traffic
    select p.website, pt.month, pt.year, pt.traffic
    from page p
    join page_scrape ps on ps.page_id = p.id
    join page_traffic pt on pt.scrape_id = ps.id
    order by p.website, pt.year asc, pt.month asc;
    """
    # fetch the required data
    log.info("Fetching data for all analysis")
    df = pd.read_sql_query(query, connection)
    # month on month change in web vists

    frames = []
    grouped_by_site = df.groupby("website")
    for _, site_df in grouped_by_site:
        frames.append(_monthly_growth(site_df))

    growth_df = pd.concat(frames)
    console.print(growth_df)
