import re
from app import app, config
from flask import redirect, render_template, session, url_for, request
from sawo import createTemplate, verifyToken
import json

createTemplate("app/templates/partials", flask=True)

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'home.html',
        session=session
    )

@app.route('/search')
def search():
    return render_template(
        'search.html',
        session=session
    )

@app.route('/login')
def login():
    if 'user_id' in session and session['user_id'] != '':
        return redirect('/')
    return render_template(
        'login.html',
        sawo=sawo_route('sawo'),
        session=session
    )

@app.route('/logout')
def logout():
    session['user_id'] = ''
    session['email'] = ''
    return redirect('/')

@app.route('/sawo', methods=['GET','POST'])
def sawo():
    if request.method == 'POST':
        payload = json.loads(request.data)['payload']
        if verifyToken(payload):
            # set user session
            session['user_id'] = payload['user_id']
            session['email'] = payload['identifier']
            print('verified', payload)
            return redirect('/')
        else:
            # no good
            print('not verified')
            return redirect('/login')

def sawo_route(to_location):
    return {
        'auth_key': config['SAWO_API_KEY'],
        'identifier': 'email',
        'to': to_location
    }