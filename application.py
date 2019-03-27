#!/usr/bin/python
from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Item, Category

# Imports to implement anti-forgery state tokens
from flask import session as login_session
import random, string

# OAUTH imports

#Creates a flow object from the client secrets JSON file. This JSON stores the
# client id, client secret, and other OAuth2 params
from oauth2client.client import flow_from_clientsecrets
#used when we run into an error when we try to exchange OTC for an auth token
from oauth2client.client import FlowExchangeError
# comprehensive http client lib from python
import httplib2
# python json lib for creation/manipulation of json data
import json
# converts the response from a function into a real http response
from flask import make_response
# similar to urllib2, but with improvements
import requests

#Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# extract the client_id and secrets from our secrets file.
CLIENT_ID = \
    json.loads(open('client_secret.json','r').read())['web']['client_id']

@app.route('/')
@app.route('/catalog')
def index():
    return render_template('catalog.html')


@app.route('/catalog/<category>/items')
def show_all_cat_items(category):
    return 'TODO: display the page with the following info:\n'\
        '\t- Page header including log-in/out button\n'\
        '\t- List of categories\n'\
        '\t- List of all items in this category\n'\
        '\t- if the use is logged in, show an option to add an item\n'


@app.route('/catalog/<category>/<item>')
def show_cat_item(category, item):
    """
    """
    return 'TODO: display the page with the following info:\n'\
        '\t- Page header including log-in/out button\n'\
        '\t- Item name as a heading and item description\n'\
        '\t- if the use is logged in, show an option to edit/delete the item\n'


@app.route('/catalog/<category>/delete')
def delete_cat_item(category):
    return 'TODO: display the delete conf page with the following info:\n'\
        '\t- Page header including log-in/out button\n'\
        '\t- Item deletion confirmation message\n'\
        '\t- Item deletion confirmation button\n'\


@app.route('/catalog/<category>/edit')
def edit_cat_item(category):
    return 'TODO: display the edit page with the following info:\n'\
        '\t- Page header including log-in/out button\n'\
        '\t- Edit header\n'\
        '\t- Title(name) input field for the title of item\n'\
        '\t- Description input field\n'\
        '\t- Category dropdown with all available categories\n'\
        '\t\tNOTE: This field should also contain an "other" option where '\
        'you can specify a new category\n'\


@app.route('/catalog/<category>/new')
def new_cat_item(category):
    return 'TODO: display the new page with the following info:\n'\
        '\t- Page header including log-in/out button\n'\
        '\t- Edit header\n'\
        '\t- Title(name) input field for the title of item\n'\
        '\t- Description input field\n'\
        '\t- Category dropdown with all available categories\n'\
        '\t\tNOTE: This field should also contain an "other" option where '\
        'you can specify a new category\n'\


