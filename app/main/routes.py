from flask import render_template, Blueprint, request, redirect, url_for, session, flash, current_app
from app.main.form_data import form_data
from app.db import execute_query
from app.main.check_in import check_in_class
from app.main.vraag_service import QuestionService
from app.main.auth_service import AuthService
from app.main.ouder_service import OuderService
from app.main.mail import stuur_tijdelijk_wachtwoord

from app.main.check_out import CheckOutClass, CheckOutSession
from app.main.sessie import SessieService
from datetime import datetime
from app.main.docent_home import DocentHome

bp = Blueprint('main', __name__)


def login_required(f):
    """Sta de route alleen toe als er een gebruiker is ingelogd."""
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def rol_required(rol):
    """
    Sta de route alleen toe als de ingelogde gebruiker een specifieke rol heeft.
    Args:
        rol (str): 'leerling', 'docent' of 'ouder'.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("main.login"))
            if session.get("rol") != rol:
                flash("Toegang geweigerd.", "warning")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def _redirect_naar_home():
    """Stuur een ingelogde gebruiker door naar de juiste pagina op basis van rol."""
    rol = session.get("rol")
    if rol == "docent":
        return redirect(url_for("main.docent_home"))
    if rol == "ouder":
        return redirect(url_for("main.ouder_home"))
    return redirect(url_for("main.check_in"))


@bp.route("/")
def index():
    """Landingspagina of redirect naar home bij inlog."""
    if "user" in session:
        return _redirect_naar_home()
    return render_template("main/index.html")




@bp.route("/check_out", methods=["GET", "POST"])
@login_required
def check_out():
    if request.method == "POST":
        # 1. Maak het formulier object aan (haalt zelf data op)
        form = CheckOutClass()
        
        if form.has_already_checked_out():
            flash("Je hebt al een check-out gedaan vandaag.", "warning")
            return render_template("main/end_page.html")
        # 2. Validatie
        if not form.is_valid():
            flash("Vul alle verplichte velden in voordat je verder gaat.")
            return render_template("main/check_out.html")

        # 3. Data in database stoppen
        form.insert_db()

        # 4. Tijd berekenen en in de sessie zetten
        session_logic = CheckOutSession()
        session_logic.save_to_session()

        # 5. Klaar! Door naar de bedankpagina
        return redirect(url_for("main.end_page"))

    return render_template("main/check_out.html")

@bp.route("/end_page")
def end_page():
    if not session.get("checked_out"):
        return redirect(url_for("main.index"))

    return render_template(
        "main/end_page.html",
        session_hours=session.get("session_hours", 0),
        session_minutes=session.get("session_minutes", 0),
        session_seconds=session.get("session_seconds", 0),
        check_in_time=session.get("check_in_time", "--:--"),
        check_out_time=session.get("check_out_time", "--:--"),
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return _redirect_naar_home()

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        auth = AuthService()
        gebruiker = auth.login(email, password)

        if gebruiker:
            session["user"] = gebruiker["naam"]
            session["user_id"] = gebruiker["user_id"]
            session["email"] = gebruiker["email"]
            session["rol"] = gebruiker["rol"]
            return _redirect_naar_home()

        flash("Ongeldig e-mailadres of wachtwoord.")

    return render_template("auth/login.html")


def _verwerk_registratie(rol, template):
    if "user" in session:
        return _redirect_naar_home()

    if request.method == "POST":
        naam = request.form.get("naam", "").strip()
        achternaam = request.form.get("achternaam", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        if password != password_confirm:
            flash("Wachtwoorden komen niet overeen.")
            return render_template(template)

        if len(password) < 6:
            flash("Wachtwoord moet minimaal 6 tekens bevatten.")
            return render_template(template)

        auth = AuthService()
        if auth.email_bestaat(rol, email):
            flash("Dit e-mailadres is al in gebruik.")
            return render_template(template)

        auth.registreer(rol, naam, achternaam, email, password)
        flash("Account aangemaakt! Je kunt nu inloggen.")
        return redirect(url_for("main.login"))

    return render_template(template)


@bp.route("/register")
def register():
    if "user" in session:
        return _redirect_naar_home()
    return render_template("auth/register_keuze.html")


@bp.route("/register/leerling", methods=["GET", "POST"])
def register_leerling():
    return _verwerk_registratie("leerling", "auth/register.html")


@bp.route("/register/docent", methods=["GET", "POST"])
def register_docent():
    return _verwerk_registratie("docent", "auth/register_docent.html")


@bp.route("/register/ouder", methods=["GET", "POST"])
def register_ouder():
    return _verwerk_registratie("ouder", "auth/register_ouder.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/wachtwoord-vergeten", methods=["GET", "POST"])
def wachtwoord_vergeten():
    """
    Pagina waar een gebruiker zijn wachtwoord kan resetten.

    Bij GET: toon het formulier met een e-mailadresveld.
    Bij POST: zoek het account op, genereer een tijdelijk wachtwoord,
              sla het op in de database en stuur het per e-mail.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        auth = AuthService()
        tijdelijk_wachtwoord = auth.reset_wachtwoord(email)

        if tijdelijk_wachtwoord:
            stuur_tijdelijk_wachtwoord(email, tijdelijk_wachtwoord)
            flash("Je tijdelijke wachtwoord is verstuurd naar je e-mail.", "success")
            return redirect(url_for("main.login"))

        flash("Geen account gevonden met dit e-mailadres.", "warning")

    return render_template("auth/wachtwoord_vergeten.html")


