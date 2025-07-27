from pydantic import RootModel
import elwis_api.client
from elwis_api.models import ElwisFtmMessage


client = elwis_api.client.ApiClient()

messages = client.query()


class Export(RootModel):
    root: list[ElwisFtmMessage]


with open("result.json", "w") as f:
    f.write(Export(messages).model_dump_json())
