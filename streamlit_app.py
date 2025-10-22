import streamlit as st
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Clear cache to force refresh
st.cache_data.clear()
st.cache_resource.clear()

# Import calendar tools with error handling - v3
try:
    import sys
    if 'calendar_tools' in sys.modules:
        del sys.modules['calendar_tools']
    from calendar_tools import (
        create_calendar_event,
        find_event_by_subject,
        update_calendar_event,
        delete_calendar_event,
    )
except Exception as e:
    st.error(f"Failed to import calendar tools: {e}")
    st.info("Please refresh the page to try again.")
    st.stop()
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Configuration in sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Get credentials from user input, Streamlit secrets, or environment
    def get_credential(key, default=""):
        # Try Streamlit secrets first (for cloud deployment)
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            return os.getenv(key, default)
    
    tenant_id = st.text_input("Tenant ID", value=get_credential("TENANT_ID", "common"), help="Your Azure tenant ID")
    client_id = st.text_input("Client ID", value=get_credential("CLIENT_ID"), help="Your Azure app client ID")
    client_secret = st.text_input("Client Secret", value=get_credential("CLIENT_SECRET"), type="password", help="Your Azure app client secret")
    user_email = st.text_input("User Email", value=get_credential("USER_EMAIL"), help="Your Microsoft account email")
    google_api_key = st.text_input("Google API Key", value=get_credential("GOOGLE_API_KEY"), type="password", help="Your Google AI API key")
    
    # Store credentials in session state
    if client_id and client_secret and google_api_key:
        st.session_state.tenant_id = tenant_id
        st.session_state.client_id = client_id
        st.session_state.client_secret = client_secret
        st.session_state.user_email = user_email
        st.session_state.google_api_key = google_api_key
        
        # Set environment variables
        os.environ["TENANT_ID"] = tenant_id
        os.environ["CLIENT_ID"] = client_id
        os.environ["CLIENT_SECRET"] = client_secret
        os.environ["USER_EMAIL"] = user_email or ""
        os.environ["GOOGLE_API_KEY"] = google_api_key
        
        # Update graph_api_auth module variables directly
        import graph_api_auth
        graph_api_auth.CLIENT_ID = client_id
        graph_api_auth.TENANT_ID = tenant_id
        graph_api_auth.AUTHORITY = f"https://login.microsoftonline.com/{tenant_id}"
        if hasattr(graph_api_auth, 'CLIENT_SECRET'):
            graph_api_auth.CLIENT_SECRET = client_secret
        
        credentials_ready = True
        
        # Add button to reinitialize agent
        if st.button("🔄 Reinitialize Agent"):
            # Clear cached agent
            if "agent" in st.session_state:
                del st.session_state.agent
            st.rerun()
    else:
        credentials_ready = False
    
    if not credentials_ready:
        st.warning("Please provide all credentials to continue")
        st.info("Get your credentials from:")
        st.markdown("- **Azure**: [portal.azure.com](https://portal.azure.com)")
        st.markdown("- **Google**: [console.cloud.google.com](https://console.cloud.google.com)")
        st.stop()

# Initialize LLM and tools
@st.cache_resource
def initialize_agent():
    # Ensure environment variables are set
    if not os.getenv("GOOGLE_API_KEY"):
        raise Exception("Google API Key is required")
    if not os.getenv("CLIENT_ID"):
        raise Exception("Client ID is required")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    @tool
    def create_event(subject: str, start_time: str, end_time: str, attendees: List[str], body: str):
        """Creates a calendar event with subject, start/end times (ISO format), attendees list, and body."""
        return create_calendar_event(subject, start_time, end_time, attendees, body)

    @tool
    def find_event(subject: str, time_window: Dict[str, str]):
        """Finds events by subject within a time window (dict with 'start' and 'end' keys in ISO format)."""
        return find_event_by_subject(subject, time_window)

    @tool
    def update_event(event_id: str, new_start_time: str, new_end_time: str):
        """Updates an event's start and end times (ISO format) using its event_id."""
        return update_calendar_event(event_id, new_start_time, new_end_time)

    @tool
    def delete_event(event_id: str):
        """Deletes an event using its event_id."""
        return delete_calendar_event(event_id)

    tools = [create_event, find_event, update_event, delete_event]
    return create_react_agent(llm, tools)

# Streamlit UI
st.set_page_config(page_title="AI-Powered Outlook Calendar Agent", page_icon="📅")

st.title("📅 AI-Powered Outlook Calendar Agent")
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

if "agent" not in st.session_state and credentials_ready:
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
    # Simple check for existing token cache
    import os
    token_cache_exists = os.path.exists("token_cache.json")
    
    if not token_cache_exists:
        st.warning("🔐 Authentication Required")
        st.info("You need to authenticate with Microsoft to access your calendar. Try sending a message to start the authentication process.")

# Chat input
if credentials_ready:
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
                    response = st.session_state.agent.invoke({"messages": [("user", prompt)]})
                    ai_response = response["messages"][-1].content
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with examples
with st.sidebar:
    if credentials_ready:
        st.markdown("---")
        st.header("📝 Example Commands")
        
        examples = [
            "Book a meeting titled 'Quarterly Business Review' tomorrow from 10:00 AM to 11:30 AM with john@company.com and sarah@company.com about Q4 planning discussion",
            "Schedule a team standup every Monday at 9:00 AM with dev-team@company.com",
            "Find meetings with 'standup' in the title for this week",
            "Create a client presentation on Friday 2:00 PM to 4:00 PM with client@example.com about project demo",
            "Reschedule the team meeting to 2 PM next Tuesday",
            "Cancel the client presentation meeting"
        ]
        
        for example in examples:
            if st.button(example, key=example):
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
        
        st.markdown("---")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()