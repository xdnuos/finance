from flask import Flask
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap5(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
from app import models, routes
