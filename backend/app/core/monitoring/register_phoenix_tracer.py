import os

# if phoenix server is running register the tracer
# check if the phoenix server is running by checking if the endpoint is responding
import requests
from phoenix.otel import register

from ..config import simple_rag_config


def is_phoenix_running(endpoint: str) -> bool:
    try:
        response = requests.get(endpoint)
        return response.status_code == 200
    except requests.RequestException:
        return False


# If the PHOENIX_OTEL_ENDPOINT environment variable is set, use it to register the tracer
if simple_rag_config.PHOENIX_COLLECTOR_ENDPOINT and is_phoenix_running(
    simple_rag_config.PHOENIX_COLLECTOR_ENDPOINT
):
    # If the Phoenix server is running, register the tracer
    print(
        f"Registering Phoenix tracer with endpoint: {simple_rag_config.PHOENIX_COLLECTOR_ENDPOINT}"
    )
    # configure the Phoenix tracer
    tracer_provider = register(
        project_name=simple_rag_config.PHOENIX_PRJ_NAME,  # Default is 'default'
        auto_instrument=True,  # Auto-instrument your app based on installed OI dependencies
        endpoint=simple_rag_config.PHOENIX_COLLECTOR_ENDPOINT,
    )
