from flask import Flask
from .config import Config
from .extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models

    from .health import bp as health_bp
    app.register_blueprint(health_bp)

    return app
