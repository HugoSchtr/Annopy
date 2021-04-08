from flask import render_template, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required

from ..app import app, login
from ..modeles.data import *
from ..modeles.users import User

"""
Routes gérant les aspects utilisateur de l'app:
Dans l'ordre : 
/
/sign_up
/sign_in
/user_profile
/user_profile/password_update
/sign_out
/community
"""


@app.route("/")
def homepage():
    """ Affiche la page d'accueil

    :return: template index.html
    :rtype: template
    """

    # On récupère les 5 dernières collections créées en base de données
    collections = Collection.query.order_by(Collection.collection_id.desc()).limit(5).all()
    return render_template("pages/index.html", collections=collections)


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """ Route permettant de s'inscrire et de créer un compte utilisateur-ice

    :return: sign_up.html
    :rtype: template
    """

    # Si la requête HTTP est POST, on crée un compte utilisateur-ice
    if request.method == "POST":
        # On utilise la méthode create créée dans la classe User
        status, data = User.create(
            # On récupère chaque donnée du form HTML envoyée en POST avec request.form.get()
            # Par exemple, pour user_forename, on récupère l'input HTML "user_forename"
            # s'il est vide, None par défaut
            user_forename=request.form.get("user_forename", None),
            user_surname=request.form.get("user_surname", None),
            user_login=request.form.get("user_login", None),
            user_email=request.form.get("user_email", None),
            user_password=request.form.get("user_password", None)
        )
        # Si la méthode retourne True et l'user, l'inscription est faite
        # On affiche un message avec flash() sur le template
        if status is True:
            flash("Inscription terminée ! Vous pouvez vous maintenant vous identifier.", "success")
            return redirect("/")
        # Si la méthode retourne False, on affiche avec flash() les erreurs
        else:
            flash("Des erreurs ont été rencontrées. Les voici : " + ", ".join(data), "error")
            return render_template("/pages/sign_up.html")
    else:
        return render_template("pages/sign_up.html")


@app.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    """ Route permettant à l'utilisateur-ice de se connecter

    :return: sign_in.html
    :rtype: template
    """

    # Si l'utilisateur-ice est connectée, on envoie un message au templace avec flash()
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connectée-e", "info")
        return redirect("/")

    # Si la requête HTTP est POST, on identifie l'utilisateur-ice
    if request.method == "POST":
        # On utilise la méthode identification créée dans la classe User
        user = User.identification(
            login=request.form.get("login", None),
            password=request.form.get("password", None)
        )
        # Si la méthode renvoie user, alors l'utilisateur-ice est identifiée
        # On envoie un message au template avec flash()
        # On redirige vers la page d'accueil
        if user:
            flash("Vous êtes maintenant connectée-e", "success")
            login_user(user)
            return redirect("/")
        else:
            # Si la méthode renvoie None, alors l'utilisateur-ice n'a pas été identifiée
            # On envoie un message au template avec flash(), on redirige vers la même page qu'actuellement
            flash("Les identifiants n'ont pas été reconnus. Vérifiez vos identifiants ou cliquez sur 'inscription'",
                  "error")
            return redirect("/sign_in")

    return render_template("pages/sign_in.html")

# Nom de la fonction à renvoyer si l'utilisateur-ice a besoin de se log in
login.login_view = 'sign_in'


@app.route("/user_profile", methods=["POST", "GET"])
@login_required
def profile():
    """ Route permettant d'afficher le profil d'un-e utilisateur-ice
    Pour accéder à cette page, il faut être connectée-e (décorateur login_required)

    :return: user_profile.html
    :rtype: template
    """

    # Si la requête HTTP est POST, on modifie le profil utilisateur-ice
    if request.method == "POST":
        # on récupère le prénom et le nom de famille indiquée par l'utilisateur-ice
        forename = request.form.get("forename", None)
        surname = request.form.get("surname", None)
        # Les deux if suivants permettent de vérifier si forename et surname ne sont pas None.
        # Si l'un des deux n'est pas none, on modifie la donnée en base en fonction de celui-ci
        # Cela permet de changer son prénom ou son nom de famille sans effacer l'un ou l'autre
        # si on ne modifie pas les deux informations.
        if forename:
            current_user.user_forename = request.form.get("forename", None)
        if surname:
            current_user.user_surname = request.form.get("surname", None)

        # On ajoute l'utilisateur-ice courant au transport vers la base de données
        db.session.add(current_user)
        # On commit
        db.session.commit()

    return render_template("pages/user_profile.html")


@app.route("/user_profile/password_update", methods=["POST", "GET"])
@login_required
def password_update():
    """ Route permettant de mettre à jour le mot de passe de l'utilisateur-ice
    Pour accéder à cette page, il faut être connectée-e (décorateur login_required)

    :return: password_update.html
    :rtype: template
    """

    # Si la requête HTTP est POST, on met le password à jour
    if request.method == "POST":
        # On utilise la méthode password_update de la classe User
        status, data = User.password_update(
            login=current_user.user_login,
            password=request.form.get("password", None),
            new_password_1=request.form.get("new_password_1", None),
            new_password_2=request.form.get("new_password_2", None)
        )

        # Si la méthode retourne True, le password a été modifiée avec succès
        if status is True:
            # On envoie un message au template avec flash() et on redirige vers la page du profil utilisateur-ice
            flash("Mot de passe modifié avec succès", "success")
            return redirect("/user_profile")
        # Si la méthode retourne False, la modification de password a échoué
        else:
            # On envoie un message au template avec flash()
            # On redirige l'utilisateur-ice vers la même page qu'actuellement
            flash("Erreur : " + ", ".join(data), "error")
            return render_template("/pages/password_update.html")

    return render_template("pages/password_update.html")


@app.route("/sign_out", methods=["POST", "GET"])
@login_required
def sign_out():
    """ Route pour déconnecter l'utilisateur-ice

    :return: redirect
    :rtype: template
    """

    # Si l'utilisateur-ice courant-e est identifiée (True), on le/la déconnecte avec la fonction logout_user()
    if current_user.is_authenticated is True:
        logout_user()
    # On envoie un message au template avec flash()
    flash("Vous êtes maintenant déconnectée-e", "info")
    # On redirige l'utilisateur-ice déconnecté-e vers la page d'accueil
    return redirect("/")


@app.route("/community")
def community():
    """ Route permettant d'afficher la communauté inscrite paginée

    :return: community.html
    :rtype: template
    """

    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    resultats = User.query.paginate(page=page, per_page=8)

    return render_template("pages/community.html", resultats=resultats)
