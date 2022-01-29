import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
from db import db
db.init_app(app)

migrate = Migrate(app, db)

from api.api import bp_api
app.register_blueprint(bp_api)


if __name__ == '__main__':
    app.run()
