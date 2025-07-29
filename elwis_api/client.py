from datetime import date
from zeep import Client

import elwis_api.models as models


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

        messages: list[models.ElwisFtmMessage] = []

        for message in result_message:
            identification = models.parse_identification(message.identification)

            for ftm_message in message.ftm:
                values: list[models.FtmValue] = []
                for ftm_value in ftm_message["_value_1"]:
                    fairway_section: models.FtmFairwaySection = None
                    ftm_object: models.FtmObject = None
                    if "fairway_section" in ftm_value:
                        fairway_section = models.FtmFairwaySection(
                            value_type="fairway_section",
                            geo_object=models.parse_geo_object(
                                ftm_value["fairway_section"].geo_object
                            ),
                            limitation=models.parse_limitation(
                                ftm_value["fairway_section"].limitation
                            ),
                        )
                    if "object" in ftm_value:
                        ftm_object = models.FtmObject(
                            value_type="object",
                            geo_object=models.parse_geo_object(
                                ftm_value["object"].geo_object
                            ),
                            limitation=models.parse_limitation(
                                ftm_value["object"].limitation
                            ),
                        )
                    values.append(
                        models.FtmValue(
                            fairway_section=fairway_section, object=ftm_object
                        ),
                    )

                messages.append(
                    models.ElwisFtmMessage(
                        internal_id=ftm_message.internal_id,
                        identification=identification,
                        nts_number=models.NtsNumber(
                            number=ftm_message.nts_number.number,
                            year=ftm_message.nts_number.year[0],  # e.g. (2025, None)
                            serial_number=ftm_message.nts_number.serial_number,
                            organisation=ftm_message.nts_number.organisation,
                        ),
                        contents=ftm_message.contents,
                        source=ftm_message.source,
                        subject_code=ftm_message.subject_code,
                        reason_code=ftm_message.reason_code,
                        validity_period=models.ValidityPeriod(
                            start=ftm_message.validity_period.date_start,
                            end=ftm_message.validity_period.date_end,
                        ),
                        values=values,
                    )
                )
        return models.ElwisFtmQueryResponse(
            paging_result=models.PagingResult(
                count=response.paging_result.count,
                offset=response.paging_result.offset,
                total_count=response.paging_result.total_count,
            ),
            messages=messages,
        )
