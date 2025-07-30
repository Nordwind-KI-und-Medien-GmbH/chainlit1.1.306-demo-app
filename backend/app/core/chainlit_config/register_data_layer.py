import os

import chainlit as cl
import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

from ..config import simple_rag_config

cl_data._data_layer = SQLAlchemyDataLayer(conninfo=simple_rag_config.DATABASE_URL)
