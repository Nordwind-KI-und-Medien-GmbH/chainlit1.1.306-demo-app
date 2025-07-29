import os

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from core.config import simple_rag_config

# if the DATABASE_URL is set, use aktivate the chainlit data layer that is effectively activating the thread history feature in the frontend
if simple_rag_config.DATABASE_URL:
    # both (user auth and data layer) is needed to activate the thread history feature in the frontend
    from app.core.chainlit import register_header_auth_callback

    # from app.core.chainlit import register_data_layer  # Commented out - not needed for basic functionality
