from app.app import config_app

if __name__ == "__main__":
    # On indique la configuration de l'app choisie.
    app = config_app("dev")
    # On lance l'app en mode debug, au cas où cela serait nécessaire.
    app.run(debug=True)
