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
_app = None
_token_caches = {}

def _get_cache_file(client_id):
    return f"token_cache_{client_id[:8]}.json"

def _load_cache(client_id):
    if client_id not in _token_caches:
        _token_caches[client_id] = msal.SerializableTokenCache()
        cache_file = _get_cache_file(client_id)
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                _token_caches[client_id].deserialize(f.read())
    return _token_caches[client_id]

def _save_cache(client_id):
    if client_id in _token_caches and _token_caches[client_id].has_state_changed:
        try:
            cache_file = _get_cache_file(client_id)
            with open(cache_file, "w") as f:
                f.write(_token_caches[client_id].serialize())
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

def get_access_token(client_id=None, tenant_id=None, force_new_login=False):
    use_client_id = client_id or CLIENT_ID
    use_tenant_id = tenant_id or TENANT_ID
    
    if not use_client_id:
        raise Exception("CLIENT_ID is required")
    
    cache = _load_cache(use_client_id)
    authority = f"https://login.microsoftonline.com/{use_tenant_id}"
    app = msal.PublicClientApplication(
        client_id=use_client_id,
        authority=authority,
        token_cache=cache
    )
    
    # Try silent authentication (skip if force_new_login)
    if not force_new_login:
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
            try:
                flow = app.initiate_device_flow(scopes=SCOPE)
                if 'device_code' not in flow:
                    st.error("🔐 Authentication Setup Failed")
                    st.info("Please check your Azure app configuration:")
                    st.markdown("- Ensure 'Allow public client flows' is enabled")
                    st.markdown("- Verify redirect URI includes device code flow")
                    st.markdown("- Check API permissions are granted")
                    raise Exception("Device flow not supported. Check Azure app configuration.")
                    
                st.session_state.pending_auth = {'flow': flow, 'app': app, 'client_id': use_client_id}
                
                st.info("🔐 **Quick Sign-In Required**")
                auth_url = f"{flow['verification_uri']}?otc={flow['user_code']}"
                st.markdown(f"### [👉 Click here to sign in]({auth_url})")
                st.markdown("---")
                st.markdown("**Or manually:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Visit: {flow['verification_uri']}")
                with col2:
                    st.code(f"Code: {flow['user_code']}")
                st.warning("⚠️ After signing in, send a message to continue")
                
                raise Exception("Please authenticate and try again")
            except Exception as e:
                st.error(f"🔐 Authentication Error: {str(e)}")
                st.info("Try using the Quick Calendar Event Creation form below instead.")
                raise Exception("Authentication failed. Use the form to create events.")
        else:
            # Try to complete the pending authentication
            import time
            pending = st.session_state.pending_auth
            
            # Check if enough time has passed since last attempt
            if 'last_attempt' not in pending:
                pending['last_attempt'] = time.time()
                st.session_state.pending_auth = pending
            
            time_since_last = time.time() - pending['last_attempt']
            interval = pending['flow'].get('interval', 5)
            
            if time_since_last < interval:
                time.sleep(interval - time_since_last)
            
            pending['last_attempt'] = time.time()
            st.session_state.pending_auth = pending
            
            result = pending['app'].acquire_token_by_device_flow(pending['flow'])
            
            if result and "access_token" in result:
                _save_cache(pending.get('client_id', use_client_id))
                del st.session_state.pending_auth
                return result["access_token"]
            else:
                # Still pending or failed
                flow = pending['flow']
                st.info("🔐 **Waiting for sign-in...**")
                auth_url = f"{flow['verification_uri']}?otc={flow['user_code']}"
                st.markdown(f"### [👉 Click here to sign in]({auth_url})")
                st.markdown("---")
                st.markdown("**Or manually:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Visit: {flow['verification_uri']}")
                with col2:
                    st.code(f"Code: {flow['user_code']}")
                st.warning("⚠️ After signing in, send a message to continue")
                
                error = result.get('error_description', 'Please complete authentication') if result else 'Please complete authentication'
                raise Exception(error)
        
    except ImportError:
        result = app.acquire_token_interactive(scopes=SCOPE)
        if result and "access_token" in result:
            _save_cache(use_client_id)
            return result["access_token"]
        raise Exception("Authentication failed")

def logout(client_id=None):
    """Clears the token cache to log out the user."""
    use_client_id = client_id or CLIENT_ID
    cache_file = _get_cache_file(use_client_id)
    
    # Clear in-memory cache
    if use_client_id in _token_caches:
        del _token_caches[use_client_id]
    
    # Delete cache file
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    return True