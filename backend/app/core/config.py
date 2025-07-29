import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")


# Define the configuration class
class Config:
    STAGE = os.getenv("STAGE", "LOCAL")

    if STAGE == "LOCAL":
        DATABASE_URL = os.getenv("LOCAL_DB_URL", "")
    else:
        DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # Chainlit configuration
    CHAINLIT_URL = os.getenv("CHAINLIT_URL", "http://localhost:8000/")
    CHAINLIT_AUTH_SECRET = os.environ.get("CHAINLIT_AUTH_SECRET", "")
    if not CHAINLIT_AUTH_SECRET:
        # Fallback to CHAINLIT_AUTH_SECRET_1 if CHAINLIT_AUTH_SECRET is not set
        # This is useful for local development where you might have multiple secrets
        os.environ["CHAINLIT_AUTH_SECRET"] = os.environ.get(
            "CHAINLIT_AUTH_SECRET_1", ""
        )
        CHAINLIT_AUTH_SECRET = os.environ["CHAINLIT_AUTH_SECRET"]

    # Azure OpenAI and Search configuration
    AZURE_OPENAI_API_VERSION = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2025-01-01-preview"
    )
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")

    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini"
    )
    AZURE_OPENAI_CHAT_MODEL_NAME = os.getenv(
        "AZURE_OPENAI_CHAT_MODEL_NAME", "gpt-4o-mini"
    )
    AZURE_OPENAI_CHAT_MODEL_TEMPERATURE = float(
        os.getenv("AZURE_OPENAI_CHAT_MODEL_TEMPERATURE", "0.0")
    )
    AZURE_OPENAI_CHAT_MAX_TOKENS = int(
        os.getenv("AZURE_OPENAI_CHAT_MAX_TOKENS", "4096")
    )
    AZURE_OPENAI_CHAT_STREAMING = os.getenv(
        "AZURE_OPENAI_CHAT_STREAMING", "true"
    ).lower() in ("true", "1", "yes")

    AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "text-embedding-3-large"
    )
    AZURE_OPENAI_EMBEDDINGS_MODEL_NAME = os.getenv(
        "AZURE_OPENAI_EMBEDDINGS_MODEL_NAME", "text-embedding-3-large"
    )

    AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT", "")
    AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")

    OAUTH_AZURE_AD_CLIENT_ID = os.getenv("OAUTH_AZURE_AD_CLIENT_ID", "")
    OAUTH_AZURE_AD_CLIENT_SECRET = os.getenv("OAUTH_AZURE_AD_CLIENT_SECRET", "")
    OAUTH_AZURE_AD_TENANT_ID = os.getenv("OAUTH_AZURE_AD_TENANT_ID", "")
    OAUTH_AZURE_AD_ENABLE_SINGLE_TENANT = os.getenv(
        "OAUTH_AZURE_AD_ENABLE_SINGLE_TENANT", "true"
    ).lower() in ("true", "1", "yes")

    DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY", "")

    AZURE_SEARCH_APP_ID = os.getenv("AZURE_SEARCH_APP_ID", "")
    AZURE_SEARCH_APP_SECRET = os.getenv("AZURE_SEARCH_APP_SECRET", "")
    AZURE_SEARCH_CHAT_FILE_UPLOAD_INDEX_NAME = os.getenv(
        "AZURE_SEARCH_CHAT_FILE_UPLOAD_INDEX_NAME", "chat-file-upload-index"
    )
    AZURE_SEARCH_DEMO_RAG_INDEX_NAME = os.getenv(
        "AZURE_SEARCH_DEMO_RAG_INDEX_NAME", "simple-rag-index"
    )

    BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY", "")
    BING_SEARCH_ENDPOINT = os.getenv("BING_SEARCH_ENDPOINT", "")

    PHOENIX_COLLECTOR_ENDPOINT = os.getenv(
        "PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces"
    )
    PHOENIX_PRJ_NAME = os.getenv("PHOENIX_PRJ_NAME", "simple-rag-app")


simple_rag_config = Config()
