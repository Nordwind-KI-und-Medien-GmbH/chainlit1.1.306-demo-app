import os
import logging

import chainlit as cl
import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

from ..config import simple_rag_config
from ..monitoring import initialize_pg_monitor, get_pg_monitor

logger = logging.getLogger(__name__)


def init_data_layer():
    """Initialize data layer with connection monitoring after chainlit context is ready"""

    # Initialize PostgreSQL connection monitor (non-blocking)
    monitor = initialize_pg_monitor(simple_rag_config.DATABASE_URL)
    logger.info("PostgreSQL connection monitor initialized")

    # Initialize data layer first (let Chainlit handle its own connection)
    try:
        # Create data layer first
        cl_data._data_layer = SQLAlchemyDataLayer(conninfo=simple_rag_config.DATABASE_URL)
        logger.info("Data layer initialized successfully")

        # Just log that monitoring is available, don't test connection here
        # as it can cause event loop issues during initialization
        if monitor and monitor.engine:
            logger.info("Connection monitoring is available")
        else:
            logger.warning("Connection monitoring not available")

    except Exception as e:
        logger.error(f"Failed to initialize data layer: {e}")
        raise