@app.route('/login', methods=['GET','POST'])
def login():
    # handle GET requests to this endpoint
    if request.method == 'GET':
        if 'username' in login_session:
            print('username: %s' % login_session['username'])
            host = request.headers['host']
            src_url = request.headers['referer']

            redirect_path = src_url.replace(host,'')
            return redirect(redirect_path)

        # creates a pseudo-random alphanumeric string of 32 characters to act
        # as an anti-forgery token. This token is recreated every time '/login'
        # is hit
        state = ''.join(random.choice(string.ascii_uppercase+string.digits) \
                for x in xrange(32))
        # store this generated token to the session
        login_session['state'] = state
        # pass in the client ID provided by google
        return render_template('login.html', STATE=state, clientId=CLIENT_ID)
    # handle POST requests to this endpoint
    elif request.method == 'POST':
        # verify that this request came from a user attempting to log in via the
        # login page and not from some bot hitting this endpoint randomly
        if request.args.get('state') != login_session['state']:
            # respond that there was a mismatch
            response = make_response(json.dumps('Invalid state parameter'), 401)
            response.headers['Content-Type'] = 'application/json'
            return responsepostmessage

        # consume the state provided for this particular login flow
        login_session['state'] = None
        #get the query params from the body of the post
        code = request.data
            # specify that this is the OTC flow that we'll be sending

        # exchange the oauth OTC for a long-term auth token
        try:
            # creats an oauth flow object, adds client secret key
            oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
            # specify the uri that will handle the callback for the token
            # exchange
            oauth_flow.redirect_uri = 'postmessage'
            # This line does the exchange of the OTC for the credentials object
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            # respond that there was a mismatch
            response = make_response(json.dumps('Failed to upgrade the '\
                    'authorization code'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # successful token exchange, now on to verify the token and store the
        # user data. If the return value is anything other than None, we know
        # that there was some sort of issue with the login
        resp = verify_access_token(credentials)
        if resp is not None:
            # Return the error response generated by the verification function
            return response

        # token verification complete. Fetch and store the user info to the
        # session, and store the user info as well.
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = credentials.id_token['sub']

        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        params = {'access_token':login_session['access_token'], 'alt':'json'}

        # send the request and get the answer in JSON format
        answer = requests.get(userinfo_url, params=params)
        data = answer.json()

        login_session['username'] = data['name']
        # Not sure if supporting user pictures adds any value.
        # login_session['picture'] = data['picture']
        login_session['email'] = data['email']

        # Check to see if a user exists, if so, don't make a new one.
        uid = getUserId(login_session['email'])
        if uid is None:
            # if we got nothing from the db when we pinged it with the provided
            # email, then we know that there is no such user and we need to add a
            # new one
            print('Adding new user with email %', login_session['email'])
            uid = createUser(login_session)

        # either after creating a new user or after verifying it's existence, set
        # the session user_id variable
        login_session['user_id'] = uid
        login_session['provider'] = 'google'

        # formatted output for the sign-in button callback
        output = ''
        output += '<h1>Welcome, '+login_session['username']
        output += '!</h1>'

        # output += '<img src="' + login_session['picture']
        # output += '" style="width:300px; height: 300px; '\
        #     'border-radius:150px;-webkit-border-radius: '\
        #     '150px;-moz-border-radius:150px;">'

        flash('You are now logged in as %s'%login_session['username'])
        return output


@app.route('/logout')
def logout():
    # get the stored access token
    try:
        access_token = login_session['access_token']
    except KeyError:
        response = make_response(json.dumps(
            'User logout error'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # if there wasn't one presently, send a server error response
    if access_token is None:
        response = make_response(json.dumps(
            'User logout error'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # send a request to invalidate the access token
    url = 'https://accounts.google.com/o/oauth2/revoke?token='\
        + access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if the token invalidation was successful, remove all data associated with
    # this token
    del login_session['user_id']
    del login_session['provider']
    del login_session['email']
    del login_session['username']
    del login_session['access_token']
    del login_session['gplus_id']

    flash('You have been successfully logged out.')
    return redirect(url_for('index'))






#
# Helper methods for the login functionality
#
def verify_access_token(credentials):
    """
    verify_access_token - verifies the access token returned from the google
    OAuth2 server against several exceptional conditions listed below:
        error - there was an error in retrieving the token
        user_id mismatch - the token received doesn't match the expected google
            user ID
        client mismatch - the client_id for the token doesn't match that stored
            in the client secrets for this app
        already logged - the user is already logged in

    None is returned upon successful verification of the token
    """
    access_token = credentials.access_token
    url=('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'\
            .format(access_token))
    h = httplib2.Http()
    #send the GET request to google to verify
    results = json.loads(h.request(url, 'GET')[1])

    # if there are any errors, send an internal server error response
    if results.get('error') is not None:
        # respond that there was an internal error
        response = make_response(json.dumps(results.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # get the id for this access token to check against the id returned by the
    # google api server, if they don't match, there is either an attack or a
    # google api error
    gplus_id = credentials.id_token['sub']
    if results['user_id'] != gplus_id:
        # respond that there was an id mismatch
        response = make_response(json.dumps('Token ID does not match given '\
                'user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check the client id returned in the results
    if results['issued_to'] != CLIENT_ID:
        # respond that there was an id mismatch
        response = make_response(json.dumps('Token client ID does not match '\
                'given client ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if a user is already logged into a session
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current User is already logged '\
            'in'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    return None



def createUser(login_session):
    """
    Creates a new user in the DB using the session parameters
    """
    newUser = User(uname=login_session['username'], email =
            login_session['email'])
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Returns the User entry that has `user_id` as id
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    """
    Returns the ID for a User entry containing `email` as the registered email
    address
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


#
# JSON endpoints
#
@app.route('/catalog.json')
def catalog_json():
    """
    catalog_json - REST API endpoint that returns the contents of the catalog
    database as a JSON object.
    """
    # empty list to hold the contents of the catalog
    ret = []
    cats = session.query(Category).all()
    # for each category, add it to the return list and then search for it's
    # items
    for c in cats:
        ret.append(c.serialize)
        # once we have the items, serialize them and add them to the dict.
        items = session.query(Item).join(Item.category)
        ret[-1]['Item']= [i.serialize for i in items]
    return jsonify(Category = ret)

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
