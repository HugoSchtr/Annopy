from flask import render_template
from ..app import app


# Routes pour gérer les erreurs HTTP


@app.errorhandler(404)
def not_found(error):
    """ Route pour code de réponse HTTP 404 (Not Found)

    :param error: code d'erreur HTTP
    :return: template 404.html
    :rtype: template
    """
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    """ Route pour code de réponse HTTP 500 (not found) (Internal Server Error)

    :param error: code d'erreur HTTP
    :return: template 500.html
    :rtype: template
    """
    return render_template('errors/500.html'), 500
