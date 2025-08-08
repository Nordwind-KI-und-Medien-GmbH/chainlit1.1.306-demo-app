from typing import List, Optional, Union

import chainlit as cl
from app.core.chainlit_config.register_data_layer import init_data_layer
from app.core.chainlit_config.user_session import simple_rag_cl_user_session
from app.core.config import simple_rag_config
from app.core.services.azure_services.az_openai_svc.chat import SimpleRagChatLLM
from app.features.chat.tool_agent_w_memory.chat_memory import SimpleRagChatMemory
from app.features.chat_file_upload.file_upload_handler import file_loader
from langchain.memory import ConversationSummaryBufferMemory

from .chat_response_stream_handler import StreamHandler
from .tool_agent_w_memory.tool_agent import SimpleRagToolAgent, setup_runnable


def detect_external_client() -> bool:
    """Detect if the client is an external websocket client vs Chainlit UI"""
    try:
        client_type = cl.context.session.client_type
        return client_type == "python"
    except:
        return False


def extract_rag_chunks(intermediate_steps: List[tuple]) -> List[str]:
    """Extract RAG chunks from agent intermediate steps as strings"""
    rag_chunks = []
    for action, tool_result in intermediate_steps:
        if action.tool == "simple-rag-search-tool":
            if isinstance(tool_result, list):  # Success case
                for chunk in tool_result:
                    if isinstance(chunk, dict) and "page_content" in chunk:
                        rag_chunks.append(chunk["page_content"])
                    else:
                        rag_chunks.append(str(chunk))
    return rag_chunks


@cl.on_chat_start
async def start_chat():
    """
    Handle the start of a chat session.
    This function is triggered when a chat session starts.
    It initializes the session and prepares the context for the user.
    """
    # Initialize data layer when chat session starts
    init_data_layer()

    await setup_runnable()

    # Log the start of the chat session
    print("Chat session started.")


@cl.on_message
async def handle_message(message: cl.Message):
    """
    Handler for the main message event.
    This function is the main entry point for processing user messages in the chat application.
    It handles both regular messages and file uploads.
    """
    simple_rag_cl_user_session.current_thread = message.thread_id

    # If the message contains file elements, start the file loading process
    if message.elements:
        try:
            await file_loader(message)
            simple_rag_cl_user_session.agent_executor.memory.chat_memory.add_user_message(f"{len(message.elements)} files have been uploaded.")  # type: ignore
        except Exception:
            await cl.Message(
                author="System",
                content="An error occurred while reading the file. Please try again.",
            ).send()

    # Get the agent executor from the user session
    agent_executor: SimpleRagToolAgent = await setup_runnable(simple_rag_cl_user_session.agent_executor.memory)  # type: ignore

    # Detect client type to determine response format
    is_external_client = detect_external_client()

    # Invoke the agent with the user message as input
    try:
        if is_external_client:
            # External websocket client - return complete response with RAG metadata
            result = await agent_executor.ainvoke(
                {"input": message.content},
                {"callbacks": [cl.AsyncLangchainCallbackHandler()]},  # No streaming
            )

            # Extract RAG chunks from intermediate steps
            rag_chunks = extract_rag_chunks(result["intermediate_steps"])

            # Send complete response with metadata
            await cl.Message(
                content=result["output"],
                author="Assistant",
                metadata={"rag_chunks": rag_chunks} if rag_chunks else None,
            ).send()

        else:
            # Chainlit UI - keep existing streaming behavior
            await agent_executor.ainvoke(
                {"input": message.content},
                {"callbacks": [cl.AsyncLangchainCallbackHandler(), StreamHandler()]},
            )

    except Exception:
        await cl.Message(
            author="System",
            content="An error occurred while processing the message. Please try again.",
        ).send()


@cl.on_chat_end
async def on_chat_end():
    """
    This function is called when a chat ends.
    It sets the current_thread value in the user session to None.
    """
    cl.user_session.set("current_thread", None)
