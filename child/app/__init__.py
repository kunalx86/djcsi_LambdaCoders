#! /Users/droom/Documents/codeshastra_lambda/nenv/bin/python3 
from flask import Flask
from flask_mongoengine import MongoEngine
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
# from flask_bcrypt import Bcrypt


from app.config import Config

app = Flask(__name__)

app.config.from_object(Config)

db = MongoEngine(app)
# jwt = JWTManager(app)
# bcrypt = Bcrypt(app)
# CORS(app, origins="*", supports_credentials=False)

@app.route("/me")
def test():
  return ("hello flask!")


from app.blueprints.filter import filter
app.register_blueprint(filter, url_prefix="/filter")