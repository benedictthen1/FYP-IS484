import flask
from flask import Flask
import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from app import *

server = Flask(__name__)

server.config['SQLALCHEMY_DATABASE_URI'] = ''
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['AQLALCHEMY_ECHO'] = True

db = SQLAlchemy(server)

from app.dashboard import *
