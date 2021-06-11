from app import app
from flask import redirect, render_template, session, url_for, request

@app.route('/')
def home():
    return "Hello World!"