# add curret path to sys.path
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(Path(os.path.abspath(__file__)).parent))
print(f"sys.path: {sys.path}")

# Import necessary modules and packages
from chainlit import chainlit as cl
from core.config import herbalista_config
from core.chainlit.user_session import herbalista_cl_user_session
from core.monitoring import register_phoenix_tracer
from features import user_auth
from features import thread_history

from features.chat import handle_chat_session
from app.features.chat_file_upload import file_upload_handler
from features.thread_history import resume_chat


if __name__ == "__main__":
    # This is a debug script to test the chainlit application
    # It will run the chainlit app with the specified parameters
    from chainlit import chainlit as cl
    from chainlit.cli import run_chainlit
    # from chainlit.config import config
    # config.run.watch = True  # Enable live reload for development

    run_chainlit(__file__)



# from datetime import datetime
# import os
# from typing import Dict, Optional


# from . import (
#     DOCUMENT_INTELLIGENCE_ENDPOINT,
#     DOCUMENT_INTELLIGENCE_API_KEY,
# )


# from chainlit.types import ThreadDict
# import chainlit as cl


# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain.memory import ConversationSummaryBufferMemory
# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.callbacks.base import BaseCallbackHandler
# from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from app.features.rag_search.phyto_herbs_rag_search_tool import rag_search
# #from tools.web_search import web_search
# from src.app.features.chat_file_upload.uploaded_files_search_agent_tool import uploaded_files_search_tool

# from core.services.azure_services.az_ai_search_svc.chat_file_upload_index import ChatFileUploadIndex
# from core.services.azure_services.az_ai_search_svc.phyto_herbs_index import PhytoHerbsIndex
# from core.services.azure_services.az_openai_svc.chat import llm
# from core.services.azure_services.az_openai_svc.embeddings import embeddings


# # Callback handler for handling streaming responses from the language model
# class StreamHandler(BaseCallbackHandler):
#     """
#     A callback handler for handling streaming responses from the language model.

#     Attributes:
#         msg (cl.Message): The message object used for streaming the response.

#     Methods:
#         on_llm_new_token: Called when a new token is received from the language model.
#         on_llm_end: Called when the streaming response from the language model ends.
#     """

#     def __init__(self):
#         self.msg = None

#     async def on_llm_new_token(self, token: str, **kwargs):
#         if not token:
#             return

#         if self.msg is None:
#             self.msg = cl.Message(content="", author="Assistant")

#         await self.msg.stream_token(token)

#     async def on_llm_end(self, response: str, **kwargs):  # type: ignore
#         if self.msg:
#             await self.msg.send()
#         self.msg = None


# # Function to setup the runnable environment for the chat application
# async def setup_runnable(memory: ConversationSummaryBufferMemory):
#     """
#     Sets up the runnable environment for the chat application.
#     """

#     # Create the prompt for the agent

#     # Add knowledge of current date to the prompt
#     system_prompt = (
#         """Du bist ein KI-Assistent der als Heilpraktiker- und Phytotherapie Experte, deine Benutzer,die meist ihrerseits Phytotherapeuten sind, bei der Betreuung ihrer Patienten hilfst.
# Du bietest:

# 1. **Fallbesprechungen:** Unterstützung bei der Analyse von Patientenfällen unter Berücksichtigung individueller Bedürfnisse und Konstitutionen.

# 2. **Pflanzenwissen:** Fundierte Informationen über Heilpflanzen, ihre Eigenschaften, Wirkstoffe und Anwendungsmöglichkeiten.

# 3. **Beratung bei Therapien:** Unterstützung bei der Auswahl geeigneter Heilpflanzen für spezifische gesundheitliche Probleme, basierend auf aktuellen wissenschaftlichen Erkenntnissen und traditionellen Anwendungen.

# 4. **Sicherheitshinweise:** Hinweise zu möglichen Wechselwirkungen, Kontraindikationen und Dosierungen, um die Sicherheit und Wirksamkeit der pflanzlichen Heilmittel zu gewährleisten.

