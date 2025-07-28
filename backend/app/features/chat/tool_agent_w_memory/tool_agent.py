from collections.abc import Sequence
from typing import Optional, Union

from langchain.agents import AgentExecutor, create_tool_calling_agent, create_self_ask_with_search_agent
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from app.core.chainlit.user_session import herbalista_cl_user_session
from app.core.services.azure_services.az_openai_svc.chat import HerbalistaChatLLM
from ...chat_file_upload.uploaded_files_search_agent_tool import file_question_answering_tool
from ...rag_search.phyto_herbs_rag_search_tool import phyto_herbs_rag_search_tool
from .prompt_template import HerbalistaChatPromptTemplate
from .chat_memory import HerbalistaChatMemory

class HerbalistaToolAgent(AgentExecutor):
    def __init__(self, agent: Runnable, tools: Sequence[BaseTool], memory: HerbalistaChatMemory, max_iterations=5):
        """
        Initializes the HerbalistaToolAgent with the specified agent, tools, and memory.
        
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
            return_intermediate_steps=True
        )

    @staticmethod
    def create(memory: Optional[HerbalistaChatMemory] = None) -> "HerbalistaToolAgent":
        """Creates an agent executor with the specified agent, tools, and memory (static version)."""
        from app.core.chainlit.user_session import herbalista_cl_user_session

        prompt_template = HerbalistaChatPromptTemplate().get_prompt_template()
        tools = [phyto_herbs_rag_search_tool]

        if herbalista_cl_user_session.chat_has_uploaded_files is True:
            tools.append(file_question_answering_tool)

        agent = create_tool_calling_agent(HerbalistaChatLLM(), tools, prompt_template)

        if memory is None:
            # If no memory is provided, create a new HerbalistaChatMemory instance  
            _memory = HerbalistaChatMemory()
        else:
            _memory = memory

        return HerbalistaToolAgent(
            agent=agent, tools=tools, memory=_memory, max_iterations=5
        )

    def activate_file_upload_tool(self):
        """
        Activates the file upload tool in the agent.
        This method is used to ensure that the file upload tool is available for use in the agent.
        """
        if file_question_answering_tool not in self.tools:
            self.tools.append(file_question_answering_tool)  # type: ignore

async def setup_runnable(memory: Optional[HerbalistaChatMemory] = None) -> Union[HerbalistaToolAgent, None]:
    herbalista_cl_user_session.agent_executor = HerbalistaToolAgent.create(memory=memory)
    return herbalista_cl_user_session.agent_executor # type: ignore
