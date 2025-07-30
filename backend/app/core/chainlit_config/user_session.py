# pydantic interface with simple rag app specific session variables and methods to the cl.user_session
from typing import Any, Dict, Optional, Union

import chainlit as cl
from chainlit.user_session import UserSession
from langchain.agents import AgentExecutor
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field


class SimpleRagCLUserSession:
    CL_SEESSION_LLM_KEY = "cl_session_llm"
    CL_SESSION_CHAT_MEMORY_KEY = "cl_session_chat_memory"
    CL_SESSION_CHAT_HISTORY_KEY = "cl_session_chat_history"
    CL_SESSION_CHAT_PROFILE_KEY = "cl_session_chat_profile"
    CL_SESSION_EMBEDDINGS_KEY = "cl_session_embeddings"
    CL_SESSION_CHAT_HAS_UPLOADED_FILES_KEY = "chat_has_uploaded_files"
    CL_SESSION_AGENT_EXECUTOR_KEY = "agent_executor"
    CL_SESSSION_CURRENT_THREAD_KEY = "current_thread"
    CL_SESSSION_CURRENT_USER_KEY = "user"

    def __init__(self):
        self._session: UserSession = cl.user_session

    @property
    def llm(self) -> Union[AzureChatOpenAI, None]:
        """
        Get the LLM instance from the session.
        """
        return self._session.get(self.CL_SEESSION_LLM_KEY, None)

    @llm.setter
    def llm(self, value: AzureChatOpenAI):
        """
        Set the LLM instance in the session.
        """
        self._session.set(self.CL_SEESSION_LLM_KEY, value)

    # cl.user_session.set("uploaded_files", True)
    @property
    def chat_has_uploaded_files(self) -> bool:
        """
        Get the uploaded files status from the session.
        """
        return self._session.get(self.CL_SESSION_CHAT_HAS_UPLOADED_FILES_KEY) in [
            True,
            "True",
            "true",
            1,
            "1",
        ]

    @chat_has_uploaded_files.setter
    def chat_has_uploaded_files(self, value: bool):
        """
        Set the uploaded files status in the session.
        """
        self._session.set(self.CL_SESSION_CHAT_HAS_UPLOADED_FILES_KEY, value)

    @property
    def agent_executor(self) -> Optional[AgentExecutor]:
        """
        Get the agent executor from the session.
        """
        return self._session.get(self.CL_SESSION_AGENT_EXECUTOR_KEY, None)

    @agent_executor.setter
    def agent_executor(self, value: AgentExecutor):
        """
        Set the agent executor in the session.
        """
        self._session.set(self.CL_SESSION_AGENT_EXECUTOR_KEY, value)

    @property
    def current_thread(self) -> Optional[str]:
        """
        Get the current thread ID from the session.
        """
        return self._session.get(self.CL_SESSSION_CURRENT_THREAD_KEY, None)

    @current_thread.setter
    def current_thread(self, value: str):
        """
        Set the current thread ID in the session.
        """
        self._session.set(self.CL_SESSSION_CURRENT_THREAD_KEY, value)

    @property
    def current_user(self) -> Optional[str]:
        """
        Get the current user ID from the session.
        """
        user = self._session.get(self.CL_SESSSION_CURRENT_USER_KEY, None)
        if user and hasattr(user, "identifier"):
            return user.identifier
        return str(user) if user else "anonymous"

    @current_user.setter
    def current_user(self, value: str):
        """
        Set the current user ID in the session.
        """
        self._session.set(self.CL_SESSSION_CURRENT_USER_KEY, value)

    # @property
    # def chat_memory(self) -> Optional[Any]:
    #     """
    #     Get the chat memory from the session.
    #     """
    #     res = self._session.get(self.CL_SESSION_CHAT_MEMORY_KEY, None)
    #     if res is None or not isinstance(res, Herbalista):
    #         # If LLM is not set, create a new instance
    #         res = HerbalistaChatLLM()
    #         self.llm = res
    #     return res
    #     return self._session.get(self.CL_SESSION_CHAT_MEMORY_KEY)

    # @chat_memory.setter
    # def chat_memory(self, value: Any):
    #     """
    #     Set the chat memory in the session.
    #     """
    #     self._session[self.CL_SESSION_CHAT_MEMORY_KEY] = value

    # @property
    # def chat_history(self) -> Optional[Dict[str, BaseMessage]]:
    #     """
    #     Get the chat history from the session.
    #     """
    #     return self._session.get(self.CL_SESSION_CHAT_HISTORY_KEY, {})

    # @chat_history.setter
    # def chat_history(self, value: Dict[str, BaseMessage]):
    #     """
    #     Set the chat history in the session.
    #     """
    #     self._session[self.CL_SESSION_CHAT_HISTORY_KEY] = value


simple_rag_cl_user_session = SimpleRagCLUserSession()