# 5. **Aktuelle Forschung:** Informationen über neueste Entwicklungen und Studien in der Phytotherapie.

# Dir stehen folgende Werkzeuge zur Verfügung:
# 1. **RAG-Suche:** dir stehen verschiedene RAG-Datenbanken zur Verfügung, die du nutzen kannst, um relevante Informationen zu finden. Dazu gehören:
# - **Differenzialdiagnose RAG Index:** Vorgehen und Verfahren zur Anamnese, Differentialdiagnosen, Diagnostische strategien, und klassifikation von Krnakheiten.
# - **Pflanzen RAG Index:**  Pflanzen mit ihren Wirkstoffe und Anwendungsbereiche und Methode.
# - **Studien RAG Index:** Studien zu den Wirkstoffen der Pflanzen und deren Anwendungsbereiche.
# 2. **Web-Suche:** Suche im Internet, um aktuelle Informationen zu finden, die nicht in der Wissensdatenbank enthalten sind.
# 3. **Hochgeladene Dateien:** Suche in den hochgeladenen Dateien, um relevante Informationen zu finden.
# Du solltest die Werkzeuge nur dann verwenden, wenn du die benötigten Informationen nicht bereits im Kontext hast.

# Vorgehensweise:
# 1. **Welche Hilfe benötigt der Phytoterapeut im aktuellen Kontext:** Gehe schritweise vor um zu verstehen in welcher phase der Patientenbetreuung sich der Benutzer befindet um zu bestimmen was der Phytoterapeut jetzt braucht oder wissen muss um seinem Patienten weiter zu helfen.
# 1.a **Initiale Anamnese:** Wenn der Benutzer initiale Informationen über den Patienten bereitstellt, was meist die basis informationen zum patienten enthält und meist etw. umfangreicher ist, beginne mit der Anamnese.
#     - Stelle gezielte Fragen, um fehlende relevante Informationen zu sammeln.
#     - Basierend auf die erhaltenen spezifischen Anamnese informationen, identifiziere mögliche Diagnosen, und empfehle tiefergehende Fragen um diese Auszuschließen oder zu bestätigen.
#     - Wenn die erhaltenen Anamnese informationen ausreichen um eine eindeutige Diagnose zu stellen, beende die Fragerei und erstelle den Ausgefüllten Anamnese Formular mit einer anschließenden Zusammenfassung.
#     - sobald die basis informationen zum Patienten und eine grundlegende Beschreibung der Symptome vorliegen, und ergänzende Anamnese Fragen sinn machen, beschränke diese auf maximal 3 Folgefragen.
#     - Insgesammt sollte die Anamnese nicht länger als 10 Fragen dauern, um den Benutzer nicht zu überfordern und die Effizienz zu gewährleisten.
# 1.a.b **Anamnese ergänzen:** Wenn der Benutzer bereits eine Anamnese durchgeführt hat aber weitere Anamnese relevante Informationen bereitstellt, nutze diese Informationen, um die Anamnese zu ergänzen und die Diagnose zu verfeinern.
# 1.a.c **Anamnese abschließen:** Wenn der Benutzer die Anamnese abgeschlossen hat, fasse die gesammelten Informationen zusammen und stelle sicher, dass alle relevanten Details erfasst wurden.
# 1.a.d **Anamnese Formular:** Wenn der Benutzer ein Anamnese Formular benötigt, erstelle ein strukturiertes Anamnese Formular basierend auf den gesammelten Informationen und stelle es dem Benutzer zur Verfügung.
# 1.b **Differentialdiagnose:** Wenn der Benutzer eine Differentialdiagnose benötigt, nutze die RAG-Suche, um relevante Informationen zu finden und dem Benutzer bei der Analyse des Falls zu helfen.
#   - falls die Anamnese nicht vorliegt, leite den Benutzer durch die Initiale Anamnese, um die benötigten Informationen zu sammeln.
#   - Stelle gezielte Fragen, um die Symptome und den Gesundheitszustand des Patienten besser zu verstehen.
#   - Nutze die RAG-Suche, um Informationen über mögliche Differentialdiagnosen zu finden, die auf den Symptomen des Patienten basieren.
#   - Führe eine Analyse der Symptome durch, um die wahrscheinlichsten Differentialdiagnosen zu identifizieren.
#   - Empfehle dem Benutzer, weitere Tests oder Untersuchungen durchzuführen, um die Differentialdiagnose zu bestätigen oder auszuschließen.
#   - Fasse die Ergebnisse der Differentialdiagnose zusammen und stelle dem Benutzer eine klare Übersicht der möglichen Diagnosen zur Verfügung.
#   - Stelle sicher, dass der Benutzer versteht, welche Schritte als nächstes unternommen werden sollten, um die endgültige Diagnose zu stellen.
# 1.c **Therapieempfehlung:** Wenn der Benutzer eine Therapieempfehlung benötigt, nutze die RAG-Suche, um geeignete Heilpflanzen und deren Wirkstoffe zu finden, die auf die individuellen Bedürfnisse des Patienten abgestimmt sind.
#   - falls die Anamnese nicht vorliegt, leite den Benutzer durch die Initiale Anamnese, um die benötigten Informationen zu sammeln.
#   - falls die Diagnose nicht vorliegt, leite den Benutzer durch die Diagnose, um die benötigten Informationen zu sammeln.
#   - Nutze die Anamnese und Diagnose Informationen um geeignete Heilpflanzen zu identifizieren.
#     - Nutze die RAG-Suche, um Informationen über die Wirkstoffe der identifizierten Heilpflanzen zu finden und deren Anwendungsbereiche zu verstehen.
#     - Empfehle dem Benutzer, die identifizierten Heilpflanzen in die Therapie einzubeziehen, und erkläre deren Wirkungsweise.
#     - Stelle sicher, dass der Benutzer versteht, wie die empfohlenen Heilpflanzen in die Therapie integriert werden können.
#     - Fasse die Therapieempfehlungen zusammen und stelle dem Benutzer eine klare Übersicht der empfohlenen Heilpflanzen und deren Wirkstoffe zur Verfügung.
#     - Stelle sicher, dass der Benutzer versteht, welche Schritte als nächstes unternommen werden sollten, um die Therapie zu beginnen.
# 1.d **Sicherheitshinweise:** Wenn die Anamnese, Diagnose oder Therapieplan kritische Sachverhalte enthält bei der ein Gesetzlich vorgeschriebenes Vorgehen nach dem Heilpraktikergesetz, dann weise den Benutzer darauf hin.
# 2 **Aktuelle Forschung:** Wenn der Benutzer Informationen über aktuelle Forschungsergebnisse benötigt, nutze den **Studien RAG Index** und die Web-Suche, um relevante Studien und Entwicklungen in der Phytotherapie zu finden.
# 3. **Hochgeladene Dateien:** Wenn der Benutzer Dateien hochlädt, die für die aktuelle Konversation relevant sind, suche in diesen Dateien nach Informationen, die dem Benutzer bei der Beantwortung seiner Fragen helfen können.

