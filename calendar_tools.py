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
        
        event_ids = [event['id'] for event in events]
        result = f"Found {len(events)} event(s). Event IDs: {json.dumps(event_ids)}\n\n"
        for event in events:
            result += f"📅 {event['subject']}\n"
            result += f"   ID: {event['id']}\n"
            result += f"   Start: {event['start']['dateTime']}\n"
            result += f"   End: {event['end']['dateTime']}\n"
            if event.get('location', {}).get('displayName'):
                result += f"   Location: {event['location']['displayName']}\n"
            if event.get('attendees'):
                attendees = [a['emailAddress']['address'] for a in event['attendees']]
                result += f"   Attendees: {', '.join(attendees)}\n"
            result += "\n"
        return result
    else:
        raise Exception(f"Failed to get events: {response.text}")

def find_event_by_subject(subject, time_window):
    """
    Finds an event by its subject within a given time window. Returns event IDs for deletion.
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
        
        event_ids = [event['id'] for event in events]
        result = f"Found {len(events)} event(s). Event IDs: {json.dumps(event_ids)}\n\n"
        for event in events:
            result += f"📅 {event['subject']}\n"
            result += f"   ID: {event['id']}\n"
            result += f"   Start: {event['start']['dateTime']}\n"
            result += f"   End: {event['end']['dateTime']}\n"
            if event.get('location', {}).get('displayName'):
                result += f"   Location: {event['location']['displayName']}\n"
            if event.get('attendees'):
                attendees = [a['emailAddress']['address'] for a in event['attendees']]
                result += f"   Attendees: {', '.join(attendees)}\n"
            result += "\n"
        return result
    else:
        raise Exception(f"Failed to find event: {response.text}")

def update_calendar_event(event_id, new_start_time=None, new_end_time=None, new_subject=None, new_body=None, new_location=None):
    """
    Updates an existing event in the Outlook Calendar.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    event_data = {}
    if new_start_time:
        event_data["start"] = {"dateTime": new_start_time, "timeZone": "UTC"}
    if new_end_time:
        event_data["end"] = {"dateTime": new_end_time, "timeZone": "UTC"}
    if new_subject:
        event_data["subject"] = new_subject
    if new_body:
        event_data["body"] = {"contentType": "HTML", "content": new_body}
    if new_location:
        event_data["location"] = {"displayName": new_location}
    
    response = requests.patch(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers,
        data=json.dumps(event_data)
    )
    
    if response.status_code == 200:
        return f"✅ Event updated successfully."
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

def delete_multiple_events(event_ids_json):
    """
    Deletes multiple events from the Outlook Calendar.
    """
    event_ids = json.loads(event_ids_json)
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    
    deleted_count = 0
    failed_count = 0
    
    for event_id in event_ids:
        response = requests.delete(
            f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
            headers=headers
        )
        if response.status_code == 204:
            deleted_count += 1
        else:
            failed_count += 1
    
    return f"✅ Deleted {deleted_count} event(s) successfully. Failed: {failed_count}"

def add_attendees_to_event(event_id, attendee_emails):
    """
    Adds attendees to an existing event.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    # First get current event
    response = requests.get(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get event: {response.text}")
    
    event = response.json()
    current_attendees = event.get('attendees', [])
    
    # Add new attendees
    for email in attendee_emails:
        current_attendees.append({"emailAddress": {"address": email}, "type": "required"})
    
    # Update event
    event_data = {"attendees": current_attendees}
    response = requests.patch(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers,
        data=json.dumps(event_data)
    )
    
    if response.status_code == 200:
        return f"✅ Added {len(attendee_emails)} attendee(s) successfully."
    else:
        raise Exception(f"Failed to add attendees: {response.text}")

def remove_attendees_from_event(event_id, attendee_emails):
    """
    Removes attendees from an existing event.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    # First get current event
    response = requests.get(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get event: {response.text}")
    
    event = response.json()
    current_attendees = event.get('attendees', [])
    
    # Remove specified attendees
    updated_attendees = [a for a in current_attendees if a['emailAddress']['address'] not in attendee_emails]
    
    # Update event
    event_data = {"attendees": updated_attendees}
    response = requests.patch(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers,
        data=json.dumps(event_data)
    )
    
    if response.status_code == 200:
        return f"✅ Removed {len(attendee_emails)} attendee(s) successfully."
    else:
        raise Exception(f"Failed to remove attendees: {response.text}")

def update_event_location(event_id, location):
    """
    Updates the location of an existing event.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    event_data = {"location": {"displayName": location}}
    response = requests.patch(
        f"{GRAPH_API_ENDPOINT}/me/events/{event_id}",
        headers=headers,
        data=json.dumps(event_data)
    )
    
    if response.status_code == 200:
        return f"✅ Event location updated to '{location}'."
    else:
        raise Exception(f"Failed to update location: {response.text}")