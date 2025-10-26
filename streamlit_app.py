import streamlit as st
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
import os
from typing import List, Dict

# Check if running in demo mode (credentials in secrets)
try:
    demo_mode = bool(st.secrets.get("CLIENT_ID")) and bool(st.secrets.get("GOOGLE_API_KEY"))
except:
    demo_mode = False

if demo_mode:
    # Pre-configured demo mode
    os.environ["TENANT_ID"] = "common"
    os.environ["CLIENT_ID"] = st.secrets["CLIENT_ID"]
    os.environ["CLIENT_SECRET"] = st.secrets.get("CLIENT_SECRET", "")
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    credentials_ready = True
else:
    credentials_ready = False

# Import calendar tools with error handling - v3
try:
    import sys
    if 'calendar_tools' in sys.modules:
        del sys.modules['calendar_tools']
    from calendar_tools import (
        create_calendar_event,
        get_all_events,
        find_event_by_subject,
        update_calendar_event,
        delete_calendar_event,
        delete_multiple_events,
        add_attendees_to_event,
        remove_attendees_from_event,
        update_event_location,
    )
except Exception as e:
    st.error(f"Failed to import calendar tools: {e}")
    st.info("Please refresh the page to try again.")
    st.stop()
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Configuration (only show if not in demo mode)
if not demo_mode:
    with st.sidebar:
        st.header("🔧 Configuration")
        st.info("🔧 **Setup Required:** Create your own Azure app for calendar access")
        
        tenant_id = st.text_input("Tenant ID", value="common", help="Use 'common' for personal Microsoft accounts")
        client_id = st.text_input("Client ID", help="Your Azure app client ID")
        client_secret = st.text_input("Client Secret", type="password", help="Your Azure app client secret")
        user_email = st.text_input("Your Microsoft Email", help="Your Outlook/Microsoft account email")
        google_api_key = st.text_input("Your Google API Key", type="password", help="Get from: https://console.cloud.google.com")
        
        if client_id and client_secret and google_api_key:
            os.environ["TENANT_ID"] = tenant_id
            os.environ["CLIENT_ID"] = client_id
            os.environ["CLIENT_SECRET"] = client_secret
            os.environ["USER_EMAIL"] = user_email or ""
            os.environ["GOOGLE_API_KEY"] = google_api_key
            credentials_ready = True
        else:
            credentials_ready = False
            st.warning("🔑 Please provide all credentials to continue")
            st.stop()

# Update graph_api_auth module
if credentials_ready:
    import graph_api_auth
    graph_api_auth.CLIENT_ID = os.environ["CLIENT_ID"]
    graph_api_auth.TENANT_ID = os.environ["TENANT_ID"]
    graph_api_auth.AUTHORITY = f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}"

# Initialize LLM and tools
def initialize_agent():
    # Ensure environment variables are set
    if not os.getenv("GOOGLE_API_KEY"):
        raise Exception("Google API Key is required")
    if not os.getenv("CLIENT_ID"):
        raise Exception("Client ID is required")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    @tool
    def create_event(subject: str, start_time: str, end_time: str, attendees: List[str] = None, body: str = ""):
        """Creates a calendar event. Parameters: subject (event title), start_time (ISO format like '2025-09-01T14:00:00'), end_time (ISO format), attendees (optional list of emails), body (optional description)."""
        return create_calendar_event(subject, start_time, end_time, attendees, body)

    @tool
    def get_events(time_window: Dict[str, str]):
        """Gets ALL events in a time period. Use when user asks 'what events do I have today/this week/etc'. Parameter: time_window dict with 'start' and 'end' in ISO format. Example: {'start': '2025-01-23T00:00:00', 'end': '2025-01-23T23:59:59'}"""
        return get_all_events(time_window)

    @tool
    def find_event(subject: str, time_window: Dict[str, str]):
        """Finds events by subject/title. Use when user mentions a specific event name. Parameters: subject (event title to search), time_window (dict with 'start' and 'end' in ISO format)."""
        return find_event_by_subject(subject, time_window)

    @tool
    def update_event(event_id: str, new_start_time: str = None, new_end_time: str = None, new_subject: str = None, new_body: str = None, new_location: str = None):
        """Updates event details. Parameters: event_id (required), new_start_time (optional ISO format), new_end_time (optional), new_subject (optional), new_body (optional), new_location (optional)."""
        return update_calendar_event(event_id, new_start_time, new_end_time, new_subject, new_body, new_location)

    @tool
    def add_attendees(event_id: str, attendee_emails: List[str]):
        """Adds attendees to an existing event. Parameters: event_id (from find_event), attendee_emails (list of email addresses)."""
        return add_attendees_to_event(event_id, attendee_emails)

    @tool
    def remove_attendees(event_id: str, attendee_emails: List[str]):
        """Removes attendees from an existing event. Parameters: event_id (from find_event), attendee_emails (list of email addresses to remove)."""
        return remove_attendees_from_event(event_id, attendee_emails)

    @tool
    def set_location(event_id: str, location: str):
        """Sets or updates the location of an event. Parameters: event_id (from find_event), location (location name/address)."""
        return update_event_location(event_id, location)

    @tool
    def delete_event(event_id: str):
        """Deletes a single event. Parameter: event_id (from find_event result)."""
        return delete_calendar_event(event_id)

    @tool
    def delete_multiple(event_ids_json: str):
        """Deletes multiple events at once. Parameter: event_ids_json (JSON string array of event IDs from find_event result). Example: '["id1", "id2"]'"""
        return delete_multiple_events(event_ids_json)

    tools = [create_event, get_events, find_event, update_event, delete_event, delete_multiple, add_attendees, remove_attendees, set_location]
    return create_agent(llm, tools)

