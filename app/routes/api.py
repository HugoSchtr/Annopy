from flask import render_template, request, url_for, jsonify
from urllib.parse import urlencode
from flask_login import login_required

from ..app import app
from ..constantes import API_ROUTE
from ..modeles.data import *
from ..modeles.users import User

def Json_404():
    response = jsonify({"erreur": "Unable to perform the query"})
    response.status_code = 404
    return response


@app.route(API_ROUTE+"/collection/<int:collection_id>")
@login_required
def api_collection_data(collection_id):
    try:
        query = Collection.query.get(collection_id)
        return jsonify((query.to_json_api()))
    except:
        return Json_404()


@app.route(API_ROUTE+"/image/<int:image_id>")
@login_required
def api_image_data(image_id):
    try:
        query = Image.query.get(image_id)
        return jsonify((query.to_json_api()))
    except:
        return Json_404()
