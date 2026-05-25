from flask import render_template, Blueprint, request, redirect, url_for, session, flash, current_app
from app.main.form_data import form_data
from app.db import execute_query

class QuestionService:
    """Service voor het beheren van vragen en notificaties in de database."""
    
    def __init__(self):
        """Initialiseert de service met de juiste tabelnaam en statussen."""
        self.table_name = "vragen"
        self.allowed_statuses = ["open", "beantwoord", "verwijderd"]

    def insert_question(self, question, student_id):
        """Voegt een nieuwe, open vraag toe voor een student."""
        query = f"INSERT INTO {self.table_name} (vraag, status, student_id, is_gelezen) VALUES (?, 'open', ?, 0)"
        execute_query(query, (question, student_id))

    def get_open_questions(self):
        """Haalt alle openstaande vragen op, van nieuw naar oud."""
        query = f"SELECT * FROM {self.table_name} WHERE status = 'open' ORDER BY aangemaakt_op DESC"
        return execute_query(query)

    def answer_question(self, question_id, answer):
        """Slaat het antwoord op en wijzigt de status naar 'beantwoord'."""
        query = f"UPDATE {self.table_name} SET antwoord = ?, status = 'beantwoord' WHERE id = ?"
        execute_query(query, (answer, question_id))

    def delete_question(self, question_id):      
        """Verwijdert een specifieke vraag permanent uit de database."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        execute_query(query, (question_id,))

    def get_answered_questions(self, student_id=None):
        """
        Haalt alle beantwoorde vragen op. 
        Als student_id is meegegeven, komen de eigen vragen bovenaan.
        """
        if student_id:
            query = f"SELECT * FROM {self.table_name} WHERE status = 'beantwoord' ORDER BY (student_id = ?) DESC, aangemaakt_op DESC"
            return execute_query(query, (student_id,))
        else:
            query = f"SELECT * FROM {self.table_name} WHERE status = 'beantwoord' ORDER BY aangemaakt_op DESC"
            return execute_query(query)
    
    def get_unread_notifications(self, student_id):
        """Haalt alle ongelezen, beantwoorde vragen (notificaties) op voor een student."""
        query = f"SELECT * FROM {self.table_name} WHERE student_id = ? AND status = 'beantwoord' AND is_gelezen = 0"
        result = execute_query(query, (student_id,))
        return result if isinstance(result, list) else []

    def mark_all_as_read(self, student_id):
        """Markeert alle notificaties van een student als gelezen."""
        query = f"UPDATE {self.table_name} SET is_gelezen = 1 WHERE student_id = ? AND status = 'beantwoord'"
        execute_query(query, (student_id,))