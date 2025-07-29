from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .simple_rag_system_prompt import system_prompt


class SimpleRagChatPromptTemplate:
    USER_INPUT_KEY = "input"
    CHAT_HISTORY_KEY = "chat_history"
    AGENT_SCRATCHPAD_KEY = "agent_scratchpad"

    def __init__(
        self,
        user_input_key: str = USER_INPUT_KEY,
        chat_history_key: str = CHAT_HISTORY_KEY,
        agent_scratchpad_key: str = AGENT_SCRATCHPAD_KEY,
    ):
        self.system_prompt = system_prompt
        self.user_input_key = user_input_key
        self.chat_history_key = chat_history_key
        self.agent_scratchpad_key = agent_scratchpad_key

    def get_prompt_template(self):
        """Returns the chat prompt template."""
        return self._create_prompt_template(self.system_prompt)

    def _create_prompt_template(self, system_prompt: str):
        """Creates a chat prompt template with the given system prompt."""
        self.system_prompt = system_prompt
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name=self.chat_history_key),
                ("user", "{" + self.user_input_key + "}"),
                MessagesPlaceholder(variable_name=self.agent_scratchpad_key),
            ]
        )
