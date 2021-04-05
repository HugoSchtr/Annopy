from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required

from ..app import app
from ..modeles.data import *
from app.img_extractors.flickr_api_extractor import photoset_flickr_query
from app.img_extractors.iiif_extractor import ark_query


@app.route("/create_collection")
@login_required
def create_collection():
    return render_template("pages/create_collection.html")


@app.route("/create_collection_flickr_api", methods=["POST", "GET"])
@login_required
def create_collection_with_flickr():
    categories = Category.query.all()
    # On récupère toutes les catégories pour les afficher sur le template
    if request.method == "POST":
        chosen_category = request.form.get("collection_category")
        # On récupère la catégorie entrée par l'utilsiateur.ice sur le template
        api_key = request.form.get("api_key", None)
        album_id = request.form.get("album_id", None)
        flickr_user_id = request.form.get("user_id", None)
        if not api_key:
            flash("Il manque des informations pour récupérer les images depuis Flickr.", "error")
            return redirect("/create_collection_flickr_api")
        if not album_id:
            flash("Il manque des informations pour récupérer les images depuis Flickr.", "error")
            return redirect("/create_collection_flickr_api")
        if not flickr_user_id:
            flash("Il manque des informations pour récupérer les images depuis Flickr.", "error")
            return redirect("/create_collection_flickr_api")

        imgs_url = photoset_flickr_query(api_key, album_id, flickr_user_id)

        if not imgs_url:
            flash(
                "Il y a eu une erreur dans la récupération des images via l'API Flickr, vérifiez les informations fournies.",
                "error")
            return redirect("/create_collection_flickr_api")

        category_check = Category.query.filter(Category.name.like("%" + chosen_category + "%")).count()
        if category_check == 0:
            flash("Vous n'avez pas entré de catégorie ou celle-ci n'existe pas.", "error")
            return redirect("/create_collection_flickr_api")
        else:
            category = Category.query.filter(Category.name.like("%" + chosen_category + "%")).first()
            # Une fois le formulaire envoyée en méthode POST, on vérifie que la catégorie choisie existe.
            # Si elle n'existe pas, la fonction retourne un message d'erreur avec flash().
            # Si elle existe, on récupère l'objet correspondant dans la base de données.

            status, data = Collection.create(
                collection_name=request.form.get("collection_name", None),
                collection_description=request.form.get("collection_description", None)
            )
            # Si la catégorie existe, on lance la création de la collection avec la static method Collection.create().

            if status is False:
                flash("Erreur : " + ", ".join(data), "error")
                return render_template("pages/create_collection_with_flickr.html", categories=categories)

            collection = Collection.query.order_by(Collection.collection_id.desc()).limit(1).first()
            # On récupère la dernière collection en base, celle qui vient d'être créée.

            authorship = AuthorshipCollection(
                collection=collection,
                user=current_user
            )
            db.session.add(authorship)
            db.session.commit()
            # On associe l'utilisateur à la collection qu'il vient de créer avec la table AuthorshipCollection.

            collection_has_categories = CollectionHasCategories(
                collection=collection,
                category=category
            )
            db.session.add(collection_has_categories)
            db.session.commit()
            # On associe la collection à la catégorie choisie par l'utilisateur.ice.

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
                flash("Collection créée avec succès, vous pouvez dès à présent lui ajouter des images", "success")
                return redirect("/")
    return render_template("pages/create_collection_with_flickr.html", categories=categories)


@app.route("/create_collection_iiif", methods=["POST", "GET"])
@login_required
def create_collection_with_iiif():
    categories = Category.query.all()
    # On récupère toutes les catégories pour les afficher sur le template

    if request.method == "POST":
        chosen_category = request.form.get("collection_category")
        # On récupère la catégorie entrée par l'utilsiateur.ice sur le template
        manifest_iiif = request.form.get("manifest_iiif", None)
        from_f = request.form.get("from_f", None)
        from_f = int(from_f)
        to_f = request.form.get("to_f", None)
        to_f = int(to_f) # Problème de conversion
        if not manifest_iiif:
            flash("Il manque des informations pour récupérer les images.")
            return redirect("/create_collection_iiif", "error")
        if not from_f:
            flash("Il manque des informations pour récupérer les images.")
            return redirect("/create_collection_iiif", "error")
        if not to_f:
            flash("Il manque des informations pour récupérer les images.")
            return redirect("/create_collection_iiif", "error")

        imgs_url = ark_query(manifest_iiif, from_f, to_f)

        if not imgs_url:
            flash(
                "Il y a eu une erreur dans la récupération des images. Il se peut que votre lien soit invalide, que le serveur que vous essayez de consulter est indisponible, que le manifest IIIF n'est pas libre de droits, ou que vous n'ayez pas entré d'entiers pour l'intervalle.",
                "error")
            return redirect("/create_collection_iiif")

        category_check = Category.query.filter(Category.name.like("%" + chosen_category + "%")).count()
        if category_check == 0:
            flash("Vous n'avez pas entré de catégorie ou celle-ci n'existe pas.", "error")
            return redirect("/create_collection_iiif")
        else:
            category = Category.query.filter(Category.name.like("%" + chosen_category + "%")).first()
            # Une fois le formulaire envoyée en méthode POST, on vérifie que la catégorie choisie existe.
            # Si elle n'existe pas, la fonction retourne un message d'erreur avec flash().
            # Si elle existe, on récupère l'objet correspondant dans la base de données.

            status, data = Collection.create(
                collection_name=request.form.get("collection_name", None),
                collection_description=request.form.get("collection_description", None)
            )
            # Si la catégorie existe, on lance la création de la collection avec la static method Collection.create().

            if status is False:
                flash("Erreur : " + ", ".join(data), "error")
                return render_template("pages/create_collection_with_iiif.html", categories=categories)

            collection = Collection.query.order_by(Collection.collection_id.desc()).limit(1).first()
            # On récupère la dernière collection en base, celle qui vient d'être créée.

            authorship = AuthorshipCollection(
                collection=collection,
                user=current_user
            )
            db.session.add(authorship)
            db.session.commit()
            # On associe l'utilisateur à la collection qu'il vient de créer avec la table AuthorshipCollection.

            collection_has_categories = CollectionHasCategories(
                collection=collection,
                category=category
            )
            db.session.add(collection_has_categories)
            db.session.commit()
            # On associe la collection à la catégorie choisie par l'utilisateur.ice.

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
                flash("Collection créée avec succès, vous pouvez dès à présent lui ajouter des images", "success")
                return redirect("/")
    return render_template("pages/create_collection_with_iiif.html", categories=categories)


