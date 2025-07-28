from app.core.config import herbalista_config
from .base import BaseHerbalistaAzureSearch
from ...az_openai_svc.embeddings import AzureOpenAIEmbeddings, HerbalistaAzureOpenAIEmbeddings
from . import base_file_index_field_names as field_names
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)


class BaseFileIndex(BaseHerbalistaAzureSearch):
        
    def __init__(self, 
                 index_name: str,
                 embeddings: HerbalistaAzureOpenAIEmbeddings):
        super().__init__(
            index_name=index_name,
            embeddings=embeddings
        )

    
        
    def get_base_index_fields(self, 
                                embedding_dimensions: int,
                                metadata: bool = True,
                                title: bool = True,
                                uri: bool = True,
                                filename: bool = True,
                                file_type: bool = True,
                                file_size: bool = True,
                                last_modified: bool = True,
                                file_hash: bool = True,
                                file_topic: bool = True,
                                file_language: bool = True,
                                chunk_topic1: bool = True,
                                chunk_topic2: bool = True,
                                chunk_topic3: bool = True,
                                chunk_in_file_ctx_summary: bool = True,
                                chunk_question1: bool = True,
                                chunk_question2: bool = True,
                                chunk_question3: bool = True                                
                              )-> list:
        """Create the RAG index with the specified fields if it does not exist."""
        # Define fields for file based RAG index
        index_fields = [
            SimpleField(
                name=field_names.FIELD_NAME_ID, type=SearchFieldDataType.String, key=True, filterable=True
            ),
            SearchableField(
                name=field_names.FIELD_NAME_CONTENT, type=SearchFieldDataType.String, searchable=True
            ),
            SearchField(
                name=field_names.FIELD_NAME_CONTENT_VECTOR,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=embedding_dimensions,
                vector_search_profile_name="myHnswProfile",
            )
        ]

        if metadata:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_METADATA, 
                    type=SearchFieldDataType.String, searchable=True
                )
            )

        if title:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_TITLE,
                    type=SearchFieldDataType.String, searchable=True
                )
            )

        if uri:
            index_fields.append(
                SimpleField(
                    name=field_names.FIELD_NAME_URI,
                    type=SearchFieldDataType.String,
                    filterable=True,
                    searchable=True,
                )
            )

        if filename:
            index_fields.append(
                SimpleField(
                    name=field_names.FIELD_NAME_FILE_NAME,
                    type=SearchFieldDataType.String,
                    filterable=True,
                    searchable=True,
                )
            )
        if file_type:
            index_fields.append(
                SimpleField(
                    name=field_names.FIELD_NAME_FILE_TYPE,
                    type=SearchFieldDataType.String,
                    filterable=True,
                    searchable=True,
                )
            )
        if file_size:
            index_fields.append(
                SimpleField(
                    name=field_names.FIELD_NAME_FILE_SIZE,
                    type=SearchFieldDataType.Int64,
                    filterable=True,
                )
            )
        if last_modified:
            index_fields.append(
                SimpleField(
                    name=field_names.FIELD_NAME_LAST_MODIFIED,
                    type=SearchFieldDataType.DateTimeOffset,
                    filterable=True,
                )
            )

        if file_hash:
            index_fields.append(
                SimpleField(
                    name=field_names.FIELD_NAME_FILE_HASH,
                    type=SearchFieldDataType.String,
                    filterable=True,
                    searchable=True,
                )
            )
        if file_topic:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_FILE_TOPIC,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_FILE_TOPIC_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )

        if file_language:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_FILE_LANGUAGE,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

        if chunk_topic1:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_TOPIC1,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_CHUNK_TOPIC3_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )

        if chunk_topic2:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_TOPIC2,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_CHUNK_TOPIC2_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )


        if chunk_topic3:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_TOPIC3,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_FILE_TOPIC_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )


        if chunk_in_file_ctx_summary:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_IN_FILE_CTX_SUMMARY,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_CHUNK_IN_FILE_CTX_SUMMARY_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )
        


        if chunk_question1:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_QUESTION1,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_CHUNK_QUESTION1_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )

        if chunk_question2:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_QUESTION2,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_CHUNK_QUESTION2_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )

        if chunk_question3:
            index_fields.append(
                SearchableField(
                    name=field_names.FIELD_NAME_CHUNK_QUESTION3,
                    type=SearchFieldDataType.String,
                    searchable=True,
                )
            )

            index_fields.append(
                SearchField(
                    name=field_names.FIELD_NAME_FILE_TOPIC_VECTOR,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embedding_dimensions,
                    vector_search_profile_name="myHnswProfile",
                )
            )


        return index_fields
