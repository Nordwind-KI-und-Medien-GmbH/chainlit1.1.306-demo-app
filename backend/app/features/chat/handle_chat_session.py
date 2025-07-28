from typing import Optional, Union
from chainlit import chainlit as cl
from langchain.memory import ConversationSummaryBufferMemory

from app.core.config import herbalista_config
from app.core.services.azure_services.az_openai_svc.chat import HerbalistaChatLLM
from app.core.chainlit.user_session import herbalista_cl_user_session
from app.features.chat.tool_agent_w_memory.chat_memory import HerbalistaChatMemory
from .chat_response_stream_handler import StreamHandler
from app.features.chat_file_upload.file_upload_handler import file_loader
from .tool_agent_w_memory.tool_agent import HerbalistaToolAgent, setup_runnable

@cl.on_chat_start
async def start_chat():
    """
    Handle the start of a chat session.
    This function is triggered when a chat session starts.
    It initializes the session and prepares the context for the user.
    """
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
    herbalista_cl_user_session.current_thread = message.thread_id

    # If the message contains file elements, start the file loading process
    if message.elements:
        try:
            await file_loader(message)
            herbalista_cl_user_session.agent_executor.memory.chat_memory.add_user_message(f"Es wurden {len(message.elements)} Dateien hochgeladen.") # type: ignore
        except Exception as e:
            await cl.Message(
                author="System",
                content="An error occurred while reading the file. Please try again.",
            ).send()

    # Get the agent executor from the user session
    agent_executor: HerbalistaToolAgent = await setup_runnable(herbalista_cl_user_session.agent_executor.memory) # type: ignore
    #agent_executor: HITLChatAssistant = await setup_runnable(herbalista_cl_user_session.agent_executor.memory) # type: ignore


    # Invoke the agent with the user message as input
    try:
        await agent_executor.ainvoke(
            {"input": message.content},
            {"callbacks": [cl.AsyncLangchainCallbackHandler(), StreamHandler()]},
        )
    except Exception as e:
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
