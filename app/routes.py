import re
from app import app, config
from flask import redirect, render_template, session, url_for, request
from sawo import createTemplate, verifyToken
import json
from app.database import PostgreSQLConnection

createTemplate("app/templates/partials", flask=True)
sqldb = PostgreSQLConnection()

@app.route('/')
@app.route('/home')
def home():
    sqldb.drop_tables() # MAKE SURE TO REMOVE THIS
    if 'identifier_type' not in session:
        session['identifier_type'] = 'email'
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

@app.route('/login/<identifier_type>')
def set_login_type(identifier_type):
    if 'user_id' in session and session['user_id'] != '':
        return redirect('/')
    if identifier_type == 'email' or identifier_type == 'phone_number_sms':
        session['identifier_type'] = identifier_type
    return redirect('/login')

@app.route('/logout')
def logout():
    session['user_id'] = ''
    session['identifier'] = ''
    return redirect('/')

@app.route('/sawo', methods=['GET','POST'])
def sawo():
    if request.method == 'POST':
        payload = json.loads(request.data)['payload']
        if verifyToken(payload):
            # set user session
            session['user_id'] = payload['user_id']
            session['identifier'] = payload['identifier']
            sqldb.create_user(session['user_id'], session['identifier_type'], session['identifier'])
            return redirect('/')
        else:
            # no good
            print('not verified')
            return redirect('/login')

def sawo_route(to_location):
    return {
        'auth_key': config['SAWO_API_KEY'],
        'identifier': session['identifier_type'],
        'to': to_location
    }