# Streamlit UI
st.set_page_config(page_title="AI Calendar Agent" + (" - Demo" if demo_mode else ""), page_icon="📅", layout="wide")

st.title("📅 AI-Powered Outlook Calendar Agent")
if demo_mode:
    st.markdown("**Demo Version** - Manage your Microsoft Outlook Calendar with natural language!")
else:
    st.markdown("Manage your Microsoft Outlook Calendar using natural language commands!")

if not credentials_ready:
    st.info("👈 Please configure your credentials in the sidebar to get started")
    st.markdown("### What this app does:")
    st.markdown("- 📅 Create calendar events with natural language")
    st.markdown("- 🔍 Find and search your meetings")
    st.markdown("- ✏️ Update and reschedule events")
    st.markdown("- ❌ Cancel meetings")
    st.markdown("### Example commands:")
    st.code('"Book a meeting with the team tomorrow at 3 PM"')
    st.code('"Find my meetings this week"')
    st.code('"Reschedule the client call to 4 PM"')
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Force fresh agent creation every time
if credentials_ready:
    with st.spinner("Initializing AI agent..."):
        try:
            st.session_state.agent = initialize_agent()
            st.success("✅ Agent initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check authentication status
if credentials_ready:
    try:
        from graph_api_auth import _load_cache, get_access_token
        import msal
        
        cache = _load_cache(os.environ["CLIENT_ID"])
        app = msal.PublicClientApplication(
            client_id=os.environ["CLIENT_ID"],
            authority=f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}",
            token_cache=cache
        )
        accounts = app.get_accounts()
        
        if accounts:
            authenticated_email = accounts[0].get('username', 'Microsoft User')
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ Signed in as: **{authenticated_email}**")
            with col2:
                if st.button("🚪 Logout", type="secondary"):
                    from graph_api_auth import logout
                    logout(os.environ["CLIENT_ID"])
                    if 'messages' in st.session_state:
                        st.session_state.messages = []
                    if 'agent' in st.session_state:
                        del st.session_state.agent
                    st.success("Logged out successfully!")
                    st.rerun()
            authenticated = True
        else:
            st.info("🔐 **Sign in with your Microsoft account to get started**")
            st.markdown("✨ Each user signs in with their own account - your calendar stays private!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔑 Sign In with Microsoft", type="primary", use_container_width=True):
                    try:
                        get_access_token(os.environ["CLIENT_ID"], os.environ["TENANT_ID"], force_new_login=True)
                        st.rerun()
                    except Exception:
                        pass
            authenticated = False
            st.stop()
    except Exception as e:
        st.error(f"Setup error: {str(e)}")
        st.stop()

# Hide test buttons in demo mode
if not demo_mode and credentials_ready:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Test Authentication"):
            from graph_api_auth import get_access_token
            try:
                get_access_token(os.environ["CLIENT_ID"], os.environ["TENANT_ID"])
                st.success("Authentication successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Authentication error: {str(e)}")

# Chat input
if credentials_ready:
    st.markdown("---")
    prompt = st.chat_input("Type your calendar request...")
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    # Check authentication before processing
                    from graph_api_auth import get_access_token
                    try:
                        get_access_token(os.environ["CLIENT_ID"], os.environ["TENANT_ID"])
                    except Exception as auth_error:
                        st.error(f"Authentication required: {str(auth_error)}")
                        st.session_state.messages.append({"role": "assistant", "content": "Please sign in above and try again."})
                        st.stop()
                    
                    # Use agent for all requests
                    if "agent" not in st.session_state:
                        st.error("Agent not initialized. Please refresh the page.")
                        st.stop()
                    
                    # Build conversation history for context
                    conversation = [(msg["role"], msg["content"]) for msg in st.session_state.messages]
                    response = st.session_state.agent.invoke({"messages": conversation})
                    ai_response = response["messages"][-1].content
                    
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with examples
with st.sidebar:
    if credentials_ready:
        st.header("💡 Example Commands")
        
        examples = [
            "What events do I have today?",
            "Create a team meeting tomorrow at 2 PM",
            "Add john@email.com to the team meeting",
            "Remove sarah@email.com from the standup",
            "Find all meetings this week",
            "Delete the client call",
            "Change meeting location to Room 301"
        ]
        
        for example in examples:
            if st.button(example, key=example, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        st.caption("Your calendar data is accessed securely via Microsoft OAuth. No data is stored.")