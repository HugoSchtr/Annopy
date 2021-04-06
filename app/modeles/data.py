from flask import url_for
import datetime

from .. app import db

# Création de la table des collections
class Collection(db.Model):
    __tablename__ = "collection"
    collection_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # Le nom d'une collection doit être unique.
    collection_name = db.Column(db.String(45), unique=True, nullable=False)
    collection_description = db.Column(db.Text, nullable=False)
    # jointure avec la table CollectionHasCategories, pour associer une collection à une catégorie.
    # Relation many to many
    has_categories = db.relationship('CollectionHasCategories', back_populates="collection")
    # jointure avec la table AuthorshipCollection, pour associer la création d'une collection à un utilisateur.
    # relation many to many
    # si la collection est supprimée, l'authorship est supprimé avec cascade="all, delete"
    collection_authorship = db.relationship("AuthorshipCollection", back_populates="collection", cascade="all, delete")
    # jointure avec la table CollectionHasImages
    # relation many to many
    # si la collection est supprimée, suppression des images qui lui étaient associées.
    has_images = db.relationship("CollectionHasImages", back_populates="collection", cascade="all, delete")

    @staticmethod
    def create(collection_name, collection_description):
        """ Crée une collection. Retourne un typle (booléen, nouvelle Collection ou liste).
        En cas d'erreur, renvoie False suivi de la liste des erreurs.
        En cas de succès, renvoie True suivi de la donnée enregistrée.

        :param collection_name: nom de la collection
        :type collection_name: str
        :param collection_description: description de la collection
        :type collection_description: str
        :return: tuple (booléen, nouvelle Collection ou liste)
        :rtype: tuple
        """

        # On crée la liste errors qui stockera les erreurs s'il y en a
        errors = []

        # On vérifie qu'il y a un nom de collection et une description.
        # Le cas contraire, on met à jour la liste des erreurs.
        if not collection_name:
            errors.append("Le nom de la collection est manquant.")
        if not collection_description:
            errors.append("La description de la collection est manquante.")

        # Si la liste des erreurs n'est pas vide, renvoie False et la liste d'erreurs.
        if len(errors) > 0:
            return False, errors

        # On vérifie que le nom de la collection n'est pas déjà pris.
        collection_name_check = Collection.query.filter(Collection.collection_name.like("%"+collection_name+"%")).first()
        if collection_name_check:
            errors.append("Une collection porte déjà ce nom : " + collection_name)

        # Si la liste des erreurs n'est pas vide, renvoie False et la liste d'erreurs.
        if len(errors) > 0:
            return False, errors

        # On crée une nouvelle collection
        new_collection = Collection(
            collection_name=collection_name,
            collection_description=collection_description,
        )

        try:
            # On l'ajoute au transport vers la base de données.
            db.session.add(new_collection)
            # On commit
            db.session.commit()

            # On renvoie la nouvelle collection
            return True, new_collection
        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        """ Retourne l'ID de l'objet actuellement utilisé

        :return: ID de la collection
        :rtype: int
        """
        return self.collection_id

    def to_json_api(self):
        """ Retourne les données de la collection sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de la collection
        :rtype: dict
        """
        return {
            "type": "collection",
            "id": self.collection_id,
            "attributes": {
                "name": self.collection_name,
                "Category": [
                    category.category_to_json()
                    for category in self.has_categories
                ],
                "description": self.collection_description,
            },
            "relationships": {
                "editions": [
                    author.author_to_json()
                    for author in self.collection_authorship
                ]
            },
            "images": [
                image.image_to_json()
                for image in self.has_images
            ],
            "links": {
                "self": url_for("collection", collection_id=self.collection_id, _external=True),
                "json": url_for("api_collection_data", collection_id=self.collection_id, _external=True)
            },
        }


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    has_collection = db.relationship("CollectionHasCategories", back_populates="category")

    @staticmethod
    def create(category_name):
        errors = []
        if not category_name:
            errors.append("Le nom de la catégorie est manquant.")

        if len(errors) > 0:
            return False, errors

        category_check = Collection.query.filter(Collection.collection_name.like("%"+category_name+"%")).first()
        if category_check:
            errors.append("Une collection porte déjà ce nom : " + category_name)

        # Si on a au moins une erreur
        if len(errors) > 0:
            return False, errors

        new_category = Category(
            name=category_name
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(new_category)
            # On envoie le paquet
            db.session.commit()

            # On renvoie l'utilisateur
            return True, new_category
        except Exception as erreur:
            return False, [str(erreur)]

    def to_json_api(self):
        """ It ressembles a little JSON API format but it is not completely compatible

        :return:
        """
        return {
            "type": "category",
            "attributes": {
                "category_name": self.name
            }
        }


class CollectionHasCategories(db.Model):
    __tablename__ = "collection_categories"
    id = db.Column(db.Integer(), primary_key=True)
    collection_id = db.Column(db.Integer(), db.ForeignKey('collection.collection_id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))
    collection = db.relationship("Collection", back_populates="has_categories")
    category = db.relationship("Category", back_populates="has_collection")

    def category_to_json(self):
        return {
            "category": self.category.to_json_api(),
        }


class Image(db.Model):
    __tablename__ = "image"
    image_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    image_url = db.Column(db.Text, nullable=False)
    has_collection = db.relationship("CollectionHasImages", back_populates="image")
    annotation = db.relationship("Annotation", back_populates="image", cascade="all, delete")

    @staticmethod
    def create(image_url):
        error = []
        if not image_url:
            error.append("L'URL de l'image est manquant.")

        if len(error) > 0:
            return False, error

        new_image = Image(
            image_url=image_url
        )

        try:
            db.session.add(new_image)
            db.session.commit()

            return True, new_image
        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        return self.image_id

    def to_json_api(self):
        return {
            "type": "image",
            "attributes": {
                "id": self.image_id,
                "url": self.image_url,
                "annotations":
                [
                    annotation.to_json_api()
                    for annotation in self.annotation
                ]
            }
        }


class Annotation(db.Model):
    __tablename__ = "annotation"
    annotation_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    annotation_json = db.Column(db.Text, nullable=False)
    annotation_image_id = db.Column(db.Integer, db.ForeignKey("image.image_id"))
    image = db.relationship("Image", back_populates="annotation")
    annotation_authorship = db.relationship("AuthorshipAnnotation", back_populates="annotation", cascade="all, delete")

    def to_json_api(self):
        return {
            "type": "annotation",
            "attributes": {
                "id": self.annotation_id,
                "json": self.annotation_json,
                "relationships": {
                    "editions": [
                        author.author_anno_to_json()
                        for author in self.annotation_authorship
                    ]
                }
            }
        }


class AuthorshipCollection(db.Model):
    authorship_collection_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_collection_collection_id = db.Column(db.Integer, db.ForeignKey('collection.collection_id'))
    authorship_collection_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_collection_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship("User", back_populates="authorship_collection")
    collection = db.relationship("Collection", back_populates="collection_authorship")

    def author_to_json(self):
        return {
            "author": self.user.to_json_api(),
            "on": self.authorship_collection_date
        }


class AuthorshipAnnotation(db.Model):
    authorship_annotation_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_annotation_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_annotation_annotation_id = db.Column(db.Integer, db.ForeignKey('annotation.annotation_id'))
    authorship_annotation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship("User", back_populates="authorship_annotation")
    annotation = db.relationship("Annotation", back_populates="annotation_authorship", cascade="all, delete")

    def author_anno_to_json(self):
        return {
            "author": self.user.to_json_api(),
            "on": self.authorship_annotation_date
        }


class CollectionHasImages(db.Model):
    collection_has_images_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    collection_has_images_collection_id = db.Column(db.Integer, db.ForeignKey('collection.collection_id'))
    collection_has_images_image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    collection = db.relationship("Collection", back_populates="has_images")
    image = db.relationship("Image", back_populates="has_collection", cascade="all, delete")

    def image_to_json(self):
        return {
            "image": self.image.to_json_api()
        }
