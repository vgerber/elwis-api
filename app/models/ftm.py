import datetime
from click import Option
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from api_client.models import ElwisFtmItem, FtmValue, GeoObject
from app.logger import get_logger

logger = get_logger()


class FairwaySection(SQLModel, table=True):
    __tablename__ = "fairway_section"
    fairway_name: str = Field(
        description="Name of the fairway",
        foreign_key="fairway.name",
        primary_key=True,
    )
    ftm_year: int = Field(
        description="Year of the FTM message",
        foreign_key="elwis_ftm.year",
        primary_key=True,
    )
    ftm_number: int = Field(
        description="Number of the FTM message",
        foreign_key="elwis_ftm.number",
        primary_key=True,
    )
    ftm_serial_number: int = Field(
        description="Serial number of the FTM message",
        foreign_key="elwis_ftm.serial_number",
        primary_key=True,
    )
    start_hectometer: int = Field(
        primary_key=True,
        description="Start hectometer of the fairway",
    )
    end_hectometer: int = Field(
        primary_key=True,
        default=None,
        nullable=True,
        description="End hectometer of the fairway",
    )

    ftm_message: "ElwisFtm" = Relationship(
        sa_relationship_kwargs=dict(
            primaryjoin="and_(FairwaySection.ftm_year == ElwisFtm.year, FairwaySection.ftm_number == ElwisFtm.number, FairwaySection.ftm_serial_number == ElwisFtm.serial_number)",
            lazy="joined",
        ),
    )
    fairway: "Fairway" = Relationship(back_populates="sections")


class Fairway(SQLModel, table=True):
    name: str = Field(
        primary_key=True,
        description="Name of the fairway",
    )

    sections: list[FairwaySection] = Relationship(back_populates="fairway")


class ElwisFtm(SQLModel, table=True):
    __tablename__ = "elwis_ftm"
    year: int = Field(primary_key=True, description="Year of the entry")
    number: int = Field(primary_key=True, description="Number of the entry")
    serial_number: int = Field(
        primary_key=True,
        description="Serial number if number has multiple entries",
    )
    validity_date_start: datetime.date = Field(
        description="Start date of the entry",
    )
    validity_date_end: datetime.date = Field(
        default=None,
        nullable=True,
        description="End date of the entry",
    )
    message: dict = Field(
        default_factory=dict,
        description="Raw data of the entry",
        sa_column=Column(JSON),
    )


def get_fairway_sections(
    message: ElwisFtmItem,
) -> list[FairwaySection]:
    fairway_sections: list[FairwaySection] = []

    ftm = ElwisFtm(
        validity_date_start=message.validity_period.start,
        validity_date_end=message.validity_period.end,
        number=message.nts_number.number,
        year=message.nts_number.year,
        serial_number=message.nts_number.serial_number,
        message=message.model_dump(mode="json"),
    )

    def get_fairway(value: FtmValue):
        if value.fairway_section:
            return Fairway(name=value.fairway_section.geo_object.fairway_name)
        if value.object:
            return Fairway(name=value.object.geo_object.fairway_name)
        return None

    def get_fairway_section(fairway: Fairway, value: FtmValue) -> FairwaySection:
        geo_object: GeoObject = None
        if value.fairway_section:
            geo_object = value.fairway_section.geo_object
        elif value.object:
            geo_object = value.object.geo_object

        section_start = None
        section_end = None
        for id in geo_object.id:
            if section_start is None:
                section_start = id.section_hectometer
            elif section_start > id.section_hectometer:
                section_start = id.section_hectometer
            if section_end is None:
                section_end = id.section_hectometer
            elif section_end < id.section_hectometer:
                section_end = id.section_hectometer
        return FairwaySection(
            fairway=fairway,
            ftm_message=ftm,
            start_hectometer=section_start,
            end_hectometer=section_end,
        )

    for value in message.values:
        if not value.fairway_section and not value.object:
            logger.warning(f"No fairway section or object in value: {value}. Skipping.")
            continue
        if value.fairway_section and value.object:
            logger.warning(
                f"Both fairway section and object present in value: {value}. Skipping."
            )
            continue

        # Get fairway name
        fairway = get_fairway(value)
        if not fairway:
            continue

        # Get hectometer range
        fairway_section = get_fairway_section(fairway, value)
        if fairway_section:
            fairway_sections.append(fairway_section)

    return fairway_sections
