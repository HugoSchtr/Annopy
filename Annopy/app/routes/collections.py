from flask import render_template, request, flash, redirect, json
from flask_login import current_user, login_required

from ..app import app
from ..modeles.data import *
from ..img_extractors.flickr_api_extractor import photoset_flickr_query
from ..img_extractors.iiif_extractor import iiif_query

"""
Routes gérant les collections dans l'app:
Dans l'ordre : 
/create_collection
/create_collection_flickr_api
/create_collection_iiif
/collection/<int:collection_id>/update
/create_category
/delete_collection/<int:collection_id>
/search
/browse_collections
/collection/<int:collection_id>
/viewer/collection/<int:collection_id>/image/<int:image_id>
"""


@app.route("/create_collection")
@login_required
def create_collection():
    """ Route permettant à l'utilisateur-ice de choisir comment il/elle souhaite créer une collection
    Deux choix possibles : avec IIIF ou avec Flickr.
    L'utilisateur-ice doit être connecté-e pour accéder à cette page.

    :return: create_collection.html
    :rtype: template
    """

    return render_template("pages/create_collection.html")


@app.route("/create_collection_flickr_api", methods=["POST", "GET"])
@login_required
def create_collection_with_flickr():
    """ Route permettant la création d'une collection avec l'API de Flickr

    :return: create_collection_with_flickr.html
    :rtype: template
    """
    # On récupère toutes les catégories pour les afficher sur le template
    categories = Category.query.all()

    # Si la requête HTTP est POST, on crée une collection
    if request.method == "POST":
        # On récupère la catégorie entrée par l'utilisateur-ice sur le template
        chosen_category = request.form.get("collection_category")
        # On récupère les éléments nécessaires pour faire une requête à l'API Flickr
        # La API key, fournie par Flickr aux utilisateurs demandant un accès à l'API
        # L'ID de l'album, qui correspond à l'identifiant d'un album créé par un-e utilisateur-ice sur Flickr
        # L'user ID Flickr, qui correspond à l'identifiant de l'utilisateur-ice à qui appartient l'album
        api_key = request.form.get("api_key", None)
        album_id = request.form.get("album_id", None)
        flickr_user_id = request.form.get("user_id", None)
        # S'il manque les informations nécessaires (valeur des variables précédentes = None),
        # on alerte l'utilisateur-ice qu'il manque des informations nécessaires.
        if not api_key:
            flash("Il manque des informations pour récupérer les images depuis Flickr.", "error")
            return redirect("/create_collection_flickr_api")
        if not album_id:
            flash("Il manque des informations pour récupérer les images depuis Flickr.", "error")
            return redirect("/create_collection_flickr_api")
        if not flickr_user_id:
            flash("Il manque des informations pour récupérer les images depuis Flickr.", "error")
            return redirect("/create_collection_flickr_api")

        # Si tous les paramètres nécessaires à la fonction photoset_flickr_query sont présents,
        # on stocke la liste d'URL dans imgs_url
        url_query, imgs_url = photoset_flickr_query(api_key, album_id, flickr_user_id)

        # Il est possible qu'il y ait une erreur lors de la récupération des images
        # (API key erronée, user ID inexistant, etc.). Dans ce cas, on envoie un message d'erreur avec flash() et
        # on redirige l'utilisateur-ice vers un nouveau formulaire de création.
        if not imgs_url:
            flash(
                "Il y a eu une erreur dans la récupération des images via l'API Flickr, vérifiez les informations fournies.",
                "error")
            return redirect("/create_collection_flickr_api")

        # On fait une recherche filtrée pour récupérer la catégorie choisie par l'utilisateur-ice.
        # ("%" + chosen_category + "%") permet de donner de la souplesse à ce système en le rendant insensible
        # à la casse.
        category_check = Category.query.filter(Category.name.like("%" + chosen_category + "%")).count()
        # Si la requête n'a pas compté de catégorie semblable, cela signifie que la catégorie n'existe pas.
        # La création de collection est impossible.
        # On envoie un message au template avec flash() pour informer l'utilisateur-ice.
        if category_check == 0:
            flash("Vous n'avez pas entré de catégorie ou celle-ci n'existe pas.", "error")
            return redirect("/create_collection_flickr_api")
        # S'il y a au moins un résultat, on fait une nouvelle requête et on stocke le premier objet donné par la
        # requête dans category.
        else:
            category = Category.query.filter(Category.name.like("%" + chosen_category + "%")).first()

            # On lance la création de la nouvelle collection avec la méthode .create()
            status, data = Collection.create(
                collection_name=request.form.get("collection_name", None),
                collection_description=request.form.get("collection_description", None),
                collection_source=url_query
            )

            # On arrête le processus de création de collection si la méthode a retourné False.
            if status is False:
                flash("Erreur : " + ", ".join(data), "error")
                return render_template("pages/create_collection_with_flickr.html", categories=categories)

            # On récupère la dernière collection en base, celle qui vient d'être créée.
            collection = Collection.query.order_by(Collection.collection_id.desc()).limit(1).first()

            # On associe l'utilisateur-ice à la collection qu'il/elle vient de créer avec la table AuthorshipCollection.
            authorship = AuthorshipCollection(
                collection=collection,
                user=current_user
            )
            db.session.add(authorship)
            db.session.commit()

            # On associe la collection à la catégorie choisie par l'utilisateur.ice.
            collection_has_categories = CollectionHasCategories(
                collection=collection,
                category=category
            )
            db.session.add(collection_has_categories)
            db.session.commit()

            # On itère sur les URL contenues dans imgs_url pour les stocker en base.
            # Cela servira à les afficher lorsqu'il sera question de les annoter.
            for url in imgs_url:
                Image.create(
                    image_url=url
                )

                img = Image.query.order_by(Image.image_id.desc()).limit(1).first()

                collection_has_images = CollectionHasImages(
                    collection=collection,
                    image=img
                )

                db.session.add(collection_has_images)
                db.session.commit()

            if status is True:
                flash("Collection créée avec succès, vous pouvez dès à présent commencer l'annotation", "success")
                return redirect("/")
    return render_template("pages/create_collection_with_flickr.html", categories=categories)


