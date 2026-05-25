
"""Entry point for Flask application"""

from flask import Flask, render_template

from app.events import bp as events_bp
from app.main.routes import bp as main_bp   

def create_app():
    app = Flask(__name__)
    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
    app.config["SECRET_KEY"] = "DokkiePythoniAXRvULKWuFyfURRrG0YTOOTXswLJWpU"

    app.config.from_pyfile("settings.py")

    app.register_blueprint(main_bp)   
    app.register_blueprint(events_bp, url_prefix="/events")

    #404 error handling
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("main/404.html")
    return app

