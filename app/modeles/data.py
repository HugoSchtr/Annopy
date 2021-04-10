from flask import url_for, jsonify
import datetime
import json


from .. app import db


# Création de la table des collections
# La class hérite de la classe db.Model. Ce commentaire vaut pour toutes les autres classes du dossier modeles
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


# On crée la table des catégories
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    # Le nom de chaque catégorie doit être unique
    name = db.Column(db.String(50), unique=True)
    # jointure avec la table CollectionHasCategories. Associe une catégorie à une collection.
    # relation many to many
    has_collection = db.relationship("CollectionHasCategories", back_populates="category")

    @staticmethod
    def create(category_name):
        """ Crée une catégorie. Retourne un typle (booléen, nouvelle Collection ou liste).
        En cas d'erreur, renvoie False suivi de la liste des erreurs.
        En cas de succès, renvoie True suivi de la donnée enregistrée.

        :param category_name: nom de la catégorie
        :type category_name: str
        :return: tuple (booléen, nouvelle catégorie ou liste)
        :rtype: tuple
        """

        # On crée la liste errors qui stockera les erreurs s'il y en a
        errors = []

        # On vérifie qu'il y a un nom de catégorie.
        # Le cas contraire, on met à jour la liste des erreurs.
        if not category_name:
            errors.append("Le nom de la catégorie est manquant.")

        # Si la liste des erreurs n'est pas vide, renvoie False et la liste d'erreurs.
        if len(errors) > 0:
            return False, errors

        # On vérifie que le nom de la catégorie n'est pas déjà pris.
        category_check = Collection.query.filter(Collection.collection_name.like("%"+category_name+"%")).first()
        if category_check:
            errors.append("Une collection porte déjà ce nom : " + category_name)

        # Si la liste des erreurs n'est pas vide, renvoie False et la liste d'erreurs.
        if len(errors) > 0:
            return False, errors

        # On crée une nouvelle catégorie
        new_category = Category(
            name=category_name
        )

        try:
            # On l'ajoute au transport vers la base de données.
            db.session.add(new_category)
            # On commit
            db.session.commit()

            # On renvoie la catégorie
            return True, new_category
        except Exception as erreur:
            return False, [str(erreur)]

    def to_json_api(self):
        """ Retourne les données de la catégorie sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de la catégorie
        :rtype: dict
        """
        return {
            "type": "category",
            "attributes": {
                "category_name": self.name
            }
        }


# On crée la table d'association CollectionHasCategories pour les collections et les catégories
class CollectionHasCategories(db.Model):
    __tablename__ = "collection_categories"
    id = db.Column(db.Integer(), primary_key=True)
    # Clé étrangère de la collection
    collection_id = db.Column(db.Integer(), db.ForeignKey('collection.collection_id'))
    # Clé étrangère de la catégorie
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))
    # Jointure avec la table Collection
    collection = db.relationship("Collection", back_populates="has_categories")
    # Jointure avec la table Category
    category = db.relationship("Category", back_populates="has_collection")

    def category_to_json(self):
        """ Retourne les données de l'association sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'association
        :rtype: dict
        """
        return {
            "category": self.category.to_json_api(),
        }


# On crée la table Image
class Image(db.Model):
    __tablename__ = "image"
    image_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    image_url = db.Column(db.Text, nullable=False)
    # Jointure avec la table CollectionHasImages
    # relation many to many
    has_collection = db.relationship("CollectionHasImages", back_populates="image")
    # Jointure avec la table Annotation
    # relation one to one
    # Si l'image est supprimée, les annotations qui lui sont associées le seront également avec cascade="all, delete"
    annotation = db.relationship("Annotation", back_populates="image", cascade="all, delete")

    @staticmethod
    def create(image_url):
        """ Crée une image. Retourne un typle (booléen, nouvelle Image ou liste).
        En cas d'erreur, renvoie False suivi de la liste des erreurs.
        En cas de succès, renvoie True suivi de la donnée enregistrée.

        :param image_url: URL de la nouvelle image
        :type image_url: str
        :return: tuple (booléen, nouvelle Image ou liste)
        :rtype: tuple
        """

        # On crée la nouvelle image
        new_image = Image(
            image_url=image_url
        )

        try:
            # On l'ajoute au transport vers la base de données.
            db.session.add(new_image)
            # On commit
            db.session.commit()
            # On renvoie la nouvele image
            return True, new_image

        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        """ Retourne l'ID de l'objet actuellement utilisé

        :return: ID de l'image
        :rtype: int
        """
        return self.image_id

    def to_json_api(self):
        """ Retourne les données de l'image sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'image
        :rtype: dict
        """
        return {
            "type": "image",
            "attributes": {
                "id": self.image_id,
                "url": self.image_url,
                "annotations":
                [
                    # on affiche chaque annotation associée à l'image concernée, grâce à la jointure
                    annotation.to_json_api()
                    for annotation in self.annotation
                ]
            }
        }


