import attrs
import time
import re

from datetime import datetime, timedelta
from typing import Any, Dict, List
from cattrs import Converter


@attrs.define()
class SimilarWebRaw:
    """
    Structured class for the raw data scraped from SimilarWeb. The class helps
    to structure and unstructure the data in the way we want while being type
    safe using the cattrs converters
    """

    path: str = attrs.field(metadata={"alias": "Path"})
    scraped_at: str = attrs.field(metadata={"alias": "Scraped At"})
    page: str = attrs.field(metadata={"alias": "Page"})
    global_rank: str = attrs.field(metadata={"alias": "Global Rank"})
    country_rank: str = attrs.field(metadata={"alias": "Country Rank"})
    category_rank: str = attrs.field(metadata={"alias": "Category Rank"})
    total_visits: str = attrs.field(metadata={"alias": "Total Visits"})
    bounce_rate: str = attrs.field(metadata={"alias": "Bounce Rate"})
    pages_per_visit: str = attrs.field(metadata={"alias": "Pages per Visit"})
    avg_vist_duration: str = attrs.field(metadata={"alias": "Avg Visit Duration"})
    monthly_traffic_p1: str = attrs.field(metadata={"alias": "Monthly Traffic P1"})
    monthly_traffic_p2: str = attrs.field(metadata={"alias": "Monthly Traffic P2"})
    monthly_traffic_p3: str = attrs.field(metadata={"alias": "Monthly Traffic P3"})
    top_country_r1: str = attrs.field(metadata={"alias": "Top Countries (1)"})
    top_country_r2: str = attrs.field(metadata={"alias": "Top Countries (2)"})
    top_country_r3: str = attrs.field(metadata={"alias": "Top Countries (3)"})
    top_country_r4: str = attrs.field(metadata={"alias": "Top Countries (4)"})
    top_country_r5: str = attrs.field(metadata={"alias": "Top Countries (5)"})
    demgraphics_t1: str = attrs.field(metadata={"alias": "Demographics (18 - 24)"})
    demgraphics_t2: str = attrs.field(metadata={"alias": "Demographics (25 - 34)"})
    demgraphics_t3: str = attrs.field(metadata={"alias": "Demographics (35 - 44)"})
    demgraphics_t4: str = attrs.field(metadata={"alias": "Demographics (45 - 54)"})
    demgraphics_t5: str = attrs.field(metadata={"alias": "Demographics (55 - 64)"})
    demgraphics_t6: str = attrs.field(metadata={"alias": "Demographics (65+)"})


@attrs.define()
class SimilarWebMonthlyTraffic:
    page_rank: int
    month: int
    year: int
    traffic: int


@attrs.define()
class SimilarWebCountriesDistribution:
    rank: int
    country: str
    percentage_value: float


@attrs.define()
class SimilarWebDemographics:
    age_range: str
    percentage_value: float


@attrs.define()
class SimilarWebIn:
    """
    Structured class for picking up the scraped data from similar web and structuring
    it in a type safe way using cattrs. The converter will have a hook for structuring
    this class such that it will read the raw scrapped data and serialise it correctly.
    """

    path: str
    scraped_at: datetime
    page: str
    global_rank: int
    country_rank: int
    category_rank: int
    total_visits: int
    bounce_rate: float
    pages_per_visit: float
    avg_vist_duration: int
    monthly_traffic: List[SimilarWebMonthlyTraffic]
    country_distributions: List[SimilarWebCountriesDistribution]
    demographics: List[SimilarWebDemographics]


def _convert_big_number(val: str) -> int:
    if val == "< 5K":
        return 0

    unit = val[-1]
    float_val = float(val[:-1])

    if unit == "T":
        return int(float_val * 1_000)
    elif unit == "M":
        return int(float_val * 1_000_000)
    elif unit == "B":
        return int(float_val * 1_000_000_000)
    elif unit == "T":
        return int(float_val * 1_000_000_000)
    else:
        raise ValueError(f"Unknown unit when parsing. Recieved: {unit}")


def _convert_float(val: str) -> float:
    if val == "":
        return 0.0
    return float(val)


def _convert_percentage(val: str) -> float:
    if val == "":
        return 0.0
    return float(val[:-1])


