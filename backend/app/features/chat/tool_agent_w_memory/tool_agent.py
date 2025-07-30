from collections.abc import Sequence
from typing import Optional, Union

from app.core.chainlit_config.user_session import simple_rag_cl_user_session
from app.core.services.azure_services.az_openai_svc.chat import SimpleRagChatLLM
from langchain.agents import (
    AgentExecutor,
    create_self_ask_with_search_agent,
    create_tool_calling_agent,
)
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from ...chat_file_upload.uploaded_files_search_agent_tool import (
    file_question_answering_tool,
)
from ...rag_search.rag_search_tool import simple_rag_search_tool
from .chat_memory import SimpleRagChatMemory
from .prompt_template import SimpleRagChatPromptTemplate


class SimpleRagToolAgent(AgentExecutor):
    def __init__(
        self,
        agent: Runnable,
        tools: Sequence[BaseTool],
        memory: SimpleRagChatMemory,
        max_iterations=5,
    ):
        """
        Initializes the SimpleRagToolAgent with the specified agent, tools, and memory.

        :param agent: The agent to be used for executing tasks.
        :param tools: A sequence of tools that the agent can use.
        :param memory: The chat memory to maintain conversation context.
        :param max_iterations: Maximum number of iterations for the agent execution.
        """
        super().__init__(
            agent=agent,
            tools=tools,
            memory=memory,
            max_iterations=max_iterations,
            verbose=True,
            return_intermediate_steps=True,
        )

    @staticmethod
    def create(memory: Optional[SimpleRagChatMemory] = None) -> "SimpleRagToolAgent":
        """Creates an agent executor with the specified agent, tools, and memory (static version)."""
        from app.core.chainlit_config.user_session import simple_rag_cl_user_session

        prompt_template = SimpleRagChatPromptTemplate().get_prompt_template()
        tools = [simple_rag_search_tool]

        if simple_rag_cl_user_session.chat_has_uploaded_files is True:
            tools.append(file_question_answering_tool)

        agent = create_tool_calling_agent(SimpleRagChatLLM(), tools, prompt_template)

        if memory is None:
            # If no memory is provided, create a new SimpleRagChatMemory instance
            _memory = SimpleRagChatMemory()
        else:
            _memory = memory

        return SimpleRagToolAgent(
            agent=agent, tools=tools, memory=_memory, max_iterations=5
        )

    def activate_file_upload_tool(self):
        """
        Activates the file upload tool in the agent.
        This method is used to ensure that the file upload tool is available for use in the agent.
        """
        if file_question_answering_tool not in self.tools:
            self.tools.append(file_question_answering_tool)  # type: ignore


async def setup_runnable(
    memory: Optional[SimpleRagChatMemory] = None,
) -> Union[SimpleRagToolAgent, None]:
    simple_rag_cl_user_session.agent_executor = SimpleRagToolAgent.create(memory=memory)
    return simple_rag_cl_user_session.agent_executor  # type: ignore
