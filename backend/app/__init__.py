import os
from anyio import Path
import dotenv
# Load environment variables from .env file
dotenv.load_dotenv(dotenv_path=".env")

DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")

import logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.root.setLevel(logging.DEBUG)

from app.features import user_auth
from app.core import monitoring
