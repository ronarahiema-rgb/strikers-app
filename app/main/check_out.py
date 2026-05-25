from abc import ABC, abstractmethod
from datetime import date, datetime
from flask import session
from app.main.form_data import form_data
from app.db import execute_query

# --- ABSTRACTIE (De Blauwdruk) ---
class FormHandler(ABC):
    @abstractmethod
    def insert_db(self):
        """Dit dwingt elke subclass om een insert_db functie te hebben."""
        pass

# --- OVERERVING (check_out_class erft van FormHandler) ---
class CheckOutClass(FormHandler):
    def __init__(self):
        # Haalt data op via de functie van je klasgenoten
        f, e, s, l = form_data("feeling", "energy", "satisfaction_percentage", "les_opmerking")
        
        # --- INKAPSELING (_ voor variabelen die 'beschermd' zijn) ---
        self._feeling = f
        self._energy = e
        self._satisfaction = s
        self._les_opmerking = l
        self._student_id = session.get("user_id")   

    def is_valid(self):
        """Check of de verplichte velden zijn ingevuld."""
        return bool(self._feeling and self._energy and self._satisfaction)

    def has_already_checked_out(self):
        """Checkt of de student al een check-out heeft gedaan vandaag.
        dat wordt via de data DATE(), geen tijd.
        Returns: True als er al een check-out is, anders False.
        """
        today = date.today().isoformat()

        result = execute_query(
            """
            SELECT id FROM checkout
            WHERE student_id = ?
            AND DATE(created_at) = ?
            LIMIT 1
            """,
            (self._student_id, today)
        )
        return bool(result)


    def insert_db(self):
        """Slaat de data op in de database."""
        query = "INSERT INTO checkout (student_id, feeling, energy, satisfaction_percentage, les_opmerking) VALUES (?, ?, ?, ?, ?)"
        execute_query(query, (self._student_id, self._feeling, self._energy, self._satisfaction, self._les_opmerking))


class CheckOutSession:
    def __init__(self):
        self._check_out_time = datetime.now()
        self._check_in_time = self._get_check_in_time()
        
        # Berekeningen voor het verschil direct in de class
        delta = self._check_out_time - self._check_in_time
        self._total_seconds = int(delta.total_seconds())
        
        self._hours = self._total_seconds // 3600
        self._minutes = (self._total_seconds % 3600) // 60
        self._seconds = self._total_seconds % 60

    def _get_check_in_time(self):
        """Haalt de inchecktijd op uit de DB voor specifieke student en fixt het formaat."""
        student_id = session.get("user_id")

        result = execute_query(
            """
            SELECT created_at FROM checkin
            WHERE student_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (student_id,)
        )
        check_in_row = result[0] if result else None
        time = check_in_row["created_at"] if check_in_row else datetime.now()

        if isinstance(time, str):
            time = datetime.fromisoformat(time)
        return time.replace(tzinfo=None)


    def save_to_session(self):
        """Zet alle berekende data in de Flask session."""
        session["session_hours"] = self._hours
        session["session_minutes"] = self._minutes
        session["session_seconds"] = self._seconds
        session["check_in_time"] = self._check_in_time.strftime("%H:%M")
        session["check_out_time"] = self._check_out_time.strftime("%H:%M")
        session["checked_out"] = True