from app.core.config import herbalista_config
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from app.core.lib.singleton_per_signature import singleton_per_signature

@singleton_per_signature
class HerbalistaAzureOpenAIEmbeddings(AzureOpenAIEmbeddings):
    """
    Singleton class for Azure OpenAI embeddings.
    This class is used to create embeddings using Azure OpenAI service.
    """

    def __init__(self,
                 azure_deployment=herbalista_config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME,
                 api_version=herbalista_config.AZURE_OPENAI_API_VERSION,  # type: ignore
                 azure_endpoint=herbalista_config.AZURE_OPENAI_ENDPOINT,
                 api_key=herbalista_config.AZURE_OPENAI_API_KEY,
                 model=herbalista_config.AZURE_OPENAI_EMBEDDINGS_MODEL_NAME,  # type: ignore
                 **kwargs):
        """
        Initialize the Azure OpenAI embeddings with the configuration from herbalista_config.
        """
        super().__init__( azure_deployment=azure_deployment,
                         api_version=api_version,
                         azure_endpoint=azure_endpoint,
                         api_key=api_key,  # type: ignore
                         model=model,
                         **kwargs)
