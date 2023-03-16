import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from structlog import get_logger

from app.cli import cli

log = get_logger(name=__name__)

basedir = os.path.abspath(os.path.dirname(__file__))


db = SQLAlchemy()

# TOOD: Move all of the config to its own module
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "local", "database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.cli.add_command(cli)
db.init_app(app)


@app.route("/")
def main():
    return "<h1>Specter Web Scraper</h1>"


from app import models
