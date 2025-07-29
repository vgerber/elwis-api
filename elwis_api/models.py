import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, RootModel


class ISRSLocationData(BaseModel):
    """
    ISRS = International Ship Reporting Standard
    """

    un_locode: str = Field(
        ..., description="United Nations Code for Trade and Transport Locations"
    )
    fairway_section: str
    object_reference: str
    section_hectometer: int


def parse_isrs_location_code(code: str) -> ISRSLocationData:
    return ISRSLocationData(
        un_locode=code[0:5],
        fairway_section=code[5:10],
        object_reference=code[10:15],
        section_hectometer=int(code[15:20]),
    )


class TargetGroup(BaseModel):
    target_group_code: str
    direction_code: str


class Coordinate(BaseModel):
    lat: str
    long: str


class ValidityPeriod(BaseModel):
    start: datetime.date
    end: Optional[datetime.date]


class NtsNumber(BaseModel):
    organisation: str
    year: int
    number: int
    serial_number: int


class Communication(BaseModel):
    reporting_code: str
    communication_code: str
    number: str
    label: Optional[str]
    remark: Optional[str]


class GeoObject(BaseModel):
    id: list[ISRSLocationData]
    name: str
    type_code: str
    position_code: Optional[str]
    coordinate: list[Coordinate]
    fairway_name: Optional[str]


def parse_geo_object(obj: object) -> GeoObject:
    return GeoObject(
        id=[parse_isrs_location_code(code) for code in obj.id],
        name=obj.name,
        type_code=obj.type_code,
        position_code=obj.position_code,
        coordinate=[
            Coordinate(lat=coord.lat, long=coord.long) for coord in obj.coordinate
        ],
        fairway_name=obj["fairway_name"] if "fairway_name" in obj else None,
    )


class LimitationPeriod(BaseModel):
    date_start: datetime.date
    date_end: Optional[datetime.date]
    time_start: datetime.time
    time_end: Optional[datetime.time]
    interval_code: str


class Limitation(BaseModel):
    limitation_period: list[LimitationPeriod]
    limitation_code: str
    position_code: Optional[str]
    value: Optional[float | int]
    unit: Optional[str]
    reference_code: Optional[str]
    indication_code: Optional[str]
    target_group: list[TargetGroup]


def parse_limitation(items: object) -> list[Limitation]:
    return [
        Limitation(
            limitation_period=[
                LimitationPeriod(
                    date_start=period.date_start,
                    date_end=period.date_end,
                    time_start=period.time_start,
                    time_end=period.time_end,
                    interval_code=period.interval_code,
                )
                for period in item.limitation_period
            ],
            limitation_code=item.limitation_code,
            position_code=item.position_code,
            value=item.value,
            unit=item.unit,
            reference_code=item.reference_code,
            indication_code=item.indication_code,
            target_group=[
                TargetGroup(
                    target_group_code=group.target_group_code,
                    direction_code=group.direction_code,
                )
                for group in item.target_group
            ],
        )
        for item in items
    ]


class FtmObject(BaseModel):
    value_type: Literal["object"] = "object"
    geo_object: GeoObject
    limitation: list[Limitation]


class FtmFairwaySection(BaseModel):
    value_type: Literal["fairway_section"] = "fairway_section"
    geo_object: GeoObject
    limitation: list[Limitation]


class FtmValue(BaseModel):
    fairway_section: Optional[FtmFairwaySection] = None
    object: Optional[FtmObject] = None


class Identification(BaseModel):
    internal_id: Optional[str]
    service: str = Field(
        ..., description="Service/Tool used to publish (also know as 'from')"
    )
    originator: str
    country_code: str
    language_code: str
    district: Optional[str]
    date_issue: datetime.datetime


def parse_identification(obj: object) -> Identification:
    return Identification(
        internal_id=obj.internal_id,
        service=obj["from"],
        originator=obj.originator,
        country_code=obj.country_code,
        language_code=obj.language_code,
        district=obj.district,
        date_issue=obj.date_issue,
    )


class ElwisFtmMessage(BaseModel):
    internal_id: Optional[str] = None
    identification: Identification
    nts_number: NtsNumber = Field(..., description="NtS (Notices to Skippers)")
    contents: Optional[str]
    reason_code: str
    subject_code: Literal["ANNOUN", "WARNIN", "CANCEL", "INFSER"]
    source: str
    validity_period: ValidityPeriod
    values: list[FtmValue]


class RiverMessages(RootModel):
    root: list[ElwisFtmMessage]


class Paging(BaseModel):
    offset: int = 0
    limit: int = 100
    total_count: bool = True


class PagingResult(BaseModel):
    offset: int
    count: int
    total_count: Optional[int]


class ElwisFtmQueryResponse(BaseModel):
    paging_result: PagingResult
    messages: list[ElwisFtmMessage]
