from warnings import warn
import os

# On stocke la secret key
# La secret key est utilisée pour les sessions cookies et d'autres aspects de sécurité
# Elle doit être changée dans le cadre d'un déploiement d'application
SECRET_KEY = "JE SUIS UN SECRET !"
# On stocke la route de l'API
API_ROUTE = "/api"

# On lance un warning dans la console si la secret key n'a pas été changée
if SECRET_KEY == "JE SUIS UN SECRET !":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)


# On configure deux classes pour les deux configurations de l'application.
class _TEST:
    # La class _TEST utilisera une database dédiée à la phase de développement
    SECRET_KEY = SECRET_KEY
    # On configure la base de données
    # sqlite:// indique le moteur utilisé, ici SQLite.
    # / indique qu'on utilise un chemin relatif pour trouver la database
    # db_test.sqlite étant le fichier de la database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db_test.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class _PRODUCTION:
    # La class _TEST utilisera une database dédiée à la phase de production
    SECRET_KEY = SECRET_KEY
    # On configure la base de données
    # sqlite:// indique le moteur utilisé, ici SQLite.
    # / indique qu'on utilise un chemin relatif pour trouver la database
    # db_prod.sqlite étant le fichier de la database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db_prod.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# On stocke les deux classes de configuration dans le dictionnaire CONFIG
# On les réutilisera pour initialiser l'app dans app.py
CONFIG = {
    "test": _TEST,
    "production": _PRODUCTION
}

