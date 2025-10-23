import streamlit as st
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Clear cache to force refresh
st.cache_data.clear()
st.cache_resource.clear()

# Force clear agent cache
if 'agent' in st.session_state:
    del st.session_state['agent']

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
    
    st.info("🔧 **Setup Required:** Create your own Azure app for calendar access")
    
    tenant_id = st.text_input("Tenant ID", value="common", help="Use 'common' for personal Microsoft accounts")
    client_id = st.text_input("Client ID", help="Your Azure app client ID")
    client_secret = st.text_input("Client Secret", type="password", help="Your Azure app client secret")
    user_email = st.text_input("Your Microsoft Email", help="Your Outlook/Microsoft account email")
    google_api_key = st.text_input("Your Google API Key", type="password", help="Get from: https://console.cloud.google.com")
    
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
        st.warning("🔑 Please provide all credentials to continue")
        st.info("**Setup Instructions:**")
        st.markdown("**Azure App:** [portal.azure.com](https://portal.azure.com) → App registrations → New registration")
        st.markdown("**Google API:** [console.cloud.google.com](https://console.cloud.google.com) → Enable Generative Language API")
        st.stop()

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
        from graph_api_auth import _load_cache
        import msal
        
        from graph_api_auth import _load_cache
        cache = _load_cache(client_id)
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            token_cache=cache
        )
        accounts = app.get_accounts()
        
        if accounts:
            authenticated_email = accounts[0].get('username', user_email or 'Microsoft User')
            st.success(f"✅ Authenticated as: {authenticated_email}")
            if user_email and authenticated_email.lower() != user_email.lower():
                st.warning(f"⚠️ Note: Authenticated as {authenticated_email}, but configured for {user_email}")
        else:
            st.info(f"🔐 Not authenticated. Will authenticate as: {user_email or 'your Microsoft account'}")
    except:
        st.info("🔐 Authentication status unknown. Send a message to check.")

# Test authentication button
if credentials_ready and st.button("🔐 Test Authentication"):
    from graph_api_auth import get_access_token
    try:
        token = get_access_token(client_id, tenant_id)
        st.success("Authentication successful!")
        st.info("Refreshing page to update authentication status...")
        st.rerun()
    except Exception as e:
        st.error(f"Authentication needed: {str(e)}")

# Test calendar creation button
if credentials_ready and st.button("📅 Test Calendar Event Creation"):
    try:
        from calendar_tools import create_calendar_event
        result = create_calendar_event(
            "Birthday Party for Nephew",
            "2025-09-01T14:00:00",
            "2025-09-01T16:00:00",
            ["friend@email.com"],
            "Birthday celebration for my nephew"
        )
        st.success(result)
    except Exception as e:
        st.error(f"❌ Failed to create test event: {str(e)}")

# Direct agent test button
if credentials_ready and st.button("🤖 Test Agent Directly"):
    try:
        if "agent" in st.session_state:
            test_prompt = "Create a birthday party for my nephew on September 1st, 2025 from 2 PM to 4 PM with friend@email.com"
            st.write(f"Testing agent with: {test_prompt}")
            response = st.session_state.agent.invoke({"messages": [("user", test_prompt)]})
            st.write("Agent response:")
            st.json(response)
        else:
            st.error("Agent not initialized")
    except Exception as e:
        st.error(f"Agent test failed: {str(e)}")

# Simple calendar creation form (bypassing AI agent due to quota limits)
if credentials_ready:
    st.markdown("### Quick Calendar Event Creation")
    with st.form("calendar_form"):
        col1, col2 = st.columns(2)
        with col1:
            event_title = st.text_input("Event Title", placeholder="Birthday Party for Nephew")
            event_date = st.date_input("Event Date")
            start_time = st.time_input("Start Time")
        with col2:
            end_time = st.time_input("End Time")
            attendees = st.text_area("Attendees (one email per line)", placeholder="friend@email.com")
            event_body = st.text_area("Event Description", placeholder="Birthday celebration")
        
        if st.form_submit_button("Create Event"):
            try:
                # Direct authentication for form
                from graph_api_auth import get_access_token
                import datetime
                
                # Simple form-based authentication
                st.info("🔐 Creating calendar event...")
                
                # For now, show instructions for manual setup
                st.warning("**Manual Setup Required:**")
                st.markdown("1. Create your own Azure app at [portal.azure.com](https://portal.azure.com)")
                st.markdown("2. Enable 'Allow public client flows'")
                st.markdown("3. Add Calendars.ReadWrite permission")
                st.markdown("4. Use your own Client ID and Secret")
                st.stop()
                
                from calendar_tools import create_calendar_event
                
                # Convert to ISO format
                start_datetime = datetime.datetime.combine(event_date, start_time).isoformat()
                end_datetime = datetime.datetime.combine(event_date, end_time).isoformat()
                attendee_list = [email.strip() for email in attendees.split('\n') if email.strip()]
                
                result = create_calendar_event(
                    event_title,
                    start_datetime,
                    end_datetime,
                    attendee_list,
                    event_body
                )
                
                st.success(f"✅ Event '{event_title}' created successfully!")
                st.json(result)
                
            except Exception as e:
                st.error(f"❌ Failed to create event: {str(e)}")

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
                        get_access_token(client_id, tenant_id)  # This will show auth UI if needed
                    except Exception as auth_error:
                        auth_msg = f"Authentication required: {str(auth_error)}"
                        st.error(auth_msg)
                        st.session_state.messages.append({"role": "assistant", "content": "Please complete authentication above and try again."})
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
        st.markdown("---")
        st.header("📝 Example Commands")
        
        examples = [
            "Create a birthday party for my nephew on September 1st, 2025 from 2 PM to 4 PM with friend@email.com",
            "Book a team meeting tomorrow at 10 AM with colleague@company.com about project updates",
            "Schedule a client call on Friday 3 PM to 4 PM with client@example.com",
            "Find my meetings for this week",
            "Create a doctor appointment next Monday at 2 PM",
            "Schedule a family dinner on Sunday at 6 PM with family@email.com"
        ]
        
        for example in examples:
            if st.button(example, key=example):
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()
        
        st.markdown("---")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()