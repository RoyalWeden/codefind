from flask import Flask
from dotenv import dotenv_values

app = Flask(__name__)
config = dotenv_values('.env')
app.secret_key = config['SECRET_KEY']

from app import routes