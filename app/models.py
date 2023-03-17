from __future__ import annotations
from typing import List
from attrs import asdict
from structlog import get_logger

from app import db
from datetime import datetime
from sqlalchemy import ForeignKey, String, UnicodeText, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.support.similarweb import SimilarWebIn

log = get_logger(name=__name__)


class Event(db.Model):  # type: ignore
    """
    Events are a record of the fact that a file has been ingested. This is persisted
    to prevent duplication of data by processing a file twice.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (UniqueConstraint("path"),)

    @classmethod
    def create(cls, path: str) -> Event:
        event = cls(path=path)
        db.session.add(event)
        return event


class Page(db.Model):  # type: ignore
    """
    Page is to ensure that a scrape we can identify a single website being scraped
    multiple timesand records. This class also exists to make analysis of traffic
    and demographics easier, as those records are not created each time there
    has been data scraped.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    website: Mapped[str] = mapped_column(UnicodeText(100))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    scrapes: Mapped[List[PageScrape]] = relationship(
        back_populates="page", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("website"),)


class PageScrape(db.Model):  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(UnicodeText(265))

    scraped_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))

    page_id: Mapped[int] = mapped_column(ForeignKey("page.id"))
    page: Mapped["Page"] = relationship()

    global_rank: Mapped[int]
    country_rank: Mapped[int]
    category_rank: Mapped[int]

    total_visits: Mapped[int]
    bounce_rate: Mapped[float]
    pages_per_visit: Mapped[float]
    avg_vist_duration: Mapped[int]

    demographics: Mapped[List[PageDemographics]] = relationship(
        back_populates="scrape", cascade="all, delete-orphan"
    )
    traffic: Mapped[List[PageTraffic]] = relationship(
        back_populates="scrape", cascade="all, delete-orphan"
    )
    countries_distribution: Mapped[List[PageCountriesDistribution]] = relationship(
        back_populates="scrape", cascade="all, delete-orphan"
    )

    @classmethod
    def create_from_similar_web(
        cls, *, event: Event, sw_page: SimilarWebIn
    ) -> PageScrape:
        page = Page.query.filter_by(website=sw_page.page).one_or_none()
        if not page:
            log.info(f"No page found, creating new record", website=sw_page.page)
            page = Page(website=sw_page.page)
            db.session.add(page)
            db.session.flush()

        scrape = cls(
            event_id=event.id,
            page_id=page.id,
            path=sw_page.path,
            scraped_at=sw_page.scraped_at,
            global_rank=sw_page.global_rank,
            country_rank=sw_page.country_rank,
            category_rank=sw_page.category_rank,
            total_visits=sw_page.total_visits,
            bounce_rate=sw_page.bounce_rate,
            pages_per_visit=sw_page.pages_per_visit,
            avg_vist_duration=sw_page.avg_vist_duration,
        )
        db.session.add(scrape)
        db.session.flush()

        additional_ids = dict(page_id=page.id, scrape_id=scrape.id)

        log.info(
            "Creating page scrape",
            page_id=page.id,
            page_scrape_id=scrape.id,
            page_path=scrape.path,
        )
        # Create all of the one to many data points
        for sw_traffic in sw_page.monthly_traffic:
            if PageTraffic.query.filter_by(
                page_id=page.id, month=sw_traffic.month, year=sw_traffic.year
            ).one_or_none():
                continue

            traffic = PageTraffic(**asdict(sw_traffic), **additional_ids)
            db.session.add(traffic)

        for sw_country in sw_page.country_distributions:
            country = PageCountriesDistribution(**asdict(sw_country), **additional_ids)
            db.session.add(country)

        for sw_demographics in sw_page.demographics:
            demographics = PageDemographics(**asdict(sw_demographics), **additional_ids)
            db.session.add(demographics)

        return scrape


class PageTraffic(db.Model):  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    page_rank: Mapped[int]
    month: Mapped[int]
    year: Mapped[int]
    traffic: Mapped[int]

    page_id: Mapped[int] = mapped_column(ForeignKey("page.id"))
    page: Mapped["Page"] = relationship()

    scrape_id: Mapped[int] = mapped_column(ForeignKey("page_scrape.id"))
    scrape: Mapped["PageScrape"] = relationship(back_populates="traffic")

    __table_args__ = (UniqueConstraint("page_id", "month", "year"),)


class PageDemographics(db.Model):  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    age_range: Mapped[str] = mapped_column(String(15))
    percentage_value: Mapped[float]

    page_id: Mapped[int] = mapped_column(ForeignKey("page.id"))
    page: Mapped["Page"] = relationship()

    scrape_id: Mapped[int] = mapped_column(ForeignKey("page_scrape.id"))
    scrape: Mapped["PageScrape"] = relationship(back_populates="demographics")


class PageCountriesDistribution(db.Model):  # type: ignore
    id: Mapped[int] = mapped_column(primary_key=True)
    rank: Mapped[int]
    country: Mapped[str] = mapped_column(UnicodeText(50))
    percentage_value: Mapped[float]

    page_id: Mapped[int] = mapped_column(ForeignKey("page.id"))
    page: Mapped["Page"] = relationship()

    scrape_id: Mapped[int] = mapped_column(ForeignKey("page_scrape.id"))
    scrape: Mapped["PageScrape"] = relationship(back_populates="countries_distribution")
