from flask import Flask
from dotenv import dotenv_values

app = Flask(__name__)
config = dotenv_values('.env')

from app import routes