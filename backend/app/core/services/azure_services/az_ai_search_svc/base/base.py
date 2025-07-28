from app.core.config import herbalista_config
from langchain_community.vectorstores.azuresearch import AzureSearch

class BaseHerbalistaAzureSearch(AzureSearch):
        
    def __init__(self, index_name: str,
                 embeddings,
                 azure_search_service_endpoint: str = herbalista_config.AZURE_SEARCH_SERVICE_ENDPOINT,  # type: ignore
                 azure_search_api_key: str = herbalista_config.AZURE_SEARCH_API_KEY, 
                 ):
        self.index_name = index_name
        self.azure_search_service_endpoint = azure_search_service_endpoint
        self._embeddings = embeddings # type: ignore
        self.embedding_dimensions = len(self._embeddings.embed_query("Text"))
        self.index_fields = self.configure_index_fields(self.embedding_dimensions)

        super().__init__(
            azure_search_endpoint=azure_search_service_endpoint,  # type: ignore
            azure_search_key=azure_search_api_key,
            index_name=index_name,
            embedding_function=embeddings.embed_query,
            embedding_dimensions=self.embedding_dimensions,
            fields=self.index_fields
        )


    def index_exists(self) -> bool:
        """Check if the RAG index exists."""
        # Ping by calling a safe method
        try:
            _ = self.similarity_search(
                query="",  # no embedding matching
                k=1,
                filter="user_id eq 'definitely_not_existing_user'"
            )
            return True
        except Exception as e:
            print("Search index ping failed:", e)
            return False

    # to override the create_index method in subclasses
    def configure_index_fields(self, embedding_dimensions: int):
        """Create the RAG index with the specified fields if it does not exist."""
        raise NotImplementedError("Subclasses should implement this method.")
