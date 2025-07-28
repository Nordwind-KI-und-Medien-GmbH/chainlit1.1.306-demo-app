import os
from core.config import herbalista_config
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

# if the DATABASE_URL is set, use aktivate the chainlit data layer that is effectively activating the thread history feature in the frontend
if herbalista_config.DATABASE_URL:
    # both (user auth and data layer) is needed to activate the thread history feature in the frontend
    from app.core.chainlit import register_header_auth_callback
    from app.core.chainlit import register_data_layer