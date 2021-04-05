from flask import url_for
from sqlalchemy.ext.mutable import MutableDict
import datetime

from .. app import db

class Collection(db.Model):
    __tablename__ = "collection"
    collection_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    collection_name = db.Column(db.String(45), unique=True, nullable=False)
    collection_description = db.Column(db.Text, nullable=False)
    has_categories = db.relationship('CollectionHasCategories', back_populates="collection")
    collection_authorship = db.relationship("AuthorshipCollection", back_populates="collection", cascade="all, delete")
    has_images = db.relationship("CollectionHasImages", back_populates="collection", cascade="all, delete")

    @staticmethod
    def create(collection_name, collection_description):
        errors = []
        if not collection_name:
            errors.append("Le nom de la collection est manquant.")
        if not collection_description:
            errors.append("La description de la collection est manquante.")

        if len(errors) > 0:
            return False, errors

        collection_name_check = Collection.query.filter(Collection.collection_name.like("%"+collection_name+"%")).first()
        if collection_name_check:
            errors.append("Une collection porte déjà ce nom : " + collection_name)

        # Si on a au moins une erreur
        if len(errors) > 0:
            return False, errors

        new_collection = Collection(
            collection_name=collection_name,
            collection_description=collection_description,
        )

        try:
            db.session.add(new_collection)
            db.session.commit()

            return True, new_collection
        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        return self.collection_id

    def to_json_api(self):
        is_finished = ""
        if self.is_finished == 1:
            is_finished = "Complete"
        else:
            is_finished = "Not complete yet"
        return {
            "type": "collection",
            "attributes": {
                "name": self.collection_name,
                "description": self.collection_description,
                "date": self.collection_date,
                "is_finished": is_finished
            }
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


class CollectionHasCategories(db.Model):
    __tablename__ = "collection_categories"
    id = db.Column(db.Integer(), primary_key=True)
    collection_id = db.Column(db.Integer(), db.ForeignKey('collection.collection_id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))
    collection = db.relationship("Collection", back_populates="has_categories")
    category = db.relationship("Category", back_populates="has_collection")


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

    def to_json_api_dict(self):
        return {
            "type": "image",
            "attributes": {
                "url": self.image_url,
                "name": self.image_name,
            }
        }


class Annotation(db.Model):
    __tablename__ = "annotation"
    annotation_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    annotation_json = db.Column(db.Text, nullable=False)
    annotation_image_id = db.Column(db.Integer, db.ForeignKey("image.image_id"))
    image = db.relationship("Image", back_populates="annotation")
    annotation_authorship = db.relationship("AuthorshipAnnotation", back_populates="annotation", cascade="all, delete")


class AuthorshipCollection(db.Model):
    authorship_collection_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_collection_collection_id = db.Column(db.Integer, db.ForeignKey('collection.collection_id'))
    authorship_collection_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_collection_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship("User", back_populates="authorship_collection")
    collection = db.relationship("Collection", back_populates="collection_authorship")

    def authorship_collection_to_json(self):
        return {
            "author": self.user.to_json_api(),
            "on": self.authorshipCollection_date
        }


class AuthorshipAnnotation(db.Model):
    authorship_annotation_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_annotation_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_annotation_annotation_id = db.Column(db.Integer, db.ForeignKey('annotation.annotation_id'))
    authorship_annotation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship("User", back_populates="authorship_annotation")
    annotation = db.relationship("Annotation", back_populates="annotation_authorship", cascade="all, delete")


class CollectionHasImages(db.Model):
    collection_has_images_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    collection_has_images_collection_id = db.Column(db.Integer, db.ForeignKey('collection.collection_id'))
    collection_has_images_image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    collection = db.relationship("Collection", back_populates="has_images")
    image = db.relationship("Image", back_populates="has_collection", cascade="all, delete")
