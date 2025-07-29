from app.core.chainlit.user_session import simple_rag_cl_user_session
from app.core.config import simple_rag_config
from app.core.services.azure_services.az_openai_svc.chat import SimpleRagChatLLM
from langchain.memory import ConversationSummaryBufferMemory

from .simple_rag_prompt_template import SimpleRagChatPromptTemplate


class SimpleRagChatMemory(ConversationSummaryBufferMemory):
    """
    Custom chat memory class that extends ConversationSummaryBufferMemory.
    This class is used to manage the chat history and context in a conversational AI application.
    """

    def __init__(
        self,
        memory_key=SimpleRagChatPromptTemplate.CHAT_HISTORY_KEY,
        llm=SimpleRagChatLLM(),
        max_token_limit=simple_rag_config.AZURE_OPENAI_CHAT_MAX_TOKENS,
        return_messages=True,
        **kwargs
    ):
        super().__init__(
            llm=llm,
            max_token_limit=max_token_limit,
            memory_key=memory_key,
            return_messages=return_messages,
            **kwargs
        )
