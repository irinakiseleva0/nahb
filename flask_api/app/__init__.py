from flask import Flask
from .config import Config
from .extensions import db, migrate
#from .stories import bp as stories_bp
#from .pages import bp as pages_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  
    from .health import bp as health_bp
    app.register_blueprint(health_bp)

    from .routes import stories_bp, pages_bp
    app.register_blueprint(stories_bp)
    app.register_blueprint(pages_bp)

    return app