@app.route("/create_collection_iiif", methods=["POST", "GET"])
@login_required
def create_collection_with_iiif():
    """ Route permettant la création d'une collection à l'aide d'un manifest IIIF

    :return: create_collection_with_iiif.html
    :rtype: template
    """
    # On récupère toutes les catégories pour les afficher sur le template
    categories = Category.query.all()

    # Si la requête HTTP est POST, on crée une collection
    if request.method == "POST":
        # On récupère la catégorie entrée par l'utilisateur-ice sur le template
        chosen_category = request.form.get("collection_category")
        # On récupère les éléments nécessaires pour récupérer les URL des images depuis un manifest IIIF
        # avec la fonction ark_query.
        # manfifest_iiif est un lien renvoyant vers un manifest IIIF (JSON)
        # from_f est un chiffre indiquant depuis quelle image l'intervalle débute
        # to_f est un chiffre indiquant à quelle image l'intervalle se termine
        # La fonction permettra de récupérer les URL des images se trouvant dans l'intervalle
        manifest_iiif = request.form.get("manifest_iiif", None)
        from_f = request.form.get("from_f", None)
        to_f = request.form.get("to_f", None)
        # S'il manque les informations nécessaires (valeur des variables précédentes = None),
        # on alerte l'utilisateur-ice qu'il manque des informations nécessaires.
        if not manifest_iiif:
            flash("Il manque des informations pour récupérer les images.")
            return redirect("/create_collection_iiif", "error")
        if not from_f:
            flash("Il manque des informations pour récupérer les images.")
            return redirect("/create_collection_iiif", "error")
        if not to_f:
            flash("Il manque des informations pour récupérer les images.")
            return redirect("/create_collection_iiif", "error")

        # Si tous les paramètres nécessaires à la fonction iiif_query sont présents,
        # on stocke la liste d'URL dans imgs_url
        imgs_url = iiif_query(manifest_iiif, from_f, to_f)

        # Il est possible qu'il y ait une erreur lors de la récupération des images
        # (lien invalide, serveur iiif indisponible, manifest non libre de droits, pas d'entiers pour l'intervalle).
        # Dans ce cas, on envoie un message d'erreur avec flash() et
        # on redirige l'utilisateur-ice vers un nouveau formulaire de création.
        if not imgs_url:
            flash(
                "Il y a eu une erreur dans la récupération des images. Il se peut que votre lien soit invalide, que le serveur que vous essayez de consulter est indisponible, que le manifest IIIF n'est pas libre de droits, ou que vous n'ayez pas entré d'entiers pour l'intervalle.",
                "error")
            return redirect("/create_collection_iiif")

        # On fait une recherche filtrée pour récupérer la catégorie choisie par l'utilisateur-ice.
        # ("%" + chosen_category + "%") permet de donner de la souplesse à ce système en le rendant insensible
        # à la casse.
        category_check = Category.query.filter(Category.name.like("%" + chosen_category + "%")).count()
        # Si la requête n'a pas compté de catégorie semblable, cela signifie que la catégorie n'existe pas.
        # La création de collection est impossible.
        # On envoie un message au template avec flash() pour informer l'utilisateur-ice.
        if category_check == 0:
            flash("Vous n'avez pas entré de catégorie ou celle-ci n'existe pas.", "error")
            return redirect("/create_collection_iiif")
        # S'il y a au moins un résultat, on fait une nouvelle requête et on stocke le premier objet donné par la
        # requête dans category.
        else:
            category = Category.query.filter(Category.name.like("%" + chosen_category + "%")).first()

            # On lance la création de la nouvelle collection avec la méthode .create()
            status, data = Collection.create(
                collection_name=request.form.get("collection_name", None),
                collection_description=request.form.get("collection_description", None),
                collection_source=manifest_iiif
            )

            # On arrête le processus de création de collection si la méthode a retourné False.
            if status is False:
                flash("Erreur : " + ", ".join(data), "error")
                return render_template("pages/create_collection_with_iiif.html", categories=categories)

            # On récupère la dernière collection en base, celle qui vient d'être créée.
            collection = Collection.query.order_by(Collection.collection_id.desc()).limit(1).first()

            # On associe l'utilisateur à la collection qu'il vient de créer avec la table AuthorshipCollection.
            authorship = AuthorshipCollection(
                collection=collection,
                user=current_user
            )
            db.session.add(authorship)
            db.session.commit()

            # On associe la collection à la catégorie choisie par l'utilisateur.ice.
            collection_has_categories = CollectionHasCategories(
                collection=collection,
                category=category
            )
            db.session.add(collection_has_categories)
            db.session.commit()

            # On itère sur les URL contenues dans imgs_url pour les stocker en base.
            # Cela servira à les afficher lorsqu'il sera question de les annoter.
            for url in imgs_url:
                Image.create(
                    image_url=url
                )

                img = Image.query.order_by(Image.image_id.desc()).limit(1).first()

                collection_has_images = CollectionHasImages(
                    collection=collection,
                    image=img
                )

                db.session.add(collection_has_images)
                db.session.commit()

            if status is True:
                flash("Collection créée avec succès, vous pouvez dès à présent commencer l'annotation", "success")
                return redirect("/")
    return render_template("pages/create_collection_with_iiif.html", categories=categories)


