import json
from zeep import Client
import datetime

class ISRSLocationData:
    un_locode: str
    fairway_section: str
    object_reference: str
    section_hectometer: int

class RiverLocationPoint:
    isrs: ISRSLocationData
    coord: str

    def __init__(self) -> None:
        self.isrs = ISRSLocationData()

class RiverLocationData:
    start: RiverLocationPoint
    end: RiverLocationPoint

    def __init__(self) -> None:
        self.start = RiverLocationPoint()
        self.end = RiverLocationPoint()

class ValidityPeriod:
    start: datetime.date
    end: datetime.date

class RiverMessage:
    content: str
    reason_code: str
    subject_code: str
    source: str
    location: RiverLocationData
    validity_period: ValidityPeriod

    def __init__(self) -> None:
        self.location = RiverLocationData()
        self.validity_period = ValidityPeriod()

def parse_isrs_location_code(code: str) -> ISRSLocationData:
    location_data = ISRSLocationData()
    location_data.un_locode = code[0:5]
    location_data.fairway_section = code[5:10]
    location_data.object_reference = code[10:15]
    location_data.section_hectometer = int(code[15:20])
    return location_data

print("Test")

client = Client('https://nts40.elwis.de/server/web/MessageServer.php?wsdl')
#'get_messages(message_type: ns0:message_type_type, ids: ns0:id_pair[], validity_period: ns1:validity_period_type, dates_issue: ns0:date_pair[], paging_request: ns0:paging_request_type) -> result_message: ns1:RIS_Message_Type[], result_error: ns0:error_code_type[], paging_result: ns0:paging_result_type'
response = client.service.get_messages("FTM", [], { "date_start": "2024-09-22", "date_end": "2024-10-31"}, [], { "offset": 0, "limit":  1000, "total_count": True})
result_message = response.result_message
# 'DEXXX 03201 00000 00151'
"""
-> DEXXXX = DE
-> 
"""

elbe_messages: list[RiverMessage] = []
for message in result_message:
    try: 
        location = message.ftm[0]["_value_1"][0]['fairway_section'].geo_object
        print(location["fairway_name"])
        if location["fairway_name"] == "Elbe":
            location_start = parse_isrs_location_code(location.id[0])
            location_end = parse_isrs_location_code(location.id[1])
            if location_end.section_hectometer > 850:
                continue
            
            river_message = RiverMessage()

            ftm = message.ftm[0]
            river_message.content = ftm.contents
            river_message.source = ftm.source
            river_message.subject_code = ftm.subject_code
            river_message.reason_code = ftm.reason_code
            river_message.validity_period.start = ftm.validity_period.date_start
            river_message.validity_period.end = ftm.validity_period.date_end
            river_message.location.start.coord = location["coordinate"][0]
            river_message.location.start.isrs = location_start
            river_message.location.end.coord = location["coordinate"][1]
            river_message.location.end.isrs = location_end
            elbe_messages.append(river_message)
    except:
        None

print([message.subject_code for message in elbe_messages ])
print(response)




