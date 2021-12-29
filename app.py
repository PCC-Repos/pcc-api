from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://zimvcqcqedddwv:7c4ac2e62f0124e525e603dd10968c2a76e2a9e1843ae4263947898b0e347dd4@ec2-52-71-231-180.compute-1.amazonaws.com:5432/d6o7k4ttukfg04"
from db import db
db.init_app(app)

migrate = Migrate(app, db)

from api.api import bp_api
app.register_blueprint(bp_api)


if __name__ == '__main__':
    app.run()
