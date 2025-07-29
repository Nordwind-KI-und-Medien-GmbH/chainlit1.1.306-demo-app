import chainlit as cl
from app.core.chainlit.user_session import simple_rag_cl_user_session
from app.core.config import simple_rag_config
from app.core.services.azure_services.az_ai_search_svc import (
    chat_file_upload_index_field_names as file_rag_fields,
)
from app.core.services.azure_services.az_ai_search_svc.chat_file_upload_index import (
    ChatFileUploadIndex,
)
from app.core.services.azure_services.az_ai_search_svc.simple_rag_index import (
    SimpleRagIndex,
)
from langchain.tools import tool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(
        description="Gib eine präzise Suchanfrage an, um gezielt Informationen in den hochgeladenen Dateien zu finden. Vermeide allgemeine oder unklare Formulierungen."
    )


@tool("file_question_answering_tool", args_schema=SearchInput)
async def file_question_answering_tool(query: str) -> str:
    """
    This tool searches a vector database to find the most relevant chunks of information
    related to the user query uploaded during the current chat session. It retrieves only the key sections that directly address
    or relate to the question. Use this tool when query requires specific details or answers and files have been uploaded successfully in the current chat session
    """
    try:
        rag_index = ChatFileUploadIndex()
        result = await rag_index.asimilarity_search(
            query=query,
            k=5,
            search_type="hybrid",
            filters=f"{file_rag_fields.FIELD_NAME_USER_ID} eq '{simple_rag_cl_user_session.current_user or 'anonymous'}' and {file_rag_fields.FIELD_NAME_THREAD_ID} eq '{simple_rag_cl_user_session.current_thread}'",  # type: ignore
        )

        return [
            {
                "page_content": doc.page_content,
                "title": doc.metadata[file_rag_fields.FIELD_NAME_TITLE],
            }
            for doc in result
        ]  # type: ignore
    except Exception as e:
        print(f"Error in file search tool: {e}")
        return f"Error searching uploaded files: {str(e)}"
