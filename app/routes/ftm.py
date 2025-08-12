import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlmodel import funcfilter, select

from api_client.models import ElwisFtmItem, ElwisFtmQueryResponse, Paging, PagingResult
from app.database import SessionDep
from app.models.ftm import ElwisFtm, FairwaySection


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
    validity_date_start: datetime.date = Field(
        default=None, description="FTM message validity start date in ISO format"
    )
    validity_date_end: datetime.date = Field(
        default=None, description="FTM message validity end date in ISO format"
    )


@router.post("/search")
def search_ftm_messages(query: FtmQuery, session: SessionDep) -> ElwisFtmQueryResponse:
    # Build the base query with a join to ElwisFtm for date filtering
    query_statement = select(FairwaySection).join(
        ElwisFtm,
        (FairwaySection.ftm_year == ElwisFtm.year)
        & (FairwaySection.ftm_number == ElwisFtm.number)
        & (FairwaySection.ftm_serial_number == ElwisFtm.serial_number),
    )

    where_clauses = []
    if query.fairway_name:
        where_clauses.append(FairwaySection.fairway_name == query.fairway_name)
    if query.number:
        where_clauses.append(FairwaySection.ftm_number == query.number)
    if query.year:
        where_clauses.append(FairwaySection.ftm_year == query.year)
    if query.serial_number:
        where_clauses.append(FairwaySection.ftm_serial_number == query.serial_number)
    if query.hectometer_start is not None:
        where_clauses.append(FairwaySection.start_hectometer >= query.hectometer_start)
    if query.hectometer_end is not None:
        where_clauses.append(FairwaySection.end_hectometer <= query.hectometer_end)
    if query.validity_date_start:
        where_clauses.append(ElwisFtm.validity_date_start >= query.validity_date_start)
    if query.validity_date_end:
        where_clauses.append(ElwisFtm.validity_date_end <= query.validity_date_end)

    if where_clauses:
        query_statement = query_statement.where(*where_clauses)

    # Apply the same join and where clauses to the count query
    total_count = None
    if query.paging.total_count:
        count_stmt = (
            select(func.count())
            .select_from(FairwaySection)
            .join(
                ElwisFtm,
                (FairwaySection.ftm_year == ElwisFtm.year)
                & (FairwaySection.ftm_number == ElwisFtm.number)
                & (FairwaySection.ftm_serial_number == ElwisFtm.serial_number),
            )
        )
        if where_clauses:
            count_stmt = count_stmt.where(*where_clauses)
        total_count = session.exec(count_stmt).one()

    query_statement = query_statement.offset(query.paging.offset).limit(
        query.paging.limit
    )
    fairway_sections = session.exec(query_statement).all()

    messages = [
        ElwisFtmItem(**section.ftm_message.message) for section in fairway_sections
    ]

    return ElwisFtmQueryResponse(
        paging_result=PagingResult(
            offset=query.paging.offset, count=len(messages), total_count=total_count
        ),
        messages=messages,
    )
