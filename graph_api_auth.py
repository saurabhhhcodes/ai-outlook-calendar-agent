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
    use_client_id = client_id or CLIENT_ID
    use_tenant_id = tenant_id or TENANT_ID
    
    if not use_client_id:
        raise Exception("CLIENT_ID is required")
    
    cache = _load_cache()
    authority = f"https://login.microsoftonline.com/{use_tenant_id}"
    app = msal.PublicClientApplication(
        client_id=use_client_id,
        authority=authority,
        token_cache=cache
    )
    
    # Try silent authentication
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPE, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]
    
    # Need authentication
    try:
        import streamlit as st
        
        # Check if we have a pending device flow
        if 'pending_auth' not in st.session_state:
            flow = app.initiate_device_flow(scopes=SCOPE)
            st.session_state.pending_auth = {'flow': flow, 'app': app}
            
            st.error("🔐 Authentication Required")
            st.info(f"1. Go to: {flow['verification_uri']}")
            st.code(f"2. Enter: {flow['user_code']}")
            st.warning("3. After signing in, send your message again")
            
            raise Exception("Please authenticate and try again")
        else:
            # Try to complete the pending authentication
            pending = st.session_state.pending_auth
            result = pending['app'].acquire_token_by_device_flow(pending['flow'])
            
            if result and "access_token" in result:
                _save_cache()
                del st.session_state.pending_auth
                return result["access_token"]
            else:
                # Still pending or failed
                flow = pending['flow']
                st.error("🔐 Authentication Required")
                st.info(f"1. Go to: {flow['verification_uri']}")
                st.code(f"2. Enter: {flow['user_code']}")
                st.warning("3. After signing in, send your message again")
                
                error = result.get('error_description', 'Please complete authentication') if result else 'Please complete authentication'
                raise Exception(error)
        
    except ImportError:
        result = app.acquire_token_interactive(scopes=SCOPE)
        if result and "access_token" in result:
            _save_cache()
            return result["access_token"]
        raise Exception("Authentication failed")