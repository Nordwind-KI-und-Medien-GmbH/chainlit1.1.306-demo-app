from app.core.config import simple_rag_config

# Force User Session and Login only if CHAINLIT_AUTH_SECRET is defined (else its going to try the login and fail)
if simple_rag_config.CHAINLIT_AUTH_SECRET:
    from app.core.chainlit import register_header_auth_callback