@app.route("/collection/<int:collection_id>/update", methods=["POST", "GET"])
@login_required
def collection_update(collection_id):
    """ Route permettant de mettre à jour une collection

    :param collection_id: ID de la collection que l'utilisateur-ice souhaite mettre à jour
    :return: collection_update.html
    :type: template
    """

    # On récupère la collection souhaitée à l'aide de son ID et d'une query à la table Collection
    # On stocke l'objet dans collection
    collection = Collection.query.get(collection_id)

    # Si la méthode HTTP est POST, alors le formulaire HTML a été envoyée et la collection doit être mise à jour
    if request.method == "POST":
        # On récupère le nouveau nom de la collection, s'il y en a un
        collection_name = request.form.get("collection_name", None)
        # On récupère la nouvelle description de la collection, s'il y en a une
        collection_description = request.form.get("collection_description", None)
        # Les deux if suivants permettent de vérifier si collection_name et collection_description ne sont pas None.
        # Si l'un des deux n'est pas none, on modifie la donnée en base en fonction de celui-ci
        # Cela permet de changer le nom ou la description sans effacer l'un ou l'autre
        # si on ne modifie pas les deux informations en même temps.
        if collection_name:
            collection.collection_name = request.form.get("collection_name", None)
        if collection_description:
            collection.collection_description = request.form.get("collection_description", None)

        # On ajoute l'utilisateur-ice courant au transport vers la base de données
        db.session.add(collection)
        # On commit
        db.session.commit()

    return render_template("pages/collection_update.html", collection=collection)


