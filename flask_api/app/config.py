import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///nahb_flask.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_KEY = os.getenv("API_KEY", "")
