from core.config import herbalista_config

# Force User Session and Login only if CHAINLIT_AUTH_SECRET is defined (else its going to try the login and fail)
if herbalista_config.CHAINLIT_AUTH_SECRET:
    from core.chainlit import register_header_auth_callback