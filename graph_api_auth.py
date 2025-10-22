import msal
import os
import webbrowser
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID", "common")
SCOPE = ["Calendars.ReadWrite", "User.Read"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
TOKEN_CACHE_FILE = "token_cache.json"

_app = None
_token_cache = None

def _load_cache():
    global _token_cache
    if _token_cache is None:
        _token_cache = msal.SerializableTokenCache()
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, "r") as f:
                _token_cache.deserialize(f.read())
    return _token_cache

def _save_cache():
    if _token_cache and _token_cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(_token_cache.serialize())

def _get_msal_app():
    global _app
    if _app is None:
        cache = _load_cache()
        _app = msal.PublicClientApplication(
            client_id=CLIENT_ID,
            authority=AUTHORITY,
            token_cache=cache
        )
    return _app

def get_access_token(client_id=None, tenant_id=None):
    """
    Acquires an access token for the Microsoft Graph API.
    Uses interactive browser flow for user authentication.
    """
    # Use provided credentials or fall back to environment variables
    use_client_id = client_id or CLIENT_ID
    use_tenant_id = tenant_id or TENANT_ID
    
    if not use_client_id:
        raise Exception("CLIENT_ID is required. Please set it in environment variables.")
    
    # Create app with provided credentials
    cache = _load_cache()
    authority = f"https://login.microsoftonline.com/{use_tenant_id}"
    app = msal.PublicClientApplication(
        client_id=use_client_id,
        authority=authority,
        token_cache=cache
    )
    
    accounts = app.get_accounts()
    
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPE, account=accounts[0])
    
    if not result:
        print("\n" + "="*60)
        print("AUTHENTICATION REQUIRED")
        print("="*60)
        print("Opening browser for authentication...")
        print("Please sign in with your Microsoft account.")
        print("="*60)
        
        result = app.acquire_token_interactive(scopes=SCOPE)
        _save_cache()
    
    if "access_token" in result:
        return result["access_token"]
    else:
        error_msg = result.get('error_description', result.get('error', 'Unknown error'))
        raise Exception(f"Could not acquire access token: {error_msg}")