# Heute ist Montag der"""
#         + datetime.now().date().strftime("%A, %Y-%m-%d")
#     )

#     # Create the chat prompt template, the ordering of the placeholders is important, taken from: https://smith.langchain.com/hub/hwchase17/openai-tools-agent
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", system_prompt),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{input}"),
#             MessagesPlaceholder(variable_name="agent_scratchpad"),
#         ]
#     )

#     agent_tools = [rag_search]#, web_search]

#     if cl.user_session.get("uploaded_files") is True:
#         agent_tools.append(uploaded_files_search_tool)

#     # Create the OpenAI Tools agent using the specified model, tools, and prompt
#     agent = create_tool_calling_agent(azure_services.model, agent_tools, prompt)

#     # Create an agent executor by passing in the agent and tools
#     agent_executor = AgentExecutor(
#         agent=agent, tools=agent_tools, memory=memory, max_iterations=5
#     )

#     # Set the agent executor in the user session
#     cl.user_session.set("agent_executor", agent_executor)


# # Handler for the main chat start event
# @cl.on_chat_start
# async def start_chat():
#     """
#     Handler for the main chat start event.
#     """
#     # On chat start there is no thread, threads are created after first message is sent.
#     # cl.user_session.set("current_thread", None)
#     cl.user_session.set("uploaded_files", False)
#     cl.user_session.set("llm", llm)
#     cl.user_session.set("embeddings", embeddings)
#     cl.user_session.set("chat_file_upload_index", ChatFileUploadIndex())
#     cl.user_session.set("phyto_herbs_index", PhytoHerbsIndex())



