import msal
import os
import webbrowser
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID", "common")
USER_EMAIL = os.getenv("USER_EMAIL")
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
        try:
            with open(TOKEN_CACHE_FILE, "w") as f:
                f.write(_token_cache.serialize())
        except Exception:
            # Ignore cache save errors in cloud environments
            pass

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
    Uses device code flow for cloud-friendly authentication.
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
        # Check if we're in a cloud environment (Streamlit Cloud or no display)
        import sys
        is_cloud = (
            'STREAMLIT_SERVER_PORT' in os.environ or 
            'streamlit.app' in os.environ.get('HOSTNAME', '') or
            not os.environ.get('DISPLAY')
        )
        
        if is_cloud:
            # Use device code flow for cloud deployment
            flow = app.initiate_device_flow(scopes=SCOPE)
            if "user_code" not in flow:
                raise Exception("Failed to create device flow")
            
            # Display device code in Streamlit instead of console
            import streamlit as st
            st.error("🔐 Authentication Required!")
            st.info(f"**Step 1:** Go to: {flow['verification_uri']}")
            st.code(f"Step 2: Enter code: {flow['user_code']}")
            st.warning("**Step 3:** After authenticating, refresh this page to continue.")
            
            # Don't wait for device flow completion in cloud - let user refresh
            raise Exception("Please complete authentication and refresh the page.")
        else:
            # Use interactive flow for local development
            result = app.acquire_token_interactive(scopes=SCOPE)
            _save_cache()
    
    if result and "access_token" in result:
        return result["access_token"]
    else:
        error_msg = result.get('error_description', result.get('error', 'Authentication required')) if result else 'Authentication required'
        raise Exception(f"I am sorry, I cannot fulfill this request. I need to have access to the user's calendar in order to create the event. Please complete authentication first: {error_msg}")