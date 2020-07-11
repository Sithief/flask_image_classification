from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser
import os

current_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_path, 'config.cfg')
CONF = configparser.ConfigParser()
CONF.read(path, encoding='utf-8')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)