# # Handler for the main message event
# @cl.on_message
# async def chat(message: cl.Message):
#     """
#     Handler for the main message event.
#     This function is the main entry point for processing user messages in the chat application.
#     It handles both regular messages and file uploads.
#     """
#     cl.user_session.set("current_thread", message.thread_id)
#     # If the message contains file elements, start the file loading process
#     if message.elements:
#         try:
#             await file_loader(message)
#         except Exception as e:
#             await cl.Message(
#                 author="System",
#                 content="An error occurred while reading the file. Please try again.",
#             ).send()

#     # Get the agent executor from the user session
#     agent_executor: AgentExecutor = cl.user_session.get("agent_executor") # type: ignore

#     # Invoke the agent with the user message as input
#     try:
#         await agent_executor.ainvoke(
#             {"input": message.content},
#             {"callbacks": [cl.AsyncLangchainCallbackHandler(), StreamHandler()]},
#         )
#     except Exception as e:
#         await cl.Message(
#             author="System",
#             content="An error occurred while processing the message. Please try again.",
#         ).send()


# @cl.on_chat_resume
# async def on_chat_resume(thread: ThreadDict):
#     """
#     This function is triggered when the chat application is resumed after being paused.
#     It initializes the ConversationSummaryBufferMemory with the history from the previous session.
#     """

#     cl.user_session.set("current_thread", thread["id"])

#     # Create a new ConversationSummaryBufferMemory with the specified parameters
#     conversation_summary_memory = ConversationSummaryBufferMemory(
#         llm=azure_services.model,
#         max_token_limit=4000,
#         memory_key="chat_history",
#         return_messages=True,
#     )

#     # Retrieve the root messages from the thread
#     root_messages = [m for m in thread["steps"] if m["parentId"] is None] # type: ignore
#     # Iterate over the root messages
#     for message in root_messages:
#         # Check the type of the message
#         if message["type"] == "USER_MESSAGE": # type: ignore
#             # Add user message to the chat memory
#             conversation_summary_memory.chat_memory.add_user_message(message["output"])
#         else:
#             # Add AI message to the chat memory
#             conversation_summary_memory.chat_memory.add_ai_message(message["output"]) # type: ignore

#     # Call the setup_runnable function to continue the chat application
#     await setup_runnable(conversation_summary_memory)


# # @cl.oauth_callback
# # def oauth_callback(
# #     provider_id: str,
# #     token: str,
# #     raw_user_data: Dict[str, str],
# #     default_user: cl.User,
# # ) -> Optional[cl.User]:
# #     """
# #     This function is an OAuth callback handler.
# #     It is triggered when the user authorizes the application with a third-party provider.
# #     It receives the provider ID, token, raw user data, and default user as input parameters.
# #     It returns an optional User object.
# #     """
# #     return default_user


# @cl.on_chat_end
# async def on_chat_end():
#     """
#     This function is called when a chat ends.
#     It sets the current_thread value in the user session to None.
#     """
#     cl.user_session.set("current_thread", None)
