import os
from fyers_apiv3 import fyersModel
from config import CLIENT_ID, TOKEN_PATH

def get_fyers():
    token_path = os.path.abspath(TOKEN_PATH)
    with open(token_path, "r", encoding="utf-8") as f:
        access_token = f.read().strip()
    assert ":" not in access_token, "Use RAW v3 JWT (no APP_ID prefix)."
    assert access_token.count(".") >= 2, "Token doesn't look like a JWT."
    return fyersModel.FyersModel(client_id=CLIENT_ID, token=access_token, log_path="")
