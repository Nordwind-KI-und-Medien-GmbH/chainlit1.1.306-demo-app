import os

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

from ..config import simple_rag_config


@cl.data_layer
def get_data_layer():
    # return SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:///C:/adrian/dev/herbalista/herbalista-poc/herbalista.db")
    return SQLAlchemyDataLayer(conninfo=simple_rag_config.DATABASE_URL)
