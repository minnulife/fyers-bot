# file: token_smoketest.py
from fyers_apiv3 import fyersModel

APP_ID = "1MYQ32PLKP-100"
with open("token.txt") as f:
    ACCESS_TOKEN = f.read().strip()     # beware of trailing spaces/newlines

fyers = fyersModel.FyersModel(client_id=APP_ID, token=ACCESS_TOKEN, log_path="")
print("Profile:", fyers.get_profile())  # should print {'s':'ok', ...}

# Optional: quick quotes test
print("Quotes:", fyers.quotes({"symbols": "NSE:NIFTY50-INDEX"}))
