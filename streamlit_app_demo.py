import streamlit as st
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
import os
from typing import List, Dict

# Pre-configured credentials (hidden from users)
os.environ["TENANT_ID"] = "common"
os.environ["CLIENT_ID"] = st.secrets.get("CLIENT_ID", "")
os.environ["CLIENT_SECRET"] = st.secrets.get("CLIENT_SECRET", "")
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", "")

# Import calendar tools
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

# Update graph_api_auth module variables
import graph_api_auth
graph_api_auth.CLIENT_ID = os.environ["CLIENT_ID"]
graph_api_auth.TENANT_ID = os.environ["TENANT_ID"]
graph_api_auth.AUTHORITY = f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}"

# Initialize LLM and tools
def initialize_agent():
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
    def delete_event(event_id: str):
        """Deletes a single event. Parameter: event_id (from find_event result)."""
        return delete_calendar_event(event_id)

    @tool
    def delete_multiple(event_ids_json: str):
        """Deletes multiple events at once. Parameter: event_ids_json (JSON string array of event IDs from find_event result). Example: '["id1", "id2"]'"""
        return delete_multiple_events(event_ids_json)

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

    tools = [create_event, get_events, find_event, update_event, delete_event, delete_multiple, add_attendees, remove_attendees, set_location]
    return create_agent(llm, tools)

# Streamlit UI
st.set_page_config(page_title="AI Calendar Agent Demo", page_icon="📅", layout="wide")

st.title("📅 AI-Powered Outlook Calendar Agent")
st.markdown("**Demo Version** - Manage your Microsoft Outlook Calendar with natural language!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check authentication status
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
        st.success(f"✅ Signed in as: **{authenticated_email}**")
        authenticated = True
    else:
        st.info("🔐 **Sign in with your Microsoft account to get started**")
        st.markdown("Click the button below to authenticate:")
        if st.button("🔑 Sign In with Microsoft", type="primary"):
            try:
                get_access_token(os.environ["CLIENT_ID"], os.environ["TENANT_ID"])
                st.rerun()
            except Exception as e:
                st.error(f"Authentication error: {str(e)}")
        authenticated = False
        st.stop()
except Exception as e:
    st.error(f"Setup error: {str(e)}")
    st.stop()

# Initialize agent
if "agent" not in st.session_state:
    with st.spinner("Initializing AI agent..."):
        try:
            st.session_state.agent = initialize_agent()
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Type your calendar request... (e.g., 'What events do I have today?')")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                conversation = [(msg["role"], msg["content"]) for msg in st.session_state.messages]
                response = st.session_state.agent.invoke({"messages": conversation})
                ai_response = response["messages"][-1].content
                
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with examples
with st.sidebar:
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
