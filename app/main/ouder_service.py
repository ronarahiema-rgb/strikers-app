from app.db import execute_query


class OuderService:
    """
    Service class voor alle ouder-gerelateerde logica:
    het koppelen van een kind en het ophalen van hun check-ins.

    Attributes:
        ouder_id (int): Het ID van de ingelogde ouder.
        studenten (list): Lijst van gekoppelde studenten als dicts.
        checkins_per_student (dict): Koppeling van student_id naar lijst van check-ins.
    """

    def __init__(self, ouder_id):
        # Simpel datatype: int
        self.ouder_id: int = ouder_id

        # Complex datatype: list — wordt gevuld door get_gekoppelde_studenten()
        self.studenten: list = []

        # Complex datatype: dict — wordt gevuld door get_checkins_van_student()
        self.checkins_per_student: dict = {}

    def get_gekoppelde_studenten(self):
        """
        Haal alle studenten op die gekoppeld zijn aan deze ouder.
        Slaat het resultaat op in self.studenten.

        Twee losse queries omdat de API geen JOINs ondersteunt.

        Returns:
            list: Lijst van studenten met student_id, name en surname.
        """
        koppelingen = execute_query(
            "SELECT student_id FROM ouder_student WHERE ouder_id = ?",
            (self.ouder_id,),
        )
        if not isinstance(koppelingen, list) or not koppelingen:
            self.studenten = []
            return self.studenten

        for rij in koppelingen:
            student = execute_query(
                "SELECT student_id, name, surname FROM student WHERE student_id = ?",
                (rij["student_id"],),
            )
            if isinstance(student, list) and student:
                self.studenten.append(student[0])

        return self.studenten

    def get_checkins_van_student(self, student_id):
        """
        Haal de check-ins op van een specifieke student.
        Slaat het resultaat op in self.checkins_per_student.

        Args:
            student_id (int): Het ID van de student.

        Returns:
            list: Lijst van check-ins, nieuwste eerst.
        """
        result = execute_query(
            "SELECT mood, status, focus_target, backpack, created_at "
            "FROM checkin WHERE student_id = ? ORDER BY created_at DESC",
            (student_id,),
        )
        checkins = result if isinstance(result, list) else []
        self.checkins_per_student[student_id] = checkins
        return checkins

    def koppel_student_via_email(self, student_email):
        """
        Koppel een student aan deze ouder door het e-mailadres van de student.

        Args:
            student_email (str): Het e-mailadres van de student.

        Returns:
            bool: True als de koppeling gelukt is, False als de student niet gevonden werd.
        """
        student = execute_query(
            "SELECT student_id FROM student WHERE email = ?",
            (student_email,),
        )
        if not isinstance(student, list) or not student:
            return False

        student_id = student[0]["student_id"]

        bestaand = execute_query(
            "SELECT id FROM ouder_student WHERE ouder_id = ? AND student_id = ?",
            (self.ouder_id, student_id),
        )
        if isinstance(bestaand, list) and bestaand:
            return True

        execute_query(
            "INSERT INTO ouder_student (ouder_id, student_id) VALUES (?, ?)",
            (self.ouder_id, student_id),
        )
        return True

    def ontkoppel_student(self, student_id):
        # verwijder de koppeling tussen de ouder en het kind
        execute_query(
            "DELETE FROM ouder_student WHERE ouder_id = ? AND student_id = ?",
            (self.ouder_id, student_id),
        )
