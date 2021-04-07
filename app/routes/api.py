from flask import jsonify
from flask_login import login_required

from ..app import app
from ..constantes import API_ROUTE
from ..modeles.data import *

"""
Routes pour l'API, dans l'ordre:
/api/collection/<int:collection_id>
/api/image/<int:image_id>
"""


def json_404():
    """ Gère les erreurs 404 pour l'API.

    :return: HTML response
    """
    response = jsonify({"erreur": "Unable to perform the query"})
    response.status_code = 404
    return response


@app.route(API_ROUTE+"/collection/<int:collection_id>")
@login_required
def api_collection_data(collection_id):
    """ Route permettant de récupérer toutes les données d'une collection au format JSON.
    La collection est récupérée grâce à son ID.
    Renvoie les données au format JSON de :
    - la collection
    - Les images
    - Les annotations des images

    :param collection_id: ID de la collection recherchée
    :type collection_id: int
    :return: données au format JSON
    """

    try:
        # On fait une query à la base de données pour récupérer une collection selon son ID.
        # L'objet récupéré est stocké dans la variable query
        query = Collection.query.get(collection_id)
        # On exécute la fonction to_json_api() définie dans data.py pour la class Collection à query
        # On convertit la réponse de la fonction au format JSON avec la fonction jsonify()
        return jsonify((query.to_json_api()))
    except:
        # S'il y a une erreur, si la collection n'existe pas, on lance une erreur HTML 404
        return json_404()


@app.route(API_ROUTE+"/image/<int:image_id>")
@login_required
def api_image_data(image_id):
    """ Route permettant de récupérer toutes les données d'une image au format JSON.
    L'image est récupérée grâce à son ID.
    Renvoie les données au format JSON de :
    - L'image
    - Ses annotations

    :param image_id: ID de l'image recherchée
    :type image_id: int
    :return: données au format JSON
    """

    try:
        # On fait une query à la base de données pour récupérer une image selon son ID.
        # L'objet récupéré est stocké dans la variable query
        query = Image.query.get(image_id)
        # On exécute la fonction to_json_api() définie dans data.py pour la class Image à query
        # On convertit la réponse de la fonction au format JSON avec la fonction jsonify()
        return jsonify((query.to_json_api()))
    except:
        # S'il y a une erreur, si l'image n'existe pas, on lance une erreur HTML 404
        return json_404()
