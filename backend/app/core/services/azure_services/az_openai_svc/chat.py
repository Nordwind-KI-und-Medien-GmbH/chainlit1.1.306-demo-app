from app.core.config import simple_rag_config
from app.core.lib.singleton_per_signature import singleton_per_signature
from langchain_openai import AzureChatOpenAI


@singleton_per_signature
class SimpleRagChatLLM(AzureChatOpenAI):
    def __init__(
        self,
        azure_deployment=simple_rag_config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,  # type: ignore
        openai_api_version=simple_rag_config.AZURE_OPENAI_API_VERSION,  # type: ignore
        azure_endpoint=simple_rag_config.AZURE_OPENAI_ENDPOINT,
        api_key=simple_rag_config.AZURE_OPENAI_API_KEY,
        model_name=simple_rag_config.AZURE_OPENAI_CHAT_MODEL_NAME,  # "gpt-4o-mini", # type: ignore
        temperature=simple_rag_config.AZURE_OPENAI_CHAT_MODEL_TEMPERATURE,
        streaming=simple_rag_config.AZURE_OPENAI_CHAT_STREAMING,  # type: ignore
        **kwargs
    ):
        super().__init__(
            azure_deployment=azure_deployment,
            api_version=openai_api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            model_name=model_name,  # type: ignore
            temperature=temperature,
            streaming=streaming,
            **kwargs
        )
