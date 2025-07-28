from langchain.memory import ConversationSummaryBufferMemory

from app.core.config import herbalista_config
from app.core.services.azure_services.az_openai_svc.chat import HerbalistaChatLLM
from app.core.chainlit.user_session import herbalista_cl_user_session
from .prompt_template import HerbalistaChatPromptTemplate
class HerbalistaChatMemory(ConversationSummaryBufferMemory):
    """
    Custom chat memory class that extends ConversationSummaryBufferMemory.
    This class is used to manage the chat history and context in a conversational AI application.
    """
    def __init__(self, 
                 memory_key=HerbalistaChatPromptTemplate.CHAT_HISTORY_KEY,
                 llm=HerbalistaChatLLM(),
                 max_token_limit=herbalista_config.AZURE_OPENAI_CHAT_MAX_TOKENS,
                 return_messages=True,
                 **kwargs):
        super().__init__(llm=llm,
                         max_token_limit=max_token_limit,
                         memory_key=memory_key,
                         return_messages=return_messages,
                         **kwargs)
