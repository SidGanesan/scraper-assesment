import pytest

from support.similarweb import SimilarWebConverter, SimilarWebIn


def test_structure__similiar_web_in__happy_path():
    test_dict = {
        "Path": "local/scraped_pages/similarweb-google-com.html",
        "Scraped At": "2023-03-15T12:49:28.850051",
        "Page": "google.com",
        "Global Rank": "#1",
        "Country Rank": "#1",
        "Category Rank": "#1",
        "Total Visits": "86.4B",
        "Bounce Rate": "28.77%",
        "Pages per Visit": "8.29",
        "Avg Visit Duration": "00:10:35",
        "Monthly Traffic P1": "Oct:87.0B",
        "Monthly Traffic P2": "Nov:85.1B",
        "Monthly Traffic P3": "Dec:86.4B",
        "Top Countries (1)": "United States:27.04%",
        "Top Countries (2)": "India:4.51%",
        "Top Countries (3)": "Brazil:4.39%",
        "Top Countries (4)": "United Kingdom:3.81%",
        "Top Countries (5)": "Japan:3.70%",
        "Demographics (18 - 24)": "23.86%",
        "Demographics (25 - 34)": "30.32%",
        "Demographics (35 - 44)": "18.79%",
        "Demographics (45 - 54)": "12.75%",
        "Demographics (55 - 64)": "8.63%",
        "Demographics (65+)": "5.64%",
    }

    result = SimilarWebConverter.structure(test_dict, SimilarWebIn)

    assert result.global_rank == 1
    assert len(result.demographics) == 6
    assert len(result.country_distributions) == 5
    assert len(result.monthly_traffic) == 3


def test_structure__similar_web_in__nulls():
    test_dict = {
        "Path": "local/scraped_pages/similarweb-byte-trading-com.html",
        "Scraped At": "2023-03-15T12:49:29.094564",
        "Page": "byte-trading.com",
        "Global Rank": "#7,277,9362,350,824",
        "Country Rank": "#755,500",
        "Category Rank": "",
        "Total Visits": "< 5K",
        "Bounce Rate": "",
        "Pages per Visit": "",
        "Avg Visit Duration": "",
        "Monthly Traffic P1": "",
        "Monthly Traffic P2": "",
        "Monthly Traffic P3": "",
        "Top Countries (1)": "",
        "Top Countries (2)": "",
        "Top Countries (3)": "",
        "Top Countries (4)": "",
        "Top Countries (5)": "",
        "Demographics (18 - 24)": "",
        "Demographics (25 - 34)": "",
        "Demographics (35 - 44)": "",
        "Demographics (45 - 54)": "",
        "Demographics (55 - 64)": "",
        "Demographics (65+)": "",
    }

    result = SimilarWebConverter.structure(test_dict, SimilarWebIn)

    assert result.global_rank == 7_277_9362_350_824
