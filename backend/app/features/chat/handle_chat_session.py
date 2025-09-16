from typing import List, Optional, Union

import chainlit as cl
from app.core.chainlit_config.register_data_layer import init_data_layer
from app.core.chainlit_config.user_session import simple_rag_cl_user_session
from app.core.config import simple_rag_config
from app.core.services.azure_services.az_openai_svc.chat import SimpleRagChatLLM
from app.features.chat.tool_agent_w_memory.chat_memory import SimpleRagChatMemory
from app.features.chat_file_upload.file_upload_handler import file_loader
from app.core.monitoring import get_pg_monitor, start_health_monitoring
from langchain.memory import ConversationSummaryBufferMemory
import logging

from .chat_response_stream_handler import StreamHandler
from .tool_agent_w_memory.tool_agent import SimpleRagToolAgent, setup_runnable

logger = logging.getLogger(__name__)


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
async def on_chat_start():
    logger.info("Chat session started")

    # Debug: Check user and authentication context
    try:
        current_user = cl.context.session.user
        logger.info(f"Current user: {current_user}")
        logger.info(f"User identifier: {current_user.identifier if current_user else 'None'}")
        logger.info(f"Data layer: {cl.context.session.client_type}")
    except Exception as e:
        logger.warning(f"Could not get user context: {e}")

    # Initialize the agent executor for this session
    try:
        from .tool_agent_w_memory.tool_agent import setup_runnable
        agent_executor = await setup_runnable()
        logger.info("Agent executor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent executor: {e}")
        # Continue with the session even if agent setup fails

    # Safe connection monitoring (non-blocking)
    try:
        monitor = get_pg_monitor()
        if monitor:
            # Just log monitoring availability, don't perform async operations
            logger.info("Connection monitoring available for this session")
    except Exception as e:
        # Don't fail the session if monitoring isn't available
        logger.warning(f"Connection monitoring not available: {e}")

@cl.on_message
async def handle_message(message: cl.Message):
    """
    Handler for the main message event.
    This function is the main entry point for processing user messages in the chat application.
    It handles both regular messages and file uploads.
    """
    simple_rag_cl_user_session.current_thread = message.thread_id

    # Monitor connections before processing (non-blocking, ignore errors)
    monitor = get_pg_monitor()
    stats_before = None
    if monitor:
        try:
            stats_before = await monitor.get_connection_stats()
        except Exception as e:
            logger.debug(f"Could not get connection stats before message processing: {e}")

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

    # Check for connection leaks after processing (non-blocking, ignore errors)
    if monitor and stats_before:
        try:
            stats_after = await monitor.get_connection_stats()

            # Only check if both stats are healthy
            if (stats_before.get('status') == 'healthy' and
                stats_after.get('status') == 'healthy'):

                before_active = stats_before.get('database_stats', {}).get('active_connections', 0)
                after_active = stats_after.get('database_stats', {}).get('active_connections', 0)

                if isinstance(before_active, int) and isinstance(after_active, int):
                    if after_active > before_active + 1:  # Allow for some variance
                        logger.info(f"Connection count increased from {before_active} to {after_active} during message processing")

        except Exception as e:
            logger.debug(f"Could not check connections after message processing: {e}")


@cl.on_chat_end
async def on_chat_end():
    """
    This function is called when a chat ends.
    It sets the current_thread value in the user session to None.
    """
    cl.user_session.set("current_thread", None)
