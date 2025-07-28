import os
from ..config import herbalista_config
from phoenix.otel import register

# if phoenix server is running register the tracer
# check if the phoenix server is running by checking if the endpoint is responding
import requests
def is_phoenix_running(endpoint: str) -> bool:
    try:
        response = requests.get(endpoint)
        return response.status_code == 200
    except requests.RequestException:
        return False

# If the PHOENIX_OTEL_ENDPOINT environment variable is set, use it to register the tracer
if herbalista_config.PHOENIX_COLLECTOR_ENDPOINT and is_phoenix_running(herbalista_config.PHOENIX_COLLECTOR_ENDPOINT):
    # If the Phoenix server is running, register the tracer
    print(f"Registering Phoenix tracer with endpoint: {herbalista_config.PHOENIX_COLLECTOR_ENDPOINT}")
    # configure the Phoenix tracer
    tracer_provider = register(
    project_name=herbalista_config.PHOENIX_PRJ_NAME, # Default is 'default'
    auto_instrument=True # Auto-instrument your app based on installed OI dependencies
    ,endpoint=herbalista_config.PHOENIX_COLLECTOR_ENDPOINT
    )