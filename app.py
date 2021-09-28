from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost:5858/first_class_api_db"
from db import db
db.init_app(app)

migrate = Migrate(app, db)

from api.api import bp_api
app.register_blueprint(bp_api)


if __name__ == '__main__':
    app.run()
