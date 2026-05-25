from datetime import date

from flask import render_template, Blueprint, request, redirect, url_for, session, flash, current_app
from app.main.form_data import form_data
from app.db import execute_query


class check_in_class:

    def __init__(self):
        self.mood, self.status, self.focus_target, self.backpack = form_data("mood", "status", "focus_target", "backpack") 
    
    
    def has_already_checked_in(self):
        today = date.today().isoformat()
        result = execute_query(
            """
            SELECT id FROM checkin
            WHERE student_id = ?
            AND DATE(created_at) = ?
            LIMIT 1
            """,
            (session.get("user_id"), today)
        )
        return bool(result)   
    
    def insert_db(self):
        query = f"INSERT INTO checkin (mood, status, focus_target, backpack, student_id) VALUES (?, ?, ?, ?,? )  "
        result = execute_query(query,(self.mood,self.status,self.focus_target,self.backpack,session.get("user_id") ))
        print(result)

