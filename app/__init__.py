from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config.from_object('app.config.BaseConfig')

base_url = os.environ.get('BASE_URL', '')
app.config['APPLICATION_ROOT'] = base_url

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models import *
from app.routes import *
from app.api import *