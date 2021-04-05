from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .. app import db, login, app


class User(UserMixin, db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_forename = db.Column(db.Text, nullable=False)
    user_surname = db.Column(db.Text, nullable=False)
    user_login = db.Column(db.String(45), nullable=False, unique=True)
    user_email = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.Text, nullable=False)
    authorship_collection = db.relationship("AuthorshipCollection", back_populates="user")
    authorship_annotation = db.relationship("AuthorshipAnnotation", back_populates="user")

    @staticmethod
    def identification(login, password):
        """ Identifie un utilisateur. Si cela fonctionne, renvoie les données de l'utilisateurs.

        :param login: Login de l'utilisateur
        :param motdepasse: Mot de passe envoyé par l'utilisateur
        :returns: Si réussite, données de l'utilisateur. Sinon None
        :rtype: User or None
        """
        user = User.query.filter(User.user_login == login).first()
        if user:
            if login and check_password_hash(user.user_password, password):
                return user
        return None

    @staticmethod
    def create(user_forename, user_surname, user_login, user_email, user_password):
        """ Crée un compte utilisateur-rice. Retourne un tuple (booléen, User ou liste).
        Si il y a une erreur, la fonction renvoie False suivi d'une liste d'erreur
        Sinon, elle renvoie True suivi de la donnée enregistrée

        :param login: Login de l'utilisateur-rice
        :param email: Email de l'utilisateur-rice
        :param nom: Nom de l'utilisateur-rice
        :param motdepasse: Mot de passe de l'utilisateur-rice (Minimum 6 caractères)

        """
        errors = []
        if not user_forename:
            errors.append("prénom manquant")
        if not user_surname:
            errors.append("nom manquant")
        if not user_login:
            errors.append("login manquant")
        if not user_email:
            errors.append("email manquant")
        if not user_password or len(user_password) < 6:
            errors.append("le mot de passe fourni est vide ou fait moins de 6 caractères")

        # On vérifie que personne n'a utilisé cet email ou ce login
        uniques = User.query.filter(
            db.or_(User.user_email == user_email, User.user_login == user_login)
        ).count()
        if uniques > 0:
            errors.append("l'email ou le login sont déjà inscrits dans notre base de données")

        # Si on a au moins une erreur
        if len(errors) > 0:
            return False, errors

        # On crée un utilisateur
        new_user = User(
            user_forename=user_forename,
            user_surname=user_surname,
            user_login=user_login,
            user_email=user_email,
            user_password=generate_password_hash(user_password)
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(new_user)
            # On envoie le paquet
            db.session.commit()

            # On renvoie l'utilisateur
            return True, new_user
        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def password_update(login, password, new_password_1, new_password_2):
        user = User.query.filter(User.user_login == login).first()
        errors = []
        if not password:
            errors.append("mot de passe actuel manquant")
        if not new_password_1:
            errors.append("nouveau mot de passe manquant")
        if not new_password_2:
            errors.append("confirmation du nouveau mot de passe manquante")

        if len(errors) > 0:
            return False, errors

        if check_password_hash(user.user_password, password):
            if new_password_1 == new_password_2:
                user.user_password = generate_password_hash(new_password_2)
            else:
                errors.append("La confirmation du mot de passe a échoué")
                return False, errors
            try:
                db.session.add(user)
                db.session.commit()
                return True, user
            except Exception as erreur:
                return False, [str(erreur)]
        else:
            errors.append("Votre mot de passe actuel est incorrect")
            return False, errors


    def get_id(self):
        """ Retourne l'id de l'objet actuellement utilisé

        :returns: ID de l'utilisateur
        :rtype: int
        """
        return self.user_id

    def to_json_api(self):
        """ It ressembles a little JSON API format but it is not completely compatible

        :return:
        """
        return {
            "type": "people",
            "attributes": {
                "login": self.user_login
            }
        }


@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    return User.query.get(int(identifiant))
