from flask import render_template, request, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required

from ..app import app, login
from ..modeles.data import *
from ..modeles.users import User


@app.route("/")
def homepage():
    collections = Collection.query.order_by(Collection.collection_id.desc()).limit(5).all()
    return render_template("pages/index.html", collections=collections)


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        status, data = User.create(
            user_forename=request.form.get("user_forename", None),
            user_surname=request.form.get("user_surname", None),
            user_login=request.form.get("user_login", None),
            user_email=request.form.get("user_email", None),
            user_password=request.form.get("user_password", None)
        )
        if status is True:
            flash("Inscription terminée ! Vous pouvez vous maintenant vous identifier.", "success")
            return redirect("/")
        else:
            flash("Des erreurs ont été rencontrées. Les voici : " + ", ".join(data), "error")
            return render_template("/pages/sign_up.html")
    else:
        return render_template("pages/sign_up.html")


@app.route("/sign_in", methods=["POST", "GET"])
def sign_in():
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connectée-e", "info")
        return redirect("/")

    if request.method == "POST":
        user = User.identification(
            login=request.form.get("login", None),
            password=request.form.get("password", None)
        )
        if user:
            flash("Vous êtes maintenant connectée-e", "success")
            login_user(user)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus. Vérifiez vos identifiants ou cliquez sur 'inscription'",
                  "error")
            return redirect("/sign_in")

    return render_template("pages/sign_in.html")


login.login_view = 'sign_in'


@app.route("/user_profile", methods=["POST", "GET"])
@login_required
def profile():
    if request.method == "POST":
        forename = request.form.get("forename", None)
        surname = request.form.get("surname", None)
        if forename:
            current_user.user_forename = request.form.get("forename", None)
        if surname:
            current_user.user_surname = request.form.get("surname", None)

        db.session.add(current_user)
        db.session.commit()

    return render_template("pages/user_profile.html")


@app.route("/user_profile/password_update", methods=["POST", "GET"])
@login_required
def password_update():
    if request.method == "POST":
        status, data = User.password_update(
            login=current_user.user_login,
            password=request.form.get("password", None),
            new_password_1=request.form.get("new_password_1", None),
            new_password_2=request.form.get("new_password_2", None)
        )

        if status is True:
            flash("Mot de passe modifié avec succès", "success")
            return redirect("/user_profile")
        else:
            flash("Erreur : " + ", ".join(data), "error")
            return render_template("/pages/password_update.html")

    return render_template("pages/password_update.html")


@app.route("/sign_out", methods=["POST", "GET"])
@login_required
def sign_out():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes maintenant déconnectée-e", "info")
    return redirect("/")


@app.route("/communauté")
def community():
    resultats = User.query.all()
    return render_template("pages/community.html", communities=resultats)
