from langchain.callbacks.base import BaseCallbackHandler

from chainlit import chainlit as cl

# Callback handler for handling streaming responses from the language model
class StreamHandler(BaseCallbackHandler):
    """
    A callback handler for handling streaming responses from the language model.

    Attributes:
        msg (cl.Message): The message object used for streaming the response.

    Methods:
        on_llm_new_token: Called when a new token is received from the language model.
        on_llm_end: Called when the streaming response from the language model ends.
    """

    def __init__(self):
        self.msg = None

    async def on_llm_new_token(self, token: str, **kwargs):
        if not token:
            return

        if self.msg is None:
            self.msg = cl.Message(content="", author="Assistant")

        await self.msg.stream_token(token)

    async def on_llm_end(self, response: str, **kwargs):  # type: ignore
        if self.msg:
            await self.msg.send()
        self.msg = None
