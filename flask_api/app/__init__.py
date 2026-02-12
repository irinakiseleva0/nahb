# flask_api/app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)


    # register blueprints
    from app.routes.stories import bp as stories_bp
    from app.routes.pages import bp as pages_bp

    app.register_blueprint(stories_bp)
    app.register_blueprint(pages_bp)

    # optional healthcheck
    try:
        from app.health import bp as health_bp
        app.register_blueprint(health_bp)
    except Exception:
        pass

    return app