@bp.route("/wachtwoord-wijzigen", methods=["GET", "POST"])
@login_required
def wachtwoord_wijzigen():
    """
    Pagina waar een ingelogde gebruiker zijn wachtwoord kan wijzigen.

    Bij GET: toon het formulier.
    Bij POST: controleer huidig wachtwoord en sla het nieuwe op.
    """
    if request.method == "POST":
        huidig = request.form.get("huidig_wachtwoord", "").strip()
        nieuw = request.form.get("nieuw_wachtwoord", "").strip()
        bevestiging = request.form.get("bevestig_wachtwoord", "").strip()

        if nieuw != bevestiging:
            flash("Nieuwe wachtwoorden komen niet overeen.", "warning")
            return render_template("auth/wachtwoord_wijzigen.html")

        if len(nieuw) < 6:
            flash("Nieuw wachtwoord moet minimaal 6 tekens bevatten.", "warning")
            return render_template("auth/wachtwoord_wijzigen.html")

        auth = AuthService()
        gelukt = auth.wijzig_wachtwoord(
            session.get("rol"),
            session.get("email"),
            huidig,
            nieuw,
        )

        if gelukt:
            flash("Wachtwoord succesvol gewijzigd.", "success")
            return redirect(url_for("main.index"))

        flash("Huidig wachtwoord is onjuist.", "warning")

    return render_template("auth/wachtwoord_wijzigen.html")



@bp.route("/check-in")
@login_required
def check_in():
    return render_template("main/check_in.html")


@bp.route("/check-in_form", methods=["POST"])
@login_required
def check_in_form():
    check_in_obj = check_in_class()

    if check_in_obj.has_already_checked_in():
        flash("Je hebt al een check-in gedaan vandaag.", "warning")
        return redirect(url_for("main.end_page"))
    
    check_in_obj.insert_db()
    return redirect(url_for("main.sessie"))


@bp.route("/sessie")
@login_required
def sessie():
    student_id = session.get("user_id")
    result = SessieService.get_timer_data(student_id)
    chart_result = SessieService.get_chart_data(student_id)
    time_data = SessieService.calculate_time(result)

    # NIEUW: Check of de docent iets beantwoord heeft!
    service = QuestionService()
    notificaties = service.get_unread_notifications(student_id)

    return render_template("main/sessie.html",
                           chart_data=chart_result,
                           notificaties=notificaties, # GEEF MEE AAN HTML
                           **time_data)


@bp.route("/mijn-sessies")
@rol_required("leerling")
def mijn_sessies():
    student_id = session.get("user_id")
    geschiedenis = SessieService.get_geschiedenis(student_id)
    chart_data = SessieService.get_geschiedenis_chart(student_id)

    if not geschiedenis:
        geschiedenis = []
    if not chart_data:
        chart_data = []

    totaal_sessies = len(geschiedenis)

    return render_template(
        "main/mijn_sessies.html",
        geschiedenis=geschiedenis,
        chart_data=chart_data,
        totaal_sessies=totaal_sessies,
    )


@bp.route("/docent_home")
@rol_required("docent")
def docent_home():
    """
    Homepagina voor de docent met een overzicht van vandaag.

    Route:
        /docent_home

    Beschrijving:
        Haalt via DocentHome de check-ins van vandaag op, de grafiekdata
        voor check-in en check-out, en de eerste drie openstaande anonieme 
        vragen als preview. Alle data wordt doorgegeven aan het template 
        voor weergave op het docenten dashboard.

    Toegang:
        Alleen toegankelijk voor gebruikers met de rol 'docent' via @rol_required.

    Returns:
        Response: Render van 'main/docent_home.html' met checkins, 
        grafiekdata en vraag preview.
    """
    vragen = DocentHome.get_vragen_preview()

    return render_template(
        "main/docent_home.html",
        checkins=DocentHome.get_vandaag_checkins(),
        aantal_open_vragen=vragen['aantal'],  
        preview_vragen=vragen['preview'],
        in_chart_data=DocentHome.get_checkin_chart(),
        checkout_data=DocentHome.get_checkout_chart()
    )

