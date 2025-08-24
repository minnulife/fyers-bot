# file: fyers_v3_end_to_end.py
# pip install fyers-apiv3

from fyers_apiv3 import fyersModel
import urllib.parse as up
import sys

APP_ID     = "1MYQ32PLKP-100" # Replace with your client ID
SECRET_KEY     = "O7UJP2L0LA"    # Replace with your secret key
REDIRECT_URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"  # Replace with your redirect URI
TOKEN_FILE   = "token.txt"

def die(msg):
    print("\nERROR:", msg)
    sys.exit(1)

def main():
    # --- 1) Build session and generate login URL ---
    session = fyersModel.SessionModel(
        client_id=APP_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )

    auth_url = session.generate_authcode()
    print("\nOpen this URL, login fully (PIN/TOTP), then copy the full redirect URL:")
    print(auth_url)

    raw = input("\nPaste the FULL redirect URL here (or just the auth_code):\n> ").strip()
    # Extract auth_code if a full URL was pasted
    if "auth_code=" in raw:
        parsed = up.urlparse(raw)
        qs = up.parse_qs(parsed.query)
        raw = qs.get("auth_code", [""])[0]

    if not raw:
        die("No auth_code captured.")

    session.set_token(raw)

    # --- 2) Exchange for access_token (v3) ---
    resp = session.generate_token()
    print("\nToken exchange response:", resp)

    access_token = resp.get("access_token")
    if not access_token:
        die("No access_token returned. Check APP_ID/SECRET/REDIRECT_URI and use a fresh auth_code.")

    # --- 3) Construct final token EXACTLY: APP_ID:access_token ---
    token_str = access_token
    '''
    # Sanity checks (these catch -209/-15 causes)
    if ":" not in token_str:
        die("Final token missing colon. Must be 'APP_ID:access_token'.")
    left, _, right = token_str.partition(":")
    if left != APP_ID:
        die(f"Left side of token != APP_ID. Got '{left}', expected '{APP_ID}'.")
    if not right or right.count(".") < 2:  # JWT has 2 dots typically
        die("Right side does not look like a JWT access token.")
    '''
    print("\nFinal ACCESS_TOKEN string (save this):")
    print(token_str)

    # --- 4) Smoke test with the SAME values used above ---
    fy = fyersModel.FyersModel(client_id=APP_ID, token=token_str, log_path="")

    prof = fy.get_profile()
    print("\nget_profile() ->", prof)
    if not isinstance(prof, dict) or prof.get("s") != "ok":
        die("get_profile() not ok. The token is not being accepted.")

    q = fy.quotes({"symbols": "NSE:NIFTY50-INDEX"})
    print("\nquotes(NIFTY50-INDEX) ->", q)
    if not isinstance(q, dict) or q.get("s") != "ok":
        die("quotes() not ok. Verify symbol and token.")

    # --- 5) Save for your algo ---
    with open(TOKEN_FILE, "w", newline="") as f:
        f.write(token_str)
    print(f"\nSaved ACCESS_TOKEN to {TOKEN_FILE}. You can now import this in your other scripts.")

if __name__ == "__main__":
    main()