# On crée la table Annotation
class Annotation(db.Model):
    __tablename__ = "annotation"
    annotation_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # Les annotations, générées au format JSON par Annotorious avec JavaScript, sont stockées en tant que str.
    # Voir https://recogito.github.io/annotorious/getting-started/web-annotation/
    annotation_json = db.Column(db.Text, nullable=False)
    # Clé étrangère de l'image à laquelle est associée l'annotation
    annotation_image_id = db.Column(db.Integer, db.ForeignKey("image.image_id"))
    # Jointure avec la table Image
    # relation one to one
    image = db.relationship("Image", back_populates="annotation")
    # Jointure avec la table AuthorshipAnnotation.
    # Relation many to many
    # Si l'annotation est supprimée, l'authorship l'est également avec cascade="all, delete".
    annotation_authorship = db.relationship("AuthorshipAnnotation", back_populates="annotation", cascade="all, delete")

    def to_json_api(self):
        """ Retourne les données de l'annotation sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'annotation
        :rtype: dict
        """

        return {
            "type": "annotation",
            "attributes": {
                "id": self.annotation_id,
                "annotation_json": [
                    # On transforme la chaîne de caractère formatée JSON enregistrée en base de données en objet JSON
                    json.loads(self.annotation_json)
                ],
                "relationships": {
                    "editions": [
                        # On affiche l'authorship de l'annotation grâce à la jointure
                        author.author_anno_to_json()
                        for author in self.annotation_authorship
                    ]
                }
            }
        }


# On crée la table d'association AuthorshipCollection pour les collections et les users
class AuthorshipCollection(db.Model):
    authorship_collection_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    # Clé étrangère de la collection
    authorship_collection_collection_id = db.Column(db.Integer, db.ForeignKey('collection.collection_id'))
    # Clé étrangère du user
    authorship_collection_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_collection_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # Jointure avec la table User
    user = db.relationship("User", back_populates="authorship_collection")
    # Jointure avec la table Collection
    collection = db.relationship("Collection", back_populates="collection_authorship")

    def author_to_json(self):
        """ Retourne les données de l'association sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'association
        :rtype: dict
        """
        return {
            "author": self.user.to_json_api(),
            "on": self.authorship_collection_date
        }


# On crée la table d'association AuthorshipAnnotation pour les annotations et les users
class AuthorshipAnnotation(db.Model):
    authorship_annotation_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    # Clé étrangère du user
    authorship_annotation_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    # Clé étrangère de l'annotation
    authorship_annotation_annotation_id = db.Column(db.Integer, db.ForeignKey('annotation.annotation_id'))
    authorship_annotation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # Jointure avec la table User
    user = db.relationship("User", back_populates="authorship_annotation")
    # Jointure avec la table Annotation
    annotation = db.relationship("Annotation", back_populates="annotation_authorship", cascade="all, delete")

    def author_anno_to_json(self):
        """ Retourne les données de l'association sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'association
        :rtype: dict
        """
        return {
            "author": self.user.to_json_api(),
            "on": self.authorship_annotation_date
        }


# On crée la table d'association CollectionHasImages pour les collections et les images
class CollectionHasImages(db.Model):
    collection_has_images_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    # Clé étrangère de la collection
    collection_has_images_collection_id = db.Column(db.Integer, db.ForeignKey('collection.collection_id'))
    # Clé étrangère de l'image
    collection_has_images_image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    # Jointure avec la table Collection
    collection = db.relationship("Collection", back_populates="has_images")
    # Jointure avec la table Image
    image = db.relationship("Image", back_populates="has_collection", cascade="all, delete")

    def image_to_json(self):
        """ Retourne les données de l'association sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'association
        :rtype: dict
        """
        return {
            "image": self.image.to_json_api()
        }
