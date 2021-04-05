from app.app import config_app

if __name__ == "__main__":
    app = config_app("test")
    app.run(debug=True)
