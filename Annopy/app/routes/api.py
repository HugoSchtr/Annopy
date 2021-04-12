from flask_login import login_required
from flask import request, jsonify
from urllib.parse import urlencode

from ..app import app
from ..constantes import API_ROUTE
from ..modeles.data import *

"""
Routes pour l'API, dans l'ordre:
/api/collection/<int:collection_id>
/api/image/<int:image_id>
/api/collections
"""


def json_404():
    """ Gère les erreurs 404 pour l'API.

    :return: HTTP response
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
        # L'objet récupéré est stocké dans la variable query.
        query = Collection.query.get(collection_id)
        # On exécute la fonction to_json_api() définie dans data.py pour la class Collection à query.
        # On convertit la réponse de la fonction au format JSON avec la fonction jsonify().
        return jsonify((query.to_json_api()))
    except:
        # S'il y a une erreur, si la collection n'existe pas, on lance une erreur HTTP 404.
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
        # L'objet récupéré est stocké dans la variable query.
        query = Image.query.get(image_id)
        # On exécute la fonction to_json_api() définie dans data.py pour la class Image à query.
        # On convertit la réponse de la fonction au format JSON avec la fonction jsonify().
        return jsonify((query.to_json_api()))
    except:
        # S'il y a une erreur, si l'image n'existe pas, on lance une erreur HTTP 404.
        return json_404()


@app.route(API_ROUTE+"/collections")
def api_collections_browse():
    """ Route permettant d'avoir le résultat d'une recherche dans les collections via l'API

    :return: données au format JSON
    """

    # q est ici utilisé comme paramètre pour la recherche.
    keyword = request.args.get("q", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    if keyword:
        query = Collection.query.filter(
            Collection.collection_name.like("%{}%".format(keyword))
        )
    else:
        # S'il n'y a pas de mot-clé pour la recherche, on renvoie toutes les collections présentes en base.
        query = Collection.query

    try:
        resultats = query.paginate(page=page, per_page=5)
    except Exception:
        return json_404()

    # On formate les données récupérées.
    dict_resultats = {
        "links": {
            "self": request.url
        },
        "data": [
            collection.to_json_api()
            for collection in resultats.items
        ]
    }

    # On pagine la recherche.
    if resultats.has_next:
        arguments = {
            "page": resultats.next_num
        }
        if keyword:
            arguments["q"] = keyword
        dict_resultats["links"]["next"] = url_for("api_collections_browse", _external=True)+"?"+urlencode(arguments)

    if resultats.has_prev:
        arguments = {
            "page": resultats.prev_num
        }
        if keyword:
            arguments["q"] = keyword
        dict_resultats["links"]["prev"] = url_for("api_collections_browse", _external=True)+"?"+urlencode(arguments)

    # On convertit les données formatées en JSON.
    response = jsonify(dict_resultats)
    return response
