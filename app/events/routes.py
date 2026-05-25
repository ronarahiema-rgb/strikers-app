from dateutil.parser import isoparse
from flask import abort, redirect, render_template, request, url_for

from app.events import bp, create_event, get_event, get_events, update_event

CREATE_ERROR_MESSAGE = (
    "Event kon niet worden aangemaakt. Zorg dat de datum in de toekomst ligt."
)


@bp.route("/")
def index():
    """Render the events overview page."""
    events = get_events()
    return render_template("events/index.html", events=events)


@bp.route("/view/<int:event_id>")
def view(event_id):
    event = get_event(event_id) or abort(404)
    event["eventDate"] = isoparse(event["eventDate"])
    return render_template("events/view.html", event=event)


@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        description = request.form["description"].strip()
        date = request.form["date"]
        event_id = create_event(description, date)

        if not event_id:
            return render_template("events/create.html", error=CREATE_ERROR_MESSAGE)
        return redirect(url_for("events.view", event_id=event_id))

    return render_template("events/create.html")


@bp.route("/edit/<int:event_id>", methods=["GET", "POST"])
def edit(event_id):
    if request.method == "POST":
        description = request.form["description"].strip()
        date = request.form["date"]
        update_event(event_id, description, date)
        return redirect(url_for("events.view", event_id=event_id))

    event = get_event(event_id) or abort(404)
    event["eventDate"] = isoparse(event["eventDate"])
    return render_template("events/edit.html", event=event)
