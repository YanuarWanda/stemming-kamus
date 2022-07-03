from flask import Flask
from os import path

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "Key secret"
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['MYSQL_DATABASE_PORT	'] = '3306'
    app.config["MYSQL_DATABASE_USER"] = "root"
    app.config["MYSQL_DATABASE_PASSWORD"] = ""
    app.config['MYSQL_DATABASE_DB'] = "kata"

    from .views import views
    app.register_blueprint(views, url_prefix="/")

    return app