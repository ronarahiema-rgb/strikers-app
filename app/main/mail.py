import smtplib
from email.mime.text import MIMEText
from os import environ
from dotenv import load_dotenv

load_dotenv()

# Haal de Gmail gegevens op uit de .env file
EMAIL_ADRES = environ.get("EMAIL_ADRES")
EMAIL_WACHTWOORD = environ.get("EMAIL_WACHTWOORD")


def stuur_tijdelijk_wachtwoord(ontvanger_email, tijdelijk_wachtwoord):
    """
    Stuurt een e-mail met het tijdelijke wachtwoord naar de gebruiker.

    Args:
        ontvanger_email (str): Het e-mailadres van de gebruiker.
        tijdelijk_wachtwoord (str): Het gegenereerde tijdelijke wachtwoord.
    """
    onderwerp = "BrainBoost – Je tijdelijke wachtwoord"
    inhoud = f"""Hallo,

Je hebt een nieuw wachtwoord aangevraagd voor BrainBoost.

Je tijdelijke wachtwoord is: {tijdelijk_wachtwoord}

Log in met dit wachtwoord en verander het daarna zo snel mogelijk.

Met vriendelijke groet,
BrainBoost
"""

    # Maak het e-mailbericht aan
    bericht = MIMEText(inhoud)
    bericht["Subject"] = onderwerp
    bericht["From"] = EMAIL_ADRES
    bericht["To"] = ontvanger_email

    # Maak verbinding met Gmail en verstuur de e-mail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADRES, EMAIL_WACHTWOORD)
        server.sendmail(EMAIL_ADRES, ontvanger_email, bericht.as_string())