@app.route("/create_category", methods=["POST", "GET"])
@login_required
def create_category():
    """ Route permettant de créer une nouvelle catégorie

    :return: create_category.html
    :rtype: template
    """

    # On récupère toutes les catégories présentes en table pour les afficher sur le template
    categories = Category.query.all()
    # Si la méthode HTTP est POST, alors le formulaire a été postée et une nouvelle catégorie doit être ajoutée
    if request.method == "POST":
        # On utilise la méthode create de la classe Category pour créer la nouvelle catégorie
        status, data = Category.create(
            category_name=request.form.get("category_name", None),
        )
        # Si la méthode retourne True, on envoie un message au template avec flash()
        if status is True:
            flash("Catégorie ajoutée avec succès", "success")
            return redirect("/create_collection")
        else:
            # Si la méthode retourne False, on envoie un message au template avec flash() avec les erreurs
            flash("Erreur : " + ", ".join(data), "error")
            return render_template("/pages/create_category.html", categories=categories)
    return render_template("pages/create_category.html", categories=categories)


@app.route("/delete_collection/<int:collection_id>")
@login_required
def delete_collection(collection_id):
    """ Route permettant de supprimer une collection

    :param collection_id: ID de la collection que l'on souhaite supprimer
    :return: /
    :rtype: response object
    """
    collection = Collection.query.get(collection_id)
    if collection is None:
        return render_template("errors/404.html"), 404
    db.session.delete(collection)
    db.session.commit()
    flash("'{}' a bien été supprimée.".format(collection.collection_name), "success")
    return redirect("/")


@app.route("/search")
def search():
    """ Route permettant de rechercher une collection

    :return: search.html
    :rtype: template
    """
    # On récupère le mot-clé envoyé par l'utilisateur-ice avec la méthode HTTP GET via le template.
    keyword = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    results = []

    # Si l'utilisateur-ice a entré un terme de recherche, on exécute une requête filtrée par ledit terme
    if keyword:
        # On pagine la requête
        results = Collection.query.filter(
            Collection.collection_name.like("%{}%".format(keyword))
        ).paginate(page=page, per_page=5)
        titre = "Résultat pour la recherche `" + keyword + "`"
        return render_template("pages/search.html", results=results, titre=titre)
    # Autrement, on redirige l'utilisateur-ice vers l'accueil en l'informant qu'il n'y avait rien à rechercher
    else:
        flash("Vous n'avez entré aucun terme pour la recherche", "info")
        return render_template("pages/index.html")


@app.route("/browse_collections")
def browse_collections():
    """ Route permettant de naviguer à travers les collections

    :return: browse_collections.html
    :rtype: template
    """
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    # On pagine les objets présents en table Collection
    resultats = Collection.query.paginate(page=page, per_page=5)

    return render_template("pages/browse_collections.html", resultats=resultats)


@app.route("/collection/<int:collection_id>")
def collection(collection_id):
    """ Route permettant d'afficher une collection et ses données.
    Depuis cette route, l'utilisateur-ice peut interagir avec les images de la collection.

    - Annoter les images de la collection
    - Récupérer les données des images de la collection
    - Récupérer les données de la collection (authorship, image(s), annotation(s))
    - Modifier la collection
    - Supprimer la collection

    :param collection_id: ID de la collection consultée
    :return: collection.html
    :rtype: template
    """
    # On récupère la collection que l'utilisateur-ice souhaite consulter avec l'ID
    collection = Collection.query.get(collection_id)
    # Si la collection n'existe pas, erreur 404
    if collection is None:
        return render_template("errors/404.html"), 404
    # On récupère l'association entre User et la Collection
    authorships = Collection.query.get(collection_id).collection_authorship
    # On récupère l'association entre Category et Collection
    categories = Collection.query.get(collection_id).has_categories
    # On récupère l'association entre Collection et Image
    imgs = Collection.query.get(collection_id).has_images

    # On informe l'utilisateur-ice non connecté-e qu'il/elle ne peut pas interagir avec les images en étant déconnecté-é
    if current_user.is_authenticated is not True:
        flash("Vous devez vous connecter pour pouvoir voir et annoter les images de cette collection.", 'info')

    return render_template("pages/collection.html", collection=collection, authorships=authorships,
                           categories=categories, imgs=imgs, Annotation=Annotation, AuthorshipAnnotation=AuthorshipAnnotation, db=db)


