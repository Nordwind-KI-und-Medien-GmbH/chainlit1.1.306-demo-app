from typing import Dict, Optional

import chainlit as cl

from .user_session import simple_rag_cl_user_session


@cl.header_auth_callback  # type: ignore
def header_auth_callback(headers: Dict) -> Optional[cl.User]:
    # Verify the signature of a token in the header (ex: jwt token)
    # or check that the value is matching a row from your database
    user_name = headers.get("auth-header", "Guest")
    user_role = headers.get("auth-role", "guest")
    return cl.User(
        identifier=user_name, metadata={"role": user_role, "provider": "header"}
    )
