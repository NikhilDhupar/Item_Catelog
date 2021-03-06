#!/usr/bin/env python3
# Python code for project item catalog
from flask import Flask, render_template, request, redirect
from flask import url_for, jsonify, make_response, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Book, User
from flask import session as login_session
import random
import string
import httplib2
import requests
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Google client_id
CLIENT_ID = json.loads(open('/var/www/FlaskApp/Item_Catelog/client_secrets.json', 'r').read())[
    'web']['client_id']

# Connect to database
engine = create_engine('postgresql://nikhil:admin123@localhost/nikhil')
Base.metadata.bind = engine

# Create session
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


# Homepage
@app.route('/')
@app.route('/bookstore/')
def Hellobookstore():
    categorylist = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publiccategorylist.html', list=categorylist)
    else:
        # print(login_session['access_token'])
        return render_template('categorylist.html', list=categorylist)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    print("The current session state is %s" % login_session['state'])
    return render_template('login.html', STATE=state)


# JSON endpoint to get category list
@app.route('/bookstore/JSON/')
def categoryjson():
    items = session.query(Category).all()
    return jsonify(Categorylist=[i.serialize for i in items])


# Display list all all categories
@app.route('/bookstore/<int:c_id>/')
def DisplayCategory(c_id):
    cat = session.query(Category).filter_by(id=c_id).one()
    blist = session.query(Book).filter_by(category_id=c_id)
    if 'username' not in login_session:
        return render_template('pdisplaybooks.html', category=cat, list=blist)
    else:
        return render_template('displaybooks.html', category=cat, list=blist)


# JSON endpoint to get list of books in this category
@app.route('/bookstore/<int:c_id>/JSON/')
def booklist(c_id):
    books = session.query(Book).filter_by(category_id=c_id)
    return jsonify(Bookslist=[i.serialize for i in books])


# Adding category
@app.route('/bookstore/addcategory/', methods=['GET', 'POST'])
def addcategory():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        newcategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newcategory)
        session.commit()
        return redirect(url_for('Hellobookstore'))
    else:
        return render_template('newcategory.html')


# Adding book
@app.route('/bookstore/<int:c_id>/addbook/', methods=['GET', 'POST'])
def addbook(c_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    category = session.query(Category).filter_by(id=c_id).one()
    if request.method == 'POST':
        print("Inside post of addbook")
        newbooks = Book(name=request.form['name'], price=request.form['price'],
                        author=request.form['author'],
                        description=request.form['description'],
                        category_id=c_id,
                        user_id=login_session['user_id'])
        session.add(newbooks)
        session.commit()
        return redirect(url_for('DisplayCategory', c_id=c_id))
    else:
        return render_template('newbook.html', category=category)


# Delete book
@app.route('/bookstore/<int:c_id>/delbook/<int:b_id>', methods=['GET', 'POST'])
def deletebook(c_id, b_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    item = session.query(Book).filter_by(id=b_id).one()
    if item.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if(request.method == 'POST'):
        session.delete(item)
        session.commit()
        return redirect(url_for('DisplayCategory', c_id=c_id))
    else:
        return render_template('deletebook.html', c_id=c_id, item=item)


# View Book
@app.route('/bookstore/<int:c_id>/vbook/<int:b_id>', methods=['GET', 'POST'])
def viewbook(c_id, b_id):
    item = session.query(Book).filter_by(id=b_id).one()
    if 'username' not in login_session:
        return render_template('publicviewbook.html', book=item, c_id=c_id)
    else:
        return render_template('viewbook.html', book=item, c_id=c_id)


# JSON endpoint to get details of a single book
@app.route('/bookstore/<int:c_id>/vbook/<int:b_id>/JSON/')
def bookjson(c_id, b_id):
    item = session.query(Book).filter_by(id=b_id).one()
    return jsonify(Book=item.serialize)


# Edit book
@app.route('/bookstore/<int:c_id>/vbook/<int:b_id>/edit',
            methods=['GET', 'POST'])
def editbook(c_id, b_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    editedItem = session.query(Book).filter_by(id=b_id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if(request.method == 'POST'):
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['name']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['author']:
            editedItem.author = request.form['author']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('viewbook', c_id=c_id, b_id=b_id))
    else:
        return render_template('editbook.html', c_id=c_id, item=editedItem)


# Deleting category
@app.route('/bookstore/delcategory/<int:c_id>', methods=['GET', 'POST'])
def deletecategory(c_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    item = session.query(Category).filter_by(id=c_id).one()
    if item.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('Hellobookstore'))
    else:
        return render_template('deletecategory.html', category=item)


# Google Connect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/FlaskApp/Item_Catelog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

# see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    # flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# logging out
@app.route('/logout')
def gdisconnect():
    if 'username' in login_session:
        access_token = login_session['access_token']
    else:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
             % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('Hellobookstore'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
