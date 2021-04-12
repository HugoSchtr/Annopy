from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..app import db, login


# On crée la table User, une class qui hérite des classes UserMixin et db.Model.
class User(UserMixin, db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_forename = db.Column(db.Text, nullable=False)
    user_surname = db.Column(db.Text, nullable=False)
    user_login = db.Column(db.String(45), nullable=False, unique=True)
    user_email = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.Text, nullable=False)
    # Jointure avec la table AuthorshipCollection.
    # Relation many to many
    authorship_collection = db.relationship("AuthorshipCollection", back_populates="user")
    # Jointure avec la table AuthorshipAnnotation.
    # Relation many to many
    authorship_annotation = db.relationship("AuthorshipAnnotation", back_populates="user")

    @staticmethod
    def identification(login, password):
        """ Identifie un-e utilisateur-ice. Si cela fonctionne, renvoie les données de l'utilisateur-ice.

        :param login: Login de l'utilisateur-ice
        :type login: str
        :param password: Mot de passe envoyé par l'utilisateur-ice
        :type password: str
        :returns: Si réussite, données de l'utilisateur-ice. Sinon None
        :rtype: User or None
        """

        # On fait une query à la table User, on stocke l'objet récupéré dans la variable user.
        # On cherche l'user qui a le même login que celui fourni par l'utilisateur-ice.
        user = User.query.filter(User.user_login == login).first()

        # Si la query a renvoyé un objet, on réalise l'identification.
        if user:
            # On vérifie que le mot de passe est le bon en comparant le password donné par l'utilisateur-ice et le hash.
            # Pour retourner l'user, il faut que le login soit True, et que check_password_hash ait renvoyé True.
            if login and check_password_hash(user.user_password, password):
                return user
        return None

    @staticmethod
    def create(user_forename, user_surname, user_login, user_email, user_password):
        """ Crée un compte utilisateur-rice. Retourne un tuple (booléen, User ou liste).
        Si il y a une erreur, la fonction renvoie False suivi d'une liste d'erreur
        Sinon, elle renvoie True suivi de la donnée enregistrée

        :param user_forename: Prénom de l'utilisateur-ice
        :type user_forename: str
        :param user_surname: Nom de l'utilisateur-ice
        :type user_surname: str
        :param user_login: Login de l'utilisateur-rice
        :type user_login: str
        :param user_email: Email de l'utilisateur-rice
        :type user_email: str
        :param user_password: Mot de passe de l'utilisateur-rice (Minimum 6 caractères)
        :type user_password: str
        :return: tuple (booléen, nouveau User ou liste)
        :rtype: tuple
        """

        # On crée la liste errors qui stockera les erreurs s'il y en a.
        errors = []
        # On vérifie qu'il y a un nom, prénom, login, email et password.
        # Le cas contraire, on met à jour la liste des erreurs.
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

        # On vérifie que l'email et le login renseigné n'existent pas déjà dans la base de données.
        # On fait une query avec un filtre.
        # On cherche à récupérer un user qui a le même email ou le même login que ceux renseignés pour vérifier.
        uniques = User.query.filter(
            db.or_(User.user_email == user_email, User.user_login == user_login)
        ).count()
        # Si la variable uniques contient plus de 0 objets, alors les identifiants existent déjà en base.
        if uniques > 0:
            errors.append("l'email ou le login sont déjà inscrits dans notre base de données")

        # Si la liste des erreurs n'est pas vide, renvoie False et la liste d'erreurs.
        if len(errors) > 0:
            return False, errors

        # On crée un-e utilisateur-rice.
        new_user = User(
            user_forename=user_forename,
            user_surname=user_surname,
            user_login=user_login,
            user_email=user_email,
            user_password=generate_password_hash(user_password)
        )

        try:
            # On l'ajoute au transport vers la base de données.
            db.session.add(new_user)
            # On commit.
            db.session.commit()

            # On renvoie utilisateur-rice.
            return True, new_user
        except Exception as erreur:
            return False, [str(erreur)]

    @staticmethod
    def password_update(login, password, new_password_1, new_password_2):
        """ Permet de mettre à jour le mot de passe de l'utilisateur-rice.

        :param login: login de utilisateur-rice
        :type login: str
        :param password: password de utilisateur-rice
        :type password: str
        :param new_password_1: nouveau password de l'utilisateur-rice
        :type new_password_1: str
        :param new_password_2: confirmation du nouveau password donné par utilisateur-rice
        :type new_password_2: str
        :return: tuple (booléen, updated User ou liste)
        :rtype: tuple
        """

        # On récupère dans la variable user l'utilisateur-rice qui souhaite changer son password.
        user = User.query.filter(User.user_login == login).first()

        # On crée la liste errors qui stockera les erreurs s'il y en a.
        errors = []
        # On vérifie qu'il y a le password actuel, le nouveau password, et la confirmation du nouveau password.
        # Le cas contraire, on met à jour la liste des erreurs.
        if not password:
            errors.append("mot de passe actuel manquant")
        if not new_password_1:
            errors.append("nouveau mot de passe manquant")
        if not new_password_2:
            errors.append("confirmation du nouveau mot de passe manquante")

        # Si la liste des erreurs n'est pas vide, renvoie False et la liste d'erreurs.
        if len(errors) > 0:
            return False, errors

        # On vérifie que l'utilisateur-rice a utilisé son bon password.
        if check_password_hash(user.user_password, password):
            # On vérifie que le nouveau password correspond à la confirmation du nouveau password.
            if new_password_1 == new_password_2:
                # Si c'est le cas, on hash le nouveau password
                user.user_password = generate_password_hash(new_password_2)
            else:
                # Si la confirmation a échoué, on renvoie l'erreur
                errors.append("La confirmation du mot de passe a échoué")
                return False, errors

            try:
                # On ajoute l'updated user au transport vers la base de données.
                db.session.add(user)
                # On commit.
                db.session.commit()

                # On renvoie l'updated user.
                return True, user

            except Exception as erreur:
                return False, [str(erreur)]
        # Si l'utilisateur-rice n'a pas donné son mot de passe actuel, on envoie l'erreur.
        else:
            errors.append("Votre mot de passe actuel est incorrect")
            return False, errors

    def get_id(self):
        """ Retourne l'id de l'objet actuellement utilisé

        :returns: ID de l'utilisateur-rice
        :rtype: int
        """
        return self.user_id

    def to_json_api(self):
        """ Retourne les données de l'utilisateur-ice sous forme de dictionnaire
        pour leur exploitation au format JSON via l'API.

        :return: dictionnaire des données de l'utilisateur-ice
        :rtype: dict
        """
        return {
            "type": "people",
            "attributes": {
                "user_id": self.user_id,
                "login": self.user_login,
                "user_forename": self.user_forename,
                "user_surname": self.user_surname
            }
        }


@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    return User.query.get(int(identifiant))
