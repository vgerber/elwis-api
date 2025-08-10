from datetime import date
from zeep import Client

import api_client.models as models
from app.logger import get_logger

logger = get_logger()


class ApiClient:
    def __init__(self, url="https://nts40.elwis.de/server/web/MessageServer.php?wsdl"):
        self._client = Client(url)

    def query(
        self,
        date_start: date,
        date_end: date,
        message_type="FTM",
        paging=models.Paging(offset=0, limit=100, total_count=True),
    ):
        #'get_messages(message_type: ns0:message_type_type, ids: ns0:id_pair[], validity_period: ns1:validity_period_type, dates_issue: ns0:date_pair[], paging_request: ns0:paging_request_type) -> result_message: ns1:RIS_Message_Type[], result_error: ns0:error_code_type[], paging_result: ns0:paging_result_type'
        response = self._client.service.get_messages(
            message_type,
            [],
            {"date_start": date_start.isoformat(), "date_end": date_end.isoformat()},
            [],
            {
                "offset": paging.offset,
                "limit": paging.limit,
                "total_count": paging.total_count,
            },
        )

        result_message = response.result_message

        messages: list[models.ElwisFtmItem] = []

        for message in result_message:
            try:
                messages += models.parse_result_message(message)
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
                continue
        return models.ElwisFtmQueryResponse(
            paging_result=models.PagingResult(
                count=response.paging_result.count,
                offset=response.paging_result.offset,
                total_count=response.paging_result.total_count,
            ),
            messages=messages,
        )
