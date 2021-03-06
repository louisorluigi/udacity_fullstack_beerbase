from flask import (
    Flask, render_template, request,
    redirect, jsonify, url_for, flash
)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, BeerType, Beer, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)

APPLICATION_NAME = "Beerbase"


engine = create_engine('sqlite:///beerbase.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# create a state for login_session
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    print 'State = ' + state

    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Login via Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data

    # Exchange client token for FB token
    fb_client_secrets_file = 'fb_client_secrets.json'

    app_id = json.loads(
        open(fb_client_secrets_file, 'r').read())['web']['app_id']
    app_secret = json.loads(
        open(fb_client_secrets_file, 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.12/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s&'
           'fb_exchange_token=%s') % (app_id, app_secret, access_token)
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    # Get access token from response
    token = 'access_token=' + data['access_token']

    # Use token to get me info from API.
    url = ('https://graph.facebook.com/v2.12/me?'
           '%s&fields=name,id,email,picture') % token
    http = httplib2.Http()
    result = http.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['picture'] = data["picture"]["data"]["url"]

    print login_session['provider']
    print login_session['username']
    print login_session['email']
    print login_session['facebook_id']
    print login_session['picture']

    # pullout and store token for disconnect
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Check if user exists in the database. If not create a new user.
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Hello, '
    output += login_session['username']
    output += login_session['picture']
    flash("%s is now logged in" % login_session['username'])
    print "done!"
    return output


# Logout
@app.route('/disconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']

    # The access token for logout
    access_token = login_session['access_token']

    url = ('https://graph.facebook.com/%s/'
           'permissions?access_token=%s') % (facebook_id, access_token)

    http = httplib2.Http()
    result = http.request(url, 'DELETE')[1]

    if result == '{"success":true}':
        login_session.clear()
        response = make_response(json.dumps('You are now disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Error message is token is invalid
        response = make_response(
            json.dumps('Failed to revoke token.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# User handeling functions
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


# JSON APIs for Beer Types
@app.route('/beerbase/JSON')
def beerTypesJSON():
    beerTypes = session.query(BeerType).all()
    return jsonify(BeerType=[b.serialize for b in beerTypes])


# JSON APIs for beers in a type
@app.route('/beerbase/<int:beerType_id>/JSON')
def beersInTypeJSON(beerType_id):
    beerType = session.query(BeerType).filter_by(id=beerType_id).one()
    beers = session.query(Beer).filter_by(
        type_id=beerType_id).all()
    return jsonify(Beer=[b.serialize for b in beers])


# Show Beer Types
@app.route('/')
@app.route('/beerbase/')
def showBeerTypes():
    beerTypes = session.query(BeerType).all()
    return render_template('showBeerTypes.html', beerTypes=beerTypes)
    print login_session


# Add Beer Type
@app.route('/beerbase/new/', methods=['GET', 'POST'])
def newBeerType():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBeerType = BeerType(type=request.form['type'])
        user_id = login_session['user_id']
        session.add(newBeerType)
        session.commit()
        return redirect(url_for('showBeerTypes'))
    else:
        return render_template('newBeerType.html')


# Edit Beer Type.
@app.route('/')
@app.route('/beerbase/<int:beerType_id>/edit/', methods=['GET', 'POST'])
def editBeerType(beerType_id):
    editedBeerType = session.query(BeerType).filter_by(id=beerType_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedBeerType.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('As you did not\
               create this entry you do not have permission to\
               change it. You can only change the entries you make.\
                );}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['type']:
            editedBeerType.type = request.form['type']
        session.add(editedBeerType)
        session.commit()
        return redirect(url_for('showBeerTypes'))
    else:
        return render_template('editBeerType.html', beerType=editedBeerType)


# Del Beer Type
@app.route('/beerbase/<int:beerType_id>/del', methods=['GET', 'POST'])
def delBeerType(beerType_id):
    delBeerType = session.query(BeerType).filter_by(id=beerType_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if delBeerType.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('As you did not\
               create this entry you do not have permission to\
               change it. You can only change the entries you make.\
                );}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(delBeerType)
        session.commit()
        return redirect(url_for('showBeerTypes'))
    else:
        return render_template('delBeerType.html', beerType=delBeerType)


# Show beers in a type of beer
@app.route('/beerbase/<int:beerType_id>/')
def showBeers(beerType_id):
    beerType = session.query(BeerType).filter_by(id=beerType_id).one()
    beers = session.query(Beer).filter_by(
        type_id=beerType_id).all()
    return render_template('showBeers.html', beerType=beerType, beers=beers)


# Add new Beer
@app.route('/beerbase/<int:beerType_id>/new/', methods=['GET', 'POST'])
def newBeer(beerType_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        addBeer = Beer(name=request.form['name'],
                       description=request.form['description'],
                       type_id=beerType_id)
        user_id = login_session['user_id']
        session.add(addBeer)
        session.commit()
        return redirect(url_for('showBeers', beerType_id=beerType_id))
    else:
        return render_template('newBeer.html', beerType_id=beerType_id)


# Edit Beer
@app.route('/beerbase/<int:beerType_id>/<int:beer_id>/edit/',
           methods=['GET', 'POST'])
def editBeer(beerType_id, beer_id):
    editBeer = session.query(Beer).filter_by(id=beer_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editBeer.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('As you did not\
               create this entry you do not have permission to\
               change it. You can only change the entries you make.\
                );}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editBeer.name = request.form['name']
        if request.form['description']:
            editBeer.description = request.form['description']
        session.add(editBeer)
        session.commit()
        return redirect(url_for('showBeers', beerType_id=beerType_id))
    else:
        return render_template('editbeer.html',
                               beerType_id=beerType_id,
                               beer_id=beer_id, beer=editBeer)


# Del beer
@app.route('/beerbase/<int:beerType_id>/<int:beer_id>/del',
           methods=['GET', 'POST'])
def delBeer(beerType_id, beer_id):
    delBeer = session.query(Beer).filter_by(id=beer_id).one()
    beerType = session.query(BeerType).filter_by(id=beerType_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if delBeer.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('As you did not\
               create this entry you do not have permission to\
               change it. You can only change the entries you make.\
                );}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(delBeer)
        session.commit()
        return redirect(url_for('showBeers', beerType_id=beerType_id))
    else:
        return render_template('delBeer.html',
                               beerType=beerType, beer=delBeer)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
'\n\n'
