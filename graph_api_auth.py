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
                    
                import time
                st.session_state.pending_auth = {'flow': flow, 'app': app, 'client_id': use_client_id, 'last_attempt': time.time()}
                
                auth_url = f"{flow['verification_uri']}?otc={flow['user_code']}"
                
                st.markdown("""
                <div style='text-align: center; padding: 30px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;'>
                    <h3 style='color: #0078D4; margin-bottom: 15px;'>🔐 Sign In Required</h3>
                    <p style='color: #666; margin-bottom: 20px;'>Click the button below to sign in with your Microsoft account</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"<a href='{auth_url}' target='_blank'><button style='width: 100%; padding: 12px; background: #0078D4; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer;'>🔑 Open Microsoft Sign-In</button></a>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style='text-align: center; margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px;'>
                    <p style='color: #856404; margin: 0;'>⚠️ After signing in, return here and send any message to continue</p>
                </div>
                """, unsafe_allow_html=True)
                
                raise Exception("Please authenticate and try again")
            except Exception as e:
                st.error(f"🔐 Authentication Error: {str(e)}")
                st.info("Try using the Quick Calendar Event Creation form below instead.")
                raise Exception("Authentication failed. Use the form to create events.")
        else:
            # Try to complete the pending authentication
            import time
            pending = st.session_state.pending_auth
            
            # Respect polling interval
            time_since_last = time.time() - pending.get('last_attempt', 0)
            interval = pending['flow'].get('interval', 5)
            
            if time_since_last < interval:
                time.sleep(interval - time_since_last)
            
            # Update last attempt time
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
                auth_url = f"{flow['verification_uri']}?otc={flow['user_code']}"
                
                st.markdown("""
                <div style='text-align: center; padding: 30px; background: #d1ecf1; border-radius: 10px; margin: 20px 0;'>
                    <h3 style='color: #0c5460; margin-bottom: 15px;'>⏳ Waiting for Sign-In...</h3>
                    <p style='color: #0c5460; margin-bottom: 20px;'>Complete the sign-in process in the popup window</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"<a href='{auth_url}' target='_blank'><button style='width: 100%; padding: 12px; background: #17a2b8; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer;'>🔄 Re-open Sign-In Window</button></a>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style='text-align: center; margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px;'>
                    <p style='color: #856404; margin: 0;'>⚠️ After signing in, return here and send any message to continue</p>
                </div>
                """, unsafe_allow_html=True)
                
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