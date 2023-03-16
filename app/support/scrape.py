import re

from js2xml import parse
from structlog import get_logger
from typing import Dict
from bs4 import BeautifulSoup

log = get_logger(name=__name__)


def scrape_similarweb_data(page: BeautifulSoup) -> Dict[str, str]:
    data_points = {}

    title = page.select(".wa-overview__title")
    assert len(title) == 1, "Overview title not found"
    data_points["Page"] = title.pop().text

    rank_list = page.select("div.wa-rank-list__item")
    assert (
        len(rank_list) == 3
    ), f"Ranking list is malformed, expected 3 items, found {len(rank_list)}"
    for item in rank_list:
        key, val, *_ = item.contents
        data_points[key.text] = val.text if val.text != "- -" else ""

    # fetch the engagement list and items
    data_points.update(_scrape_engagement(page))

    # fetch the ranking data

    # We wrap the following elements in a try/catch because the elements
    # may not exist for pages with really low traffic. The website itself
    # does not contain the elements so we assume it is None.

    # fetch the traffic chart
    try:
        data_points.update(_scrape_traffic(page))
    except Exception as error:
        # Add blank data points
        data_points.update(
            {
                "Monthly Traffic P1": "",
                "Monthly Traffic P2": "",
                "Monthly Traffic P3": "",
            }
        )
        log.error(
            "Failed to scrape traffic data points",
            page=page.title.text,  # type: ignore
            error=error,
            process="traffic_data",
        )

    # get the top countries list
    try:
        data_points.update(_scrape_countries(page))
    except Exception as error:
        data_points.update(
            {
                "Top Countries (1)": "",
                "Top Countries (2)": "",
                "Top Countries (3)": "",
                "Top Countries (4)": "",
                "Top Countries (5)": "",
            }
        )
        log.error(
            "Failed to scrape countries data points",
            page=page.title.text,  # type: ignore
            error=error,
            process="countries_data",
        )

    # fetch age distribution chart
    try:
        data_points.update(_scrape_demographics(page))
    except Exception as error:
        data_points.update(
            {
                "Demographics (18 - 24)": "",
                "Demographics (25 - 34)": "",
                "Demographics (35 - 44)": "",
                "Demographics (45 - 54)": "",
                "Demographics (55 - 64)": "",
                "Demographics (65+)": "",
            }
        )
        log.error(
            "Failed to scrape demographics data points",
            page=page.title.text,  # type: ignore
            error=error,
            process="demographics_data",
        )

    return data_points


def _scrape_engagement(page: BeautifulSoup) -> Dict[str, str]:
    data_points = {}
    engagement_list = page.select("div.engagement-list__item")
    for item in engagement_list:
        # Assert that all list is in the right shape and hasn't changed
        content_len = len(item.contents)
        assert (
            content_len == 2
        ), "Expected only 2 elements in {item.text}, but found: {content_len}"

        key, val = item.contents
        data_points[key.text] = val.text if val.text != "- -" else ""

    return data_points


def _scrape_traffic(page: BeautifulSoup) -> Dict[str, str]:
    # Get the chart and labels
    traffic_chart = page.select("div.wa-traffic__chart").pop()
    traffic_labels = traffic_chart.select(".highcharts-xaxis-labels").pop().contents

    # scrape the required text
    traffic_chart_keys = [item.text for item in traffic_labels]  # type: ignore
    traffic_chart_vals = [
        item.text for item in traffic_chart.select(".highcharts-data-label")
    ]
    return {
        f"Monthly Traffic P{idx+1}": f"{key}:{val}"
        for idx, (key, val) in enumerate(zip(traffic_chart_keys, traffic_chart_vals))
    }


def _scrape_countries(page: BeautifulSoup) -> Dict[str, str]:
    data_points = {}
    countries_list = page.select(".wa-geography__country-info")
    # We only need the top five countries
    for i in range(5):
        item = countries_list[i]
        country = item.select(".wa-geography__country-name").pop()
        percentage_val = item.select(".wa-geography__country-traffic-value").pop()
        key = f"Top Countries ({i + 1})"
        data_points[key] = f"{country.text}:{percentage_val.text}"

    return data_points


def _scrape_demographics(page: BeautifulSoup) -> Dict[str, str]:
    age_chart = page.select("div.wa-demographics__age-chart").pop()
    age_labels = age_chart.select(".highcharts-xaxis-labels").pop().contents
    age_chart_keys = [f"Demographics ({item.text})" for item in age_labels]
    age_chart_vals = [
        # We need to clean these values now to make our lives easier
        item.text if item.text != "--" else ""
        for item in age_chart.select(".highcharts-data-label")
    ]
    return dict(zip(age_chart_keys, age_chart_vals))
