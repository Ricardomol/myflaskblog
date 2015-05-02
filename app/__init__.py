import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from flask.ext.pagedown import PageDown

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = "Please log in to access this page."

moment = Moment(app)

pagedown = PageDown()

pagedown.init_app(app)

if not app.debug:
    import logging

from app import views, models
print ("******** TODO READY")