#OUDER PORTAL
@bp.route("/ouder_home")
@rol_required("ouder")
def ouder_home():
    service = OuderService(session.get("user_id"))
    studenten = service.get_gekoppelde_studenten()
    studenten_met_checkins = []
    for student in studenten:
        checkins = service.get_checkins_van_student(student["student_id"])
        studenten_met_checkins.append({
            "student_id": student["student_id"],
            "naam": f"{student['name']} {student['surname']}",
            "checkins": checkins,
        })
    return render_template("main/ouder_home.html", studenten=studenten_met_checkins)


@bp.route("/ouder_ontkoppelen/<int:student_id>", methods=["POST"])
@rol_required("ouder")
def ouder_ontkoppelen(student_id):
    service = OuderService(session.get("user_id"))
    service.ontkoppel_student(student_id)
    flash("Kind ontkoppeld.", "success")
    return redirect(url_for("main.ouder_home"))


@bp.route("/ouder_koppelen", methods=["GET", "POST"])
@rol_required("ouder")
def ouder_koppelen():
    if request.method == "POST":
        student_email = request.form.get("student_email", "").strip()
        service = OuderService(session.get("user_id"))
        if service.koppel_student_via_email(student_email):
            flash(f"Kind gekoppeld.", "success")
            return redirect(url_for("main.ouder_home"))
        flash("Geen leerling gevonden.", "warning")
    return render_template("main/ouder_koppelen.html")

 

@bp.route("/stel-vraag", methods=["POST"])
def ask_question():
    """Verwerkt een ingediende anonieme vraag van een leerling en slaat deze op in de database."""
    vraag = request.form.get("vraag", "").strip()
    student_id = session.get("user_id") 
    
    if vraag:
        service = QuestionService()
        service.insert_question(vraag, student_id) 
        flash("Je vraag is succesvol verzonden!", "success")
    else:
        flash("De vraag mag niet leeg zijn.", "warning")
        
    return redirect(url_for("main.sessie"))


@bp.route("/vragen-overzicht")
@login_required
def questions_overview():
    """
    Toont een overzicht van alle beantwoorde vragen. 
    Zorgt er ook voor dat openstaande notificaties voor leerlingen automatisch als gelezen worden gemarkeerd.
    """
    service = QuestionService()
    user_id = session.get("user_id") 
    
    if session.get("rol") == "leerling":
        service.mark_all_as_read(user_id)

    beantwoorde_vragen = service.get_answered_questions(user_id)
    
    if not isinstance(beantwoorde_vragen, list):
        beantwoorde_vragen = []
        
    return render_template("main/vragen_overzicht.html", vragen=beantwoorde_vragen, current_user_id=user_id)


@bp.route("/vragen-beantwoorden")
@login_required
def manage_questions():
    """Toont de beheerpagina waar docenten alle openstaande vragen kunnen inzien en beheren."""
    if session.get("rol") != "docent":
        flash("Toegang geweigerd.", "warning")
        return redirect(url_for("main.index"))
    
    service = QuestionService()
    open_vragen = service.get_open_questions()
    
    if not isinstance(open_vragen, list):
        open_vragen = []
        
    return render_template("main/vragen_beantwoorden.html", open_vragen=open_vragen)


@bp.route("/beantwoord-vraag/<int:vraag_id>", methods=["POST"])
@login_required
def submit_answer(vraag_id):
    """Verwerkt het ingevulde antwoord van een docent en werkt de status van de vraag bij in de database."""
    if session.get("rol") != "docent":
        return redirect(url_for("main.index"))

    antwoord = request.form.get("antwoord")
    if antwoord:
        service = QuestionService()
        service.answer_question(vraag_id, antwoord)
        flash("Vraag is succesvol beantwoord!", "success")
        
    return redirect(url_for("main.manage_questions"))


@bp.context_processor
def inject_notifications():
    """
    Context processor die automatisch ongelezen notificaties ophaalt voor ingelogde leerlingen, 
    zodat deze globaal op elke pagina (bijv. in de navigatiebalk) getoond kunnen worden.
    """
    notificaties = []
    if session.get("rol") == "leerling" and session.get("user_id"):
        service = QuestionService()
        notificaties = service.get_unread_notifications(session.get("user_id"))
    
    return dict(notificaties=notificaties)


@bp.route("/verwijder-vraag/<int:vraag_id>", methods=["POST"])
@login_required
def remove_question(vraag_id):
    """Verwijdert een specifieke anonieme vraag definitief uit het systeem."""
    if session.get("rol") != "docent":
        return redirect(url_for("main.index"))

    service = QuestionService()
    service.delete_question(vraag_id)
    flash("Vraag is verwijderd.", "info")
    
    return redirect(url_for("main.manage_questions"))