def _convert_rank(val: str) -> int:
    if val == "":
        return 0
    assert (
        val[0] == "#"
    ), f"Incorrect formatting of val. Expected leading #, recieved {val}"
    return int(val[1:].replace(",", ""))


def _convert_time(val: str) -> int:
    if val == "":
        return 0
    time = datetime.strptime(val, "%H:%M:%S")
    return int(
        timedelta(
            hours=time.hour, minutes=time.minute, seconds=time.second
        ).total_seconds()
    )


def structure_similar_web_traffic(
    data: Dict[str, str], _: Any
) -> SimilarWebMonthlyTraffic:
    key, val = list(data.items()).pop()

    assert "Monthly Traffic" in key, f"Incorrect formatting for key. Recieved: {key}"
    month_name, raw_traffic = val.split(":")
    month = time.strptime(month_name, "%b").tm_mon
    year = datetime.now().year
    return SimilarWebMonthlyTraffic(
        page_rank=int(key[-1].replace(",", "")),
        month=month,
        year=year,
        traffic=_convert_big_number(raw_traffic),
    )


def structure_similar_web_countries(
    data: Dict[str, str], _: Any
) -> SimilarWebCountriesDistribution:
    key, val = list(data.items()).pop()

    assert "Top Countries" in key, f"Incorrect formatting for key, Recieved: {key}"
    rank = re.search(r"\(([0-9_]+)\)", key).groups()[0]  # type: ignore
    country, raw_pct = val.split(":")

    return SimilarWebCountriesDistribution(
        rank=int(rank.replace(",", "")),
        country=country,
        percentage_value=_convert_percentage(raw_pct),
    )


def structure_similar_web_demographics(
    data: Dict[str, str], _: Any
) -> SimilarWebDemographics:
    key, val = list(data.items()).pop()
    range = key[key.find("(") + 1 : -1]

    return SimilarWebDemographics(
        age_range=range, percentage_value=_convert_percentage(val)
    )


def structure_similar_web_in(data: Dict[str, str], _: Any) -> SimilarWebIn:
    # Check data is type safe
    assert all(isinstance(val, str) for val in data.values())

    monthly_traffic = []
    country_distributions = []
    demographics = []

    for key, val in data.items():
        if val == "":
            continue

        if "Monthly Traffic" in key:
            monthly_traffic.append(
                SimilarWebConverter.structure(
                    {key: val},
                    SimilarWebMonthlyTraffic,
                )
            )
        if "Top Countries" in key:
            country_distributions.append(
                SimilarWebConverter.structure(
                    {key: val},
                    SimilarWebCountriesDistribution,
                )
            )
        if "Demographics" in key:
            demographics.append(
                SimilarWebConverter.structure(
                    {key: val},
                    SimilarWebDemographics,
                )
            )

    return SimilarWebIn(
        path=data["Path"],
        scraped_at=datetime.fromisoformat(data["Scraped At"]),
        page=data["Page"],
        global_rank=_convert_rank(data["Global Rank"]),
        country_rank=_convert_rank(data["Country Rank"]),
        category_rank=_convert_rank(data["Category Rank"]),
        total_visits=_convert_big_number(data["Total Visits"]),
        bounce_rate=_convert_percentage(data["Bounce Rate"]),
        pages_per_visit=_convert_float(data["Pages per Visit"]),
        avg_vist_duration=_convert_time(data["Avg Visit Duration"]),
        monthly_traffic=monthly_traffic,
        country_distributions=country_distributions,
        demographics=demographics,
    )


# We define the converter here so that we can assign specific structure/unsstructure hooks
# based on the data types. See https://catt.rs/en/stable/converters.html for more detail
# on converters
SimilarWebConverter = Converter(forbid_extra_keys=True)
SimilarWebConverter.register_structure_hook(SimilarWebIn, structure_similar_web_in)
SimilarWebConverter.register_structure_hook(
    SimilarWebMonthlyTraffic, structure_similar_web_traffic
)
SimilarWebConverter.register_structure_hook(
    SimilarWebCountriesDistribution, structure_similar_web_countries
)
SimilarWebConverter.register_structure_hook(
    SimilarWebDemographics, structure_similar_web_demographics
)
