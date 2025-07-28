
import mimetypes

import chainlit as cl
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from app.core.config import herbalista_config
from app.core.chainlit.user_session import herbalista_cl_user_session
from app.core.services.azure_services.az_ai_search_svc.chat_file_upload_index import ChatFileUploadIndex
from app.features.chat_file_upload.uploaded_files_search_agent_tool import file_question_answering_tool
from ..chat.tool_agent_w_memory.tool_agent import setup_runnable
from app.core.services.azure_services.az_ai_search_svc import chat_file_upload_index_field_names as file_rag_fields

# Add all supported mimetypes so the app functions on app services
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"
)
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"
)
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"
)
mimetypes.add_type("text/plain", ".txt")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/bmp", ".bmp")
mimetypes.add_type("image/tiff", ".tiff")
mimetypes.add_type("image/heif", ".heif")
mimetypes.add_type("text/html", ".html")


text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4o",
    chunk_size=5000,
    chunk_overlap=500,
)


# Function to handle file loading
@cl.step(type="tool")
async def file_loader(message: cl.Message):
    """
    This function processes the files uploaded by the user for further use by the chat application.
    The processed documents are then added to the conversation memory or a vector store
    and then splits the content into manageable chunks using a text splitter.
    It uses the Azure AI Document Intelligence service to extract content from the files.
    """

    documents = []
    for element in message.elements:
        loader = AzureAIDocumentIntelligenceLoader(
            api_endpoint=herbalista_config.DOCUMENT_INTELLIGENCE_ENDPOINT, # type: ignore
            api_key=herbalista_config.DOCUMENT_INTELLIGENCE_API_KEY,
            file_path=element.path,
            api_model="prebuilt-layout",
            mode="markdown",
        )

        docs = await cl.make_async(loader.load)()

        split_docs = await text_splitter.atransform_documents(docs)

        for doc in split_docs:
            doc.metadata[file_rag_fields.FIELD_NAME_THREAD_ID] = message.thread_id
            doc.metadata[file_rag_fields.FIELD_NAME_USER_ID] = herbalista_cl_user_session.current_user.id # type: ignore
            doc.metadata[file_rag_fields.FIELD_NAME_TITLE] = element.name
            documents.append(doc)

    # If there is only a single document or chunk, directly insert that chunk into the chat history. The tool to search in uploaded files has a description that tells it to not use this tool if the information it needs is already present in the context. ChatGPT also uses this strategy.
    if len(documents) == 1:
        single_doc = documents[0]

        herbalista_cl_user_session.agent_executor.memory.chat_memory.add_ai_message(  # type: ignore
            f"context: page_content={single_doc.page_content}, "
            f"title={single_doc.metadata.get(file_rag_fields.FIELD_NAME_TITLE, None)}"
        )

        if file_question_answering_tool not in herbalista_cl_user_session.agent_executor.tools:  # type: ignore
            herbalista_cl_user_session.agent_executor.tools.append(  # type: ignore
                file_question_answering_tool )
    else:
        await ChatFileUploadIndex().aadd_documents(documents)

    herbalista_cl_user_session.chat_has_uploaded_files = True

    await setup_runnable(herbalista_cl_user_session.agent_executor.memory) # type: ignore
    await cl.Message(
        author="System",
        content="Done reading and memorizing files.",
    ).send()

