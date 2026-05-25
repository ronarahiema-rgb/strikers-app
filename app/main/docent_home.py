from flask import render_template, Blueprint, request, redirect, url_for, session, flash, current_app
from app.main.form_data import form_data
from app.db import execute_query
from app.main.vraag_service import QuestionService


class DocentHome:

    @staticmethod
    def get_vandaag_checkins():
        result = execute_query(
            "SELECT student_id, mood, status, focus_target, created_at "
            "FROM checkin WHERE DATE(created_at) = CURDATE() "
            "ORDER BY created_at DESC"
        )
        return result if isinstance(result, list) else []
    @staticmethod
    def get_checkin_chart():
        query = """
            SELECT 
                c.student_id,
                s.name,
                ROUND((c.mood + c.status + c.backpack) / 3) AS gemiddelde_score
            FROM checkin c
            JOIN student s ON c.student_id = s.student_id
            WHERE DATE(c.created_at) = CURDATE()
            ORDER BY s.name
        """
        return execute_query(query)

    @staticmethod
    def get_checkout_chart():
        query = """
            SELECT 
                c.student_id,
                s.name,
                FLOOR((
                    CASE c.feeling
                        WHEN 'Slecht' THEN 25
                        WHEN 'Matig' THEN 50
                        WHEN 'Goed' THEN 75
                        WHEN 'Heel goed' THEN 100
                    END + c.energy + c.satisfaction_percentage
                ) / 3) + 0 AS gemiddelde_score
            FROM checkout c
            JOIN student s ON c.student_id = s.student_id
            WHERE DATE(c.created_at) = CURDATE()
            ORDER BY s.name
        """
        return execute_query(query)

    @staticmethod
    def get_vragen_preview():
        service = QuestionService()
        open_vragen = service.get_open_questions()
        if not isinstance(open_vragen, list):
            open_vragen = []
        return {
            'aantal': len(open_vragen),
            'preview': open_vragen[:3]
        }