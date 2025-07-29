from app.core.config import simple_rag_config
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)

from ....lib.singleton_per_signature import singleton_per_signature
from ..az_openai_svc.embeddings import SimpleRagAzureOpenAIEmbeddings
from . import chat_file_upload_index_field_names as field_names
from .base.base_file_index import BaseFileIndex


@singleton_per_signature
class SimpleRagIndex(BaseFileIndex):
    def __init__(
        self,
        index_name: str = simple_rag_config.AZURE_SEARCH_DEMO_RAG_INDEX_NAME,  # type: ignore
        embeddings=SimpleRagAzureOpenAIEmbeddings(),
    ):
        super().__init__(index_name=index_name, embeddings=embeddings)

    def configure_index_fields(self, embedding_dimensions: int):
        """Create the RAG index with the specified fields if it does not exist."""
        # Define fields for user-upload index
        self.index_fields = self.get_base_index_fields(
            embedding_dimensions=embedding_dimensions,
            # TODO: remove bellow as soon as indexing code is implemented
            chunk_topic1=False,
            chunk_topic2=False,
            chunk_topic3=False,
            chunk_in_file_ctx_summary=False,
            chunk_question1=False,
            chunk_question2=False,
            chunk_question3=False,
            uri=False,
            filename=False,
            file_type=False,
            file_size=False,
            last_modified=False,
            file_hash=False,
            file_topic=False,
            file_language=False,
        )

        return self.index_fields
