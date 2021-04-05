from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .constantes import CONFIG


chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")


db = SQLAlchemy()

login = LoginManager()

app = Flask(
    "Crow",
    template_folder=templates,
    static_folder=statics
)

from .routes import generic, collections, errors, api

def config_app(config_name="test"):
    """ Création de l'application """
    app.config.from_object(CONFIG[config_name])
    app.config['JSON_SORT_KEYS'] = False
    # Set up extensions
    db.init_app(app)
    # assets_env = Environment(app)
    login.init_app(app)

    # Register Jinja template functions

    return app
