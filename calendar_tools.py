import requests
from graph_api_auth import get_access_token
import json

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def create_calendar_event(subject, start_time, end_time, attendees, body):
    """
    Creates a new event in the Outlook Calendar.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    event_data = {
        "subject": subject,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "attendees": [{"emailAddress": {"address": attendee}, "type": "required"} for attendee in attendees],
        "body": {"contentType": "HTML", "content": body}
    }
    
    response = requests.post(
        f"{GRAPH_API_ENDPOINT}/me/events",
        headers=headers,
        data=json.dumps(event_data)
    )
    
    if response.status_code == 201:
        event = response.json()
        return f"✅ Event '{subject}' created successfully from {start_time} to {end_time}."
    else:
        raise Exception(f"Failed to create event: {response.text}")

def get_all_events(time_window):
    """
    Gets all events within a given time window.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        "$filter": f"start/dateTime ge '{time_window['start']}' and end/dateTime le '{time_window['end']}'",
        "$orderby": "start/dateTime"
    }
    
    response = requests.get(
        f"{GRAPH_API_ENDPOINT}/me/events",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        events = response.json().get('value', [])
        if not events:
            return "No events found for this time period."
        
        result = f"Found {len(events)} event(s):\n\n"
        for event in events:
            result += f"📅 {event['subject']}\n"
            result += f"   Start: {event['start']['dateTime']}\n"
            result += f"   End: {event['end']['dateTime']}\n"
            if event.get('attendees'):
                attendees = [a['emailAddress']['address'] for a in event['attendees']]
                result += f"   Attendees: {', '.join(attendees)}\n"
            result += "\n"
        return result
    else:
        raise Exception(f"Failed to get events: {response.text}")

def find_event_by_subject(subject, time_window):
    """
    Finds an event by its subject within a given time window.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    params = {
        "$filter": f"startsWith(subject, '{subject}') and start/dateTime ge '{time_window['start']}' and end/dateTime le '{time_window['end']}'"
    }
    
    response = requests.get(
        f"{GRAPH_API_ENDPOINT}/me/events",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        events = response.json().get('value', [])
        if not events:
            return "No events found matching your criteria."
        
        result = f"Found {len(events)} event(s):\n\n"
        for event in events:
            result += f"📅 {event['subject']}\n"
            result += f"   Start: {event['start']['dateTime']}\n"
            result += f"   End: {event['end']['dateTime']}\n"
            if event.get('attendees'):
                attendees = [a['emailAddress']['address'] for a in event['attendees']]
                result += f"   Attendees: {', '.join(attendees)}\n"
            result += "\n"
        return result
    else:
        raise Exception(f"Failed to find event: {response.text}")

def update_calendar_event(event_id, new_start_time, new_end_time):
    """
    Updates an existing event in the Outlook Calendar.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    event_data = {
        "start": {"dateTime": new_start_time, "timeZone": "UTC"},
        "end": {"dateTime": new_end_time, "timeZone": "UTC"}
    }
    
    response = requests.patch(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers,
        data=json.dumps(event_data)
    )
    
    if response.status_code == 200:
        return f"✅ Event updated successfully. New time: {new_start_time} to {new_end_time}."
    else:
        raise Exception(f"Failed to update event: {response.text}")

def delete_calendar_event(event_id):
    """
    Deletes an event from the Outlook Calendar.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    
    response = requests.delete(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        return "✅ Event deleted successfully."
    else:
        raise Exception(f"Failed to delete event: {response.text}")