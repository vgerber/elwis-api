import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlmodel import select

from api_client.models import ElwisFtmItem, ElwisFtmQueryResponse, Paging, PagingResult
from app.database import SessionDep
from app.models.ftm import FairwaySection


router = APIRouter(prefix="/ftm", tags=["Fairway Transfer Messages"])


class FtmQuery(BaseModel):
    paging: Paging = Field(
        default=Paging(offset=0, limit=100, total_count=True),
        description="Paging parameters for the query",
    )
    number: str = Field(default=None, description="FTM message number")
    year: int = Field(default=None, description="FTM message year")
    serial_number: str = Field(default=None, description="FTM message serial number")
    fairway_name: str = Field(default=None, description="FTM message fairway name")
    hectometer_start: int = Field(
        default=None, description="FTM message hectometer start"
    )
    hectometer_end: int = Field(default=None, description="FTM message hectometer end")
    validity_start: datetime.date = Field(
        default=None, description="FTM message validity start date in ISO format"
    )
    validity_end: datetime.date = Field(
        default=None, description="FTM message validity end date in ISO format"
    )


@router.post("/search")
def search_ftm_messages(query: FtmQuery, session: SessionDep) -> ElwisFtmQueryResponse:
    query_statement = select(FairwaySection)

    if query.fairway_name:
        query_statement = query_statement.where(
            FairwaySection.fairway_name == query.fairway_name
        )
    if query.number:
        query_statement = query_statement.where(
            FairwaySection.ftm_number == query.number
        )
    if query.year:
        query_statement = query_statement.where(FairwaySection.ftm_year == query.year)
    if query.serial_number:
        query_statement = query_statement.where(
            FairwaySection.ftm_serial_number == query.serial_number
        )
    if query.hectometer_start is not None:
        query_statement = query_statement.where(
            FairwaySection.start_hectometer >= query.hectometer_start
        )
    if query.hectometer_end is not None:
        query_statement = query_statement.where(
            FairwaySection.end_hectometer <= query.hectometer_end
        )
    if query.validity_start:
        query_statement = query_statement.where(
            FairwaySection.ftm_message.validity_date_start >= query.validity_start
        )
    if query.validity_end:
        query_statement = query_statement.where(
            FairwaySection.ftm_message.validity_date_end <= query.validity_end
        )

    fairway_sections = session.exec(query_statement).all()

    messages = [
        ElwisFtmItem(**section.ftm_message.message) for section in fairway_sections
    ]

    return ElwisFtmQueryResponse(
        paging_result=PagingResult(offset=0, count=0, total_count=100),
        messages=messages,
    )
