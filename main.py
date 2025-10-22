from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from calendar_tools import (
    create_calendar_event,
    find_event_by_subject,
    update_calendar_event,
    delete_calendar_event,
)
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

from typing import List, Dict

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
agent_executor = create_react_agent(llm, tools)

class Query(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "outlook-calendar-agent"}

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/invoke-agent")
async def invoke_agent(query: Query):
    try:
        response = agent_executor.invoke({"messages": [("user", query.query)]})
        return {"status": "success", "response": response["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))