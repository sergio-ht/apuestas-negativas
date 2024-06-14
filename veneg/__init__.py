from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from flask_login import LoginManager
from veneg.config import Config



db = SQLAlchemy()
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"



def create_app(config_obj=Config):
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    from veneg.users.routes import users
    from veneg.matches.routes import matches
    from veneg.bots.routes import bots
    from veneg.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(matches)
    app.register_blueprint(bots)
    app.register_blueprint(errors)

    return app