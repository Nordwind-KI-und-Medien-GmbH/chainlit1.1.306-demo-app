from app.core.lib.singleton_per_signature import singleton_per_signature
from core.config import herbalista_config
from langchain_openai import AzureChatOpenAI

@singleton_per_signature
class HerbalistaChatLLM(AzureChatOpenAI):
    def __init__(self,azure_deployment = herbalista_config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, # type: ignore
            openai_api_version = herbalista_config.AZURE_OPENAI_API_VERSION, # type: ignore
            azure_endpoint = herbalista_config.AZURE_OPENAI_ENDPOINT,
            api_key = herbalista_config.AZURE_OPENAI_API_KEY,
            model_name = herbalista_config.AZURE_OPENAI_CHAT_MODEL_NAME, #"gpt-4o-mini", # type: ignore
            temperature = herbalista_config.AZURE_OPENAI_CHAT_MODEL_TEMPERATURE,
            streaming = herbalista_config.AZURE_OPENAI_CHAT_STREAMING, # type: ignore
            **kwargs):
        super().__init__(
            azure_deployment=azure_deployment,
            api_version=openai_api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            model_name=model_name, # type: ignore
            temperature=temperature,
            streaming=streaming,
            **kwargs
        )