from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .constantes import CONFIG


# On stocke le chemin vers le fichier courant dans chemin_actuel
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
# On stocke le chemin du dossier des templates dans templates
templates = os.path.join(chemin_actuel, "templates")
# On stocke le chemin du dossier des statics dans statics
statics = os.path.join(chemin_actuel, "static")

# On initie l'objet SQLAlchemy en le stockant dans la variable db
db = SQLAlchemy()

# On met en place la gestion d'utilisateur-rice-s
login = LoginManager()

# On crée notre application
app = Flask(
    # Nom de l'application
    "Annopy",
    # Chemin du dossier templates
    template_folder=templates,
    # Chemin du dossier statics
    static_folder=statics
)

# On importe les routes
from .routes import generic, collections, errors, api


def config_app(config_name="test"):
    """ Création de l'application

    :param config_name: nom de la configuration choisie pour lancer l'application
    :type config_name: str
    :return: app
    """

    # On initie la configuration de l'application
    # Les configurations sont deux classes, comprises dans le dictionnaire CONFIG, dans constantes.py
    app.config.from_object(CONFIG[config_name])

    # On initie la configuration 'JSON_SORT_KEYS'. False est attribuée à la variable pour contourner le paramètre.
    # De la sorte, Flask n'ordonne pas les clés des dictionnaires.
    # Cela permet d'avoir une réponse de l'API identique au return des fonctions de l'API.
    # Le cas inverse, le JSON est inversé dans le navigateur.
    app.config['JSON_SORT_KEYS'] = False

    # On initialise l'application avec les paramètres préalablement définis.
    db.init_app(app)

    # On configure la gestion des logins
    login.init_app(app)

    return app
