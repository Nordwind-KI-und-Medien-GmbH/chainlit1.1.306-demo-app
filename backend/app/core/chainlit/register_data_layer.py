import os
from ..config import herbalista_config
from ....chainlit import chainlit as cl
from ....chainlit.data.sql_alchemy import SQLAlchemyDataLayer


@cl.data_layer
def get_data_layer():
    # return SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:///C:/adrian/dev/herbalista/herbalista-poc/herbalista.db")
    return SQLAlchemyDataLayer(conninfo=herbalista_config.DATABASE_URL)