@app.route("/collection/<int:collection_id>/update", methods=["POST", "GET"])
@login_required
def collection_update(collection_id):
    collection = Collection.query.get(collection_id)

    if request.method == "POST":
        collection_name = request.form.get("collection_name", None)
        collection_description = request.form.get("collection_description", None)
        if collection_name:
            collection.collection_name = request.form.get("collection_name", None)
        if collection_description:
            collection.collection_description = request.form.get("collection_description", None)

        db.session.add(collection)
        db.session.commit()

    return render_template("pages/collection_update.html", collection=collection)


@app.route("/create_category", methods=["POST", "GET"])
@login_required
def create_category():
    categories = Category.query.all()
    if request.method == "POST":
        status, data = Category.create(
            category_name=request.form.get("category_name", None),
        )
        if status is True:
            flash("Catégorie ajoutée avec succès", "success")
            return redirect("/create_collection")
        else:
            flash("Erreur : " + ", ".join(data), "error")
            return render_template("/pages/create_category.html", categories=categories)
    return render_template("pages/create_category.html", categories=categories)


@app.route("/delete_collection/<int:collection_id>")
def delete_collection(collection_id):
    collection = Collection.query.get(collection_id)
    if collection is None:
        return render_template("errors/404.html"), 404
    db.session.delete(collection)
    db.session.commit()
    flash("'{}' a bien été supprimée.".format(collection.collection_name), "success")
    return redirect("/")


@app.route("/recherche")
def search():
    keyword = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    results = []

    if keyword:
        results = Collection.query.filter(
            Collection.collection_name.like("%{}%".format(keyword))
        ).paginate(page=page, per_page=5)
        titre = "Résultat pour la recherche `" + keyword + "`"

    return render_template("pages/search.html", results=results, titre=titre)


@app.route("/browse_collection")
def browse_collection():
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    resultats = Collection.query.paginate(page=page, per_page=5)

    return render_template("pages/browse_collections.html", resultats=resultats)


@app.route("/collection/<int:collection_id>")
def collection(collection_id):
    collection = Collection.query.get(collection_id)
    if collection is None:
        return render_template("errors/404.html"), 404
    authorships = Collection.query.get(collection_id).collection_authorship
    categories = Collection.query.get(collection_id).has_categories
    imgs = Collection.query.get(collection_id).has_images
    if current_user.is_authenticated is True:
        for img in imgs:
            annotations = img.image.annotation
            print(annotations)

    if current_user.is_authenticated is not True:
        flash("Vous devez vous connecter pour pouvoir voir et annoter les images de cette collection.", 'info')
    return render_template("pages/collection.html", collection=collection, authorships=authorships,
                           categories=categories, imgs=imgs, Annotation=Annotation, AuthorshipAnnotation=AuthorshipAnnotation, db=db)


@app.route("/viewer/collection/<int:collection_id>/image/<int:image_id>", methods=['POST', 'GET'])
@login_required
def viewer(collection_id, image_id):
    img = Image.query.get(image_id)
    img_id = img.image_id
    if img is None:
        return render_template("errors/404.html"), 404
    img_has_collection = Image.query.get(img.image_id).has_collection
    for info in img_has_collection:
        collection_id = info.collection.collection_id

    if request.method == 'POST':
        annotations = request.json
        if annotations:
            img = Image.query.get(image_id)
            for annotation in annotations:
                annotation_to_be_added = Annotation(
                    annotation_json=str(annotation),
                    image=img
                )

                db.session.add(annotation_to_be_added)
                db.session.commit()

                new_annotation = Annotation.query.order_by(Annotation.annotation_id.desc()).limit(1).first()

                authorship_annotation = AuthorshipAnnotation(
                    user=current_user,
                    annotation=new_annotation
                )
                db.session.add(authorship_annotation)
                db.session.commit()
# trouver moyen de dire quand il n'y a pas d'annotation de créé
        flash("l'annotation a bien été enregistrée !", "success")
        return redirect("/collection/" + str(collection_id))

    return render_template("pages/viewer_annotations.html", img=img, img_id=img_id, collection_id=collection_id)
