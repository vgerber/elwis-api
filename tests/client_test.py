from datetime import date
import api_client.client

client = api_client.client.ApiClient()

result = client.query(date_start=date.today(), date_end=date.today())


with open("result.json", "w") as f:
    f.write(result.model_dump_json())
