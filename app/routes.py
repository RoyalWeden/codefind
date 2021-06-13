from app import app, config
from flask import redirect, render_template, session, url_for, request
from sawo import createTemplate, verifyToken
import json
from app.database import PostgreSQLConnection
import webbrowser

createTemplate("app/templates/partials", flask=True)
sqldb = PostgreSQLConnection()
sqldb.drop_tables() # MAKE SURE TO REMOVE THIS

from app.customsearch import CustomSearch
search_api = CustomSearch()

@app.route('/')
@app.route('/home')
def home():
    check_valid_session_user_id()

    if 'identifier_type' not in session:
        session['identifier_type'] = 'email'
    return render_template(
        'home.html',
        session=session
    )

@app.route('/search', methods=['GET','POST'])
def search():
    check_valid_session_user_id()

    searches = None
    if 'user_id' in session and session['user_id'] != '':
        stars = sqldb.get_user_stars(session['user_id'])
    else:
        stars = None

    if request.method == 'POST':
        if request.form['which_form'] == 'search_query':
            searches = search_api.get_searches(request.form['search'])
        elif request.form['which_form'] == 'open_search':
            which_source = request.form['view_link']
            if 'user_id' in session and session['user_id'] != '':
                sqldb.add_user_click(session['user_id'], request.form['source_id' + which_source])
                if len(request.form.getlist('star' + which_source)) == 1 and request.form.getlist('star' + which_source)[0] == 'start_empty':
                    sqldb.add_user_star(session['user_id'], request.form['source_id' + which_source])
                elif len(request.form.getlist('star' + which_source)) == 0:
                    sqldb.remove_user_star(session['user_id'], request.form['source_id' + which_source])
                print(sqldb.get_user_stars(session['user_id']))
                print("Clicks:", sqldb.get_user_clicks(session['user_id']))
            webbrowser.open_new_tab(request.form['link' + which_source])

    searches_len = 0
    if searches != None:
        searches_len = len(searches)

    return render_template(
        'search.html',
        session=session,
        searches=searches,
        searches_len=searches_len,
        stars=stars
    )

@app.route('/starred', methods=['GET','POST'])
def starred():
    check_valid_session_user_id()

    if 'user_id' not in session or session['user_id'] == '':
        return redirect('/login')
    
    if request.method == 'POST':
        which_source = request.form['view_link']
        sqldb.add_user_click(session['user_id'], request.form['source_id' + which_source])
        if len(request.form.getlist('star' + which_source)) == 0:
            sqldb.remove_user_star(session['user_id'], request.form['source_id' + which_source])
        webbrowser.open_new_tab(request.form['link' + which_source])
        return redirect('/starred')

    source_ids = sqldb.get_user_stars(session['user_id'])

    if source_ids != None and len(source_ids) > 0:
        if '' in source_ids:
            source_ids.remove('')
        stars = list(map(lambda source_id: sqldb.get_source(source_id), source_ids))
    else:
        stars = []

    stars_len = 0
    if stars != None:
        stars_len = len(stars)

    return render_template(
        'starred.html',
        session=session,
        stars=stars,
        stars_len=stars_len
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
    session.pop('user_id', None)
    session.pop('identifier', None)
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


def check_valid_session_user_id():
    if 'user_id' in session:
        print(session['user_id'])
        if session['user_id'] == '':
            return redirect('/logout')
        user = sqldb.get_user(session['user_id'])
        if user == None:
            return redirect('/logout')