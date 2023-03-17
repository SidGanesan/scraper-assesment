from pathlib import Path
from rich.console import Console
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
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

    save_path = Path("app") / "local" / "output"
    if not save_path.exists():
        save_path.mkdir(parents=True)

    grouped_by_site = df.groupby("website")
    for site, site_df in grouped_by_site:
        site_df = _monthly_growth(site_df)
        plt.bar(site_df.index, site_df.mom_traffic_growth, width=3)
        plt.title(f"Monthly change in traffic for {site}", fontsize=20)

        # set axis lines
        plt.axhline(y=0, color='k', linestyle='-')
        plt.axhline(y=site_df.mom_traffic_growth.mean(), color='r', linestyle='-.', linewidth=1, label="Avg Growth")

        # Percentage Formatting
        plt.ylabel("Percentage Growth (%)", fontsize=12)
        y = plt.gca().yaxis 
        y.set_major_formatter(mticker.PercentFormatter())
        
        # Month formatting
        plt.xlabel("Month", fontsize=20)
        x = plt.gca().xaxis
        x.set_major_locator(mdates.MonthLocator())
        x.set_major_formatter(mdates.DateFormatter("%b %y"))

        name = str(site).split(".")[0]
        save_path = Path("app") / "local" / "output" / f"{name}.png"
        log.info("Saving graphs", path=save_path)
        plt.savefig(save_path)
        