@app.route("/viewer/collection/<int:collection_id>/image/<int:image_id>", methods=['POST', 'GET'])
@login_required
def viewer(collection_id, image_id):
    """ Route permettant d'annoter une image d'une collection

    :param collection_id: ID de la collection qui contient l'image que l'utilisateur-ice annote
    :param image_id: ID de l'image que l'utilisateur-ice annote
    :return: viewer_annotations.html
    :rtype: template
    """

    # On récupère les annotations de l'image que l'utilisateur-ice souhaite annoter, s'il y en a déjà
    imgs_annotations = Image.query.get(image_id).annotation
    # Si des annotations ont été récupérées, on vérifie que l'utilisateur-ice courrant-e n'est pas à l'origine
    # de ces annotations
    if imgs_annotations:
        for annotation in imgs_annotations:
            check = AuthorshipAnnotation.query.filter(db.and_(
                AuthorshipAnnotation.authorship_annotation_annotation_id == annotation.annotation_id,
                AuthorshipAnnotation.authorship_annotation_user_id == current_user.user_id)
                ).first()
            # Si la requete précédente a renvoyé un objet, alors l'utilisateur-ice a déjà annoté l'image
            # la variable check, dans ce cas, est True
            # On redirige l'utilisateur-ice vers la collection en lui indiquant qu'il/elle a déjà annoté l'image
            if check:
                flash("Vous avez déjà annoté l'image que vous essayez de consulter.", 'info')
                return redirect("/collection/" + str(collection_id))
            # Avec ce système, une utilisateur-ice ne peut annoter une image qu'une seule fois

    # On récupère l'image qui va être annotée avec son ID
    img = Image.query.get(image_id)
    # Si la requête renvoie None, alors l'image n'existe pas en base
    # On informe l'utilisateur-ice avec une erreur 404
    if img is None:
        return render_template("errors/404.html"), 404
    # On récupère la collection de l'image grâce à l'association
    img_has_collection = Image.query.get(img.image_id).has_collection
    for info in img_has_collection:
        # On récupère l'ID de la collection qui contient l'image
        # Cela servira à rediriger l'utilisateur-ice une fois les annotations envoyées au serveur
        collection_id = info.collection.collection_id

    # Si la méthode HTTP est POST, alors l'utilisateur-ice a envoyé ses annotations et la requête AJAX a été lancée
    if request.method == 'POST':
        # on récupère les annotations envoyées avec la requete AJAX
        annotations = request.json
        # On vérifie qu'il y a un objet à traiter
        if annotations:
            # La requête AJAX envoie une liste de valeurs, chaque index étant une annotation.
            # Pour enregistrer chaque index dans la liste, on itère dessus.
            for annotation in annotations:
                # On crée l'annotation en lui associant l'image
                annotation_to_be_added = Annotation(
                    # On transforme le dictionnaire annotation en une chaine de caractère formatée JSON
                    annotation_json=json.dumps(annotation),
                    image=img
                )

                # On ajoute l'annotation pour le transport vers la base de données
                db.session.add(annotation_to_be_added)
                # On commit
                db.session.commit()

                # On récupère la dernière annotation créée en base
                new_annotation = Annotation.query.order_by(Annotation.annotation_id.desc()).limit(1).first()

                # On l'associe pour l'authorship avec l'utilisateur-ice courant-e
                authorship_annotation = AuthorshipAnnotation(
                    user=current_user,
                    annotation=new_annotation
                )
                # On ajoute l'authorship pour le transport vers la base de données
                db.session.add(authorship_annotation)
                # On commit
                db.session.commit()
        # On envoie un message au template avec flash(), indiquant que l'annotation a été enregistrée.
        # Ce système possède un bug, non gênant dans le fonctionnement de l'application :
        # le message envoyé avec flash() apparaît quand l'utilisateur-ice a envoyé des annotations au serveur
        # et apparaît également si aucune annotation n'a été envoyée (donc aucun enregistrement en base).
        # La mise en place d'un if côté JavaScript n'a pas fonctionné. Après recherche il est possible que cela
        # est causé par la nature asynchrone de la requête AJAX, que je ne sais pas comment gérer.
        flash("l'annotation a bien été enregistrée !", "success")
        return redirect("/collection/" + str(collection_id))

    return render_template("pages/viewer_annotations.html", img=img, collection_id=collection_id)
