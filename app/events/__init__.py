"""CRUD helpers for the events table."""

from datetime import datetime

from dateutil.parser import isoparse
from flask import Blueprint

from app.db import execute_query

bp = Blueprint("events", __name__)


def create_event(description: str, date: str) -> int | None:
    """Create a new event and return its id when successful."""
    query = "INSERT INTO Event (description, eventDate) VALUES (?, ?)"
    if not check_date_passed(date):
        formatted_date = format_event_date(date)
        result = execute_query(query, (description, formatted_date))
        return result["insertId"]

    return None


def get_event(event_id: int) -> dict | None:
    """Fetch one event by id."""
    query = "SELECT * FROM Event WHERE eventId = ?"
    result = execute_query(query, event_id)
    if result:
        return result[0]
    return None


def get_events():
    """Fetch all events."""
    query = "SELECT * FROM Event"
    return execute_query(query)


def update_event(event_id: int, description: str, date: str):
    """Update an existing event."""
    query = "UPDATE Event SET description = ?, eventDate = ? WHERE eventId = ?"
    execute_query(query, (description, format_event_date(date), event_id))


def check_date_passed(date: str) -> bool:
    """Return True when the given ISO date is in the past."""
    parsed_date = isoparse(date)
    return parsed_date < datetime.now()


def format_event_date(date: str) -> str:
    """Format an ISO date for database storage."""
    return isoparse(date).strftime("%Y-%m-%d %H:%M:%S")


from app.events import routes
