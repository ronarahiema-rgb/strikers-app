import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import execute_query


class AuthService:
    """
    Service class die alle authenticatie-logica afhandelt:
    inloggen, registreren en het controleren van e-mailadressen.

    Door deze logica in een class te bundelen (encapsulation) blijft
    de routes.py overzichtelijk en kan dezelfde logica hergebruikt
    worden voor student, docent en ouder.

    Attributes:
        TABELLEN (list): Klasseattribuut — lijst van tuples met per rol
                         de tabelnaam, primary key en rolnaam.
        beschikbare_rollen (list): Lijst van alle geldige rolnamen.
        tabel_map (dict): Koppeling van rolnaam naar (tabel, pk) voor snelle opzoekingen.
    """

    # Klasseattribuut: lijst van tuples (complex datatype)
    TABELLEN = [
        ("student", "student_id", "leerling"),
        ("docent", "docent_id", "docent"),
        ("ouder", "ouder_id", "ouder"),
    ]

    def __init__(self):
        # Lijst van geldige rollen (list — complex datatype)
        self.beschikbare_rollen: list = [r for _, _, r in self.TABELLEN]

        # Dict die elke rol koppelt aan zijn tabel en primary key (dict — complex datatype)
        self.tabel_map: dict = {
            rol: (tabel, pk)
            for tabel, pk, rol in self.TABELLEN
        }

    def _zoek_tabel_voor_rol(self, rol):
        """Haal de juiste tabelnaam en primary key kolom op voor een rol."""
        return self.tabel_map.get(rol, (None, None))

    def login(self, email, password):
        """
        Probeer een gebruiker in te loggen.

        Args:
            email (str): Het ingevoerde e-mailadres.
            password (str): Het ingevoerde wachtwoord.

        Returns:
            dict: {"naam": str, "user_id": int, "rol": str} als login slaagt.
            None: als de combinatie niet klopt.
        """
        for tabel, pk, rol in self.TABELLEN:
            result = execute_query(
                f"SELECT {pk}, name, email, password_hash FROM {tabel} WHERE email = ?",
                (email,),
            )
            if isinstance(result, list) and result and check_password_hash(result[0]["password_hash"], password):
                return {
                    "naam": result[0]["name"],
                    "user_id": result[0][pk],
                    "email": result[0]["email"],
                    "rol": rol,
                }
        return None

    def email_bestaat(self, rol, email):
        """Controleer of een e-mailadres al bestaat in de tabel van deze rol."""
        tabel, pk = self._zoek_tabel_voor_rol(rol)
        if not tabel:
            return False
        result = execute_query(
            f"SELECT {pk} FROM {tabel} WHERE email = ?",
            (email,),
        )
        return isinstance(result, list) and bool(result)

    def registreer(self, rol, naam, achternaam, email, password):
        """
        Registreer een nieuwe gebruiker voor een bepaalde rol.

        Args:
            rol (str): "leerling", "docent" of "ouder".
            naam (str): Voornaam.
            achternaam (str): Achternaam.
            email (str): E-mailadres.
            password (str): Wachtwoord (wordt gehashed opgeslagen).

        Returns:
            bool: True bij succes, False als de rol ongeldig is.
        """
        tabel, _ = self._zoek_tabel_voor_rol(rol)
        if not tabel:
            return False

        execute_query(
            f"INSERT INTO {tabel} (name, surname, email, password_hash) VALUES (?, ?, ?, ?)",
            (naam, achternaam, email, generate_password_hash(password)),
        )
        return True

    def reset_wachtwoord(self, email):
        """
        Zoekt een gebruiker op via e-mail, genereert een tijdelijk wachtwoord
        en slaat de nieuwe hash op in de database.

        Args:
            email (str): Het e-mailadres van de gebruiker.

        Returns:
            str: Het tijdelijke wachtwoord als het account gevonden is.
            None: Als het e-mailadres niet bestaat.
        """
        for tabel, pk, rol in self.TABELLEN:
            result = execute_query(
                f"SELECT {pk} FROM {tabel} WHERE email = ?",
                (email,),
            )
            if isinstance(result, list) and result:
                # Genereer een willekeurig tijdelijk wachtwoord van 8 tekens
                tijdelijk_wachtwoord = secrets.token_urlsafe(8)

                # Hash het tijdelijke wachtwoord en sla het op in de database
                nieuwe_hash = generate_password_hash(tijdelijk_wachtwoord)
                execute_query(
                    f"UPDATE {tabel} SET password_hash = ? WHERE email = ?",
                    (nieuwe_hash, email),
                )
                return tijdelijk_wachtwoord

        return None

    def wijzig_wachtwoord(self, rol, email, huidig_wachtwoord, nieuw_wachtwoord):
        """
        Wijzigt het wachtwoord van een ingelogde gebruiker.

        Args:
            rol (str): De rol van de gebruiker ("leerling", "docent" of "ouder").
            email (str): Het e-mailadres van de gebruiker.
            huidig_wachtwoord (str): Het huidig ingevoerde wachtwoord.
            nieuw_wachtwoord (str): Het nieuwe wachtwoord.

        Returns:
            bool: True als het wachtwoord gewijzigd is, False als het huidige wachtwoord onjuist is.
        """
        tabel, pk = self._zoek_tabel_voor_rol(rol)

        # Haal de opgeslagen hash op uit de database
        result = execute_query(
            f"SELECT password_hash FROM {tabel} WHERE email = ?",
            (email,),
        )

        # Controleer of het huidige wachtwoord klopt
        if not isinstance(result, list) or not result:
            return False

        opgeslagen_hash = result[0]["password_hash"]
        if not check_password_hash(opgeslagen_hash, huidig_wachtwoord):
            return False

        # Sla het nieuwe wachtwoord op als hash
        nieuwe_hash = generate_password_hash(nieuw_wachtwoord)
        execute_query(
            f"UPDATE {tabel} SET password_hash = ? WHERE email = ?",
            (nieuwe_hash, email),
        )
        return True
