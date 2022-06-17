"""Consts for the module."""
from __future__ import annotations

import platform


APP_KEY = "aung2ieCho3aiph7Een3Ei"
API_URL = "https://accounts.api.anki.com/1/sessions"
TOKEN_URL = "https://session-certs.token.global.anki-services.com/vic/"
USER_AGENT = (
    f"pyHAVector/{platform.python_implementation()}/{platform.python_version()}"
)
