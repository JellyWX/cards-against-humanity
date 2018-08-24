from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters['zip'] = zip
db = SQLAlchemy(app)
socketio = SocketIO(app)

from app import routes, models

db.create_all()
