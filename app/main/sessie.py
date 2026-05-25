from flask import render_template, Blueprint, request, redirect, url_for, session, flash, current_app
from app.db import execute_query

class SessieService:

    @staticmethod
    def get_timer_data(student_id):
        query = """
            SELECT 
                TIME(created_at) AS checked_in_at,
                TIMESTAMPDIFF(MINUTE, created_at, NOW()) AS elapsed_minutes
            FROM checkin 
            WHERE student_id = ? AND DATE(created_at) = CURDATE()
        """
        return execute_query(query, (student_id,))

    @staticmethod
    def get_chart_data(student_id):
        query = """
            SELECT 
                DATE(created_at) AS dag,
                AVG(mood) AS avg_mood,
                AVG(status) AS avg_status,
                AVG(backpack) AS avg_backpack
            FROM checkin
            WHERE student_id = ?
              AND MONTH(created_at) = MONTH(CURDATE())
              AND YEAR(created_at) = YEAR(CURDATE())
            GROUP BY DATE(created_at)
            ORDER BY dag
        """
        return execute_query(query, (student_id,))

    @staticmethod
    def get_geschiedenis(student_id):
        # haal alle check-ins op van deze student
        query = """
            SELECT
                DATE(created_at) AS dag,
                TIME(created_at) AS tijd,
                mood,
                status,
                focus_target,
                backpack
            FROM checkin
            WHERE student_id = ?
            ORDER BY created_at DESC
        """
        return execute_query(query, (student_id,))

    @staticmethod
    def get_geschiedenis_chart(student_id):
        # grafiek data per dag voor deze student
        query = """
            SELECT
                DATE(created_at) AS dag,
                AVG(mood) AS avg_mood,
                AVG(status) AS avg_status,
                AVG(backpack) AS avg_backpack
            FROM checkin
            WHERE student_id = ?
            GROUP BY DATE(created_at)
            ORDER BY dag
        """
        return execute_query(query, (student_id,))

    @staticmethod
    def calculate_time(result):
        if result and len(result) > 0:
            last_entry = result[-1]
            time_parts = str(last_entry['checked_in_at']).split(':')
            elapsed = last_entry['elapsed_minutes']
            return {
                'hours': time_parts[0],
                'minutes': time_parts[1],
                'hours_passed': elapsed // 60,
                'minutes_passed': elapsed % 60,
                'is_ingecheckt': True
            }
        return {
            'hours': "00",
            'minutes': "00",
            'hours_passed': 0,
            'minutes_passed': 0,
            'is_ingecheckt': False
        }