import chainlit as cl
from app.core.chainlit.user_session import simple_rag_cl_user_session
from chainlit.types import ThreadDict

from ..chat.tool_agent_w_memory.tool_agent import setup_runnable


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """
    This function is triggered when the chat application is resumed after being paused.
    It initializes the ConversationSummaryBufferMemory with the history from the previous session.
    """
    simple_rag_cl_user_session.current_thread = thread["id"]
    simple_rag_cl_user_session.chat_has_uploaded_files = any(step["name"] == "file_loader" for step in thread["steps"])  # type: ignore

    agent = await setup_runnable()

    # Retrieve the root messages from the thread
    root_messages = [m for m in thread["steps"] if m["parentId"] is None]  # type: ignore
    # Iterate over the root messages
    for message in root_messages:
        # Check the type of the message
        if message["type"] == "USER_MESSAGE":  # type: ignore
            # Add user message to the chat memory
            agent.memory.chat_memory.add_user_message(message["output"])  # type: ignore
        else:
            # Add AI message to the chat memory
            agent.memory.chat_memory.add_ai_message(message["output"])  # type: ignore
