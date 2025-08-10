from datetime import date


from api_client.client import ApiClient
from api_client.models import ElwisFtmItem, Paging
from app.logger import get_logger

logger = get_logger()


def fetch_all_messages_for_day(date: date, page_count=25) -> list[ElwisFtmItem]:
    return fetch_all_messages_for_date(
        date_start=date, date_end=date, page_count=page_count
    )


def fetch_all_messages_for_date(
    date_start: date, date_end: date, page_count=25
) -> list[ElwisFtmItem]:
    elwis_api_client = ApiClient()

    messages = []
    query_page_offset = 0

    while True:
        response = elwis_api_client.query(
            date_start=date_start,
            date_end=date_end,
            paging=Paging(offset=query_page_offset, limit=page_count, total_count=True),
        )

        messages += response.messages

        query_page_offset += len(response.messages)
        logger.info(
            f"Fetched {query_page_offset}/{response.paging_result.total_count} messages for {date_start} to {date_end}"
        )
        if query_page_offset >= response.paging_result.total_count:
            break
    return messages
