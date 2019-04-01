#!/usr/bin/python
from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
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
    """
    index - serves up the landing page for this application
    """
    category_list = session.query(Category).order_by(asc(Category.name))
    latest_items = session.query(Item).order_by(desc(Item.id)).limit(5).all()
    # print('items:')
    # for i in latest_items:
    #     print(i.slug)
    return render_template('catalog.html', category_list=category_list,
        items=latest_items)


@app.route('/catalog/<cat_slug>/item')
def show_all_cat_items(cat_slug):
    """
    show_all_cat_items - displays all items in the category spefied by the slug
    """
    try:
        category = session.query(Category).filter_by(slug=cat_slug).one()
    except:
        flash('Error fulfilling request.')
        return redirect(url_for('index'))

    items = session.query(Item).filter_by(cat_id=category.id).all()

    return render_template('category.html', items=items, category=category)


@app.route('/catalog/<cat_slug>/delete', methods=['GET','POST'])
def delete_cat(cat_slug):
    """
    delete_cat - delete the specified category. This will also delete all
    associated items in the database
    """
    if 'username' not in login_session:
        flash('You are not authorized to do that.')
        return redirect(url_for('index'))

    if request.method == 'GET':
        try:
            category = session.query(Category).filter_by(slug=cat_slug).one()
            return render_template('delete_category.html', category=category)
        except:
            flash('Error fulfilling request.')
            return redirect(url_for('index'))

    else:
        try:
            category = session.query(Category).filter_by(slug=cat_slug).one()
        except:
            flash('Error fulfilling request.')
            return redirect(url_for('index'))
        items = session.query(Item).filter_by(cat_id=category.id).all()

        for i in items:
            session.delete(i)
            session.commit

        session.delete(category)
        session.commit

        flash('Category "%s": and associated items deleted.' % category.name)
        return redirect(url_for('index'))



@app.route('/catalog/item/<item_slug>')
def show_cat_item(item_slug):
    """
    show_cat_item - display the item selected via a unique slug. The slug
    contains in it the category that the item rests under, so adding the
    category to the URI seems worthless.
    """
    try:
        item = session.query(Item).filter_by(slug=item_slug).one()
        cat = session.query(Category).filter_by(id=item.cat_id).one()
        return render_template('category_item.html', item=item)
    except Exception, e:
        flash('Invalid item referrenced.')
        return redirect(url_for('index'))


@app.route('/catalog/item/<item_slug>/delete', methods=['GET','POST'])
def delete_cat_item(item_slug):
    """
    delete_cat_item - deletes the item speficied by the slug
    """
    if 'username' not in login_session:
        flash('You are not authorized to do that.')
        return redirect(url_for('index'))

    if request.method == 'GET':
        try:
            item = session.query(Item).filter_by(slug=item_slug).one()
            return render_template('delete_category_item.html', item=item)
        except:
            flash('Error fulfilling request.')
            return redirect(url_for('index'))
    elif request.method =='POST':
        try:
            item = session.query(Item).filter_by(slug=item_slug).one()
        except:
            flash('Error fulfilling request.')
            return redirect(url_for('index'))
        session.delete(item)
        session.commit()
        flash('Item %s successfully deleted from the catalog.'%item.title)
        return redirect(url_for('index'))



@app.route('/catalog/item/<item_slug>/edit', methods=['GET','POST'])
def edit_cat_item(item_slug):
    """
    edit_cat_item - edit the item specified by the slug
    """
    if 'username' not in login_session:
        flash('You are not authorized to do that.')
        # categories = session.query(Category).order_by(asc(Category.name))
        # latest_items = session.query(Item).order_by(desc(Item.id)).limit(5)
        return redirect(url_for('index'))

    if request.method == 'GET':
        try:
            item = session.query(Item).filter_by(slug=item_slug).one()
            category = session.query(Category).filter_by(id=item.cat_id).one()
            return render_template('edit_category_item.html', item=item,
                    category=category)
        except:
            flash('Error fulfilling request.')
            return redirect(url_for('index'))
    elif request.method == 'POST':
        for x in request.form:
            print('%s : %s'%(x,request.form[x]))

        try:
            item = session.query(Item).filter_by(slug=item_slug).one()
        except:
            flash('Error fulfilling request.')
            return redirect(url_for('index'))

        item.title = request.form['title']
        item.description = request.form['description']
        # if the edit contains a category change, update the relevant fields in
        # the item
        if 'category_select' in request.form:
            try:
                cat = session.query(Category).filter_by(name=
                        request.form['category_select']).one()
            except:
                flash('Error fulfilling request.')
                return redirect(url_for('index'))
            item.description = request.form['description']
            item.slug = gen_item_slug(cat.slug)
            item.cat_id = cat.id

            session.add(item)
            session.commit()

        # categories = session.query(Category).order_by(asc(Category.name))
        # latest_items = session.query(Item).order_by(desc(Item.id)).limit(5)
        return redirect(url_for('index'))



@app.route('/catalog/item/new', methods=['GET','POST'])
def new_item():
    """
    new_item - Function that creates a new item. This function also creates a
    new category for items, as opposed to placing the item in an existing
    category
    """
    if request.method == 'GET':
        # Get all categories in the database, will be used to populate a
        # dropdown
        category_list = session.query(Category).all()
        return render_template('new_category_item.html',
                category_list=category_list)
    elif request.method == 'POST':
        # the data from the text fields are stored in the request.form dict
        # the name of the select element, use this along with the form elements
        # to determine if a new category was requested to be added. Also check
        # for duplicate categories.

        for k in request.form:
            print(request.form[k])
        # extract the form data
        item_cat = ''
        if 'category_select' in request.form:
            item_cat = (request.form['category_select'])
        item_title = (request.form['title'])
        item_desc = (request.form['description'])

        try:
            try:
                print('Retrieving the specified category - %s' % item_cat)
                category = session.query(Category).filter_by(name=item_cat).one()
            except:
                new_cat_name = str(request.form['new_cat_title'])
                print('Create a new category with name - {}'.format(new_cat_name))
                new_category = Category(name=new_cat_name,
                        slug=gen_cat_slug(new_cat_name))
                session.add(new_category)
                session.commit()

                try:
                    category = session.query(Category).filter_by(name=new_cat_name).\
                            one()
                except:
                    flash('Error fulfilling request.')
                    return redirect(url_for('index'))

            item_slug = gen_item_slug(category.slug)
            print('Creating a new item with name - {}, cat_id - {}, desc -'\
                    '"{}", slug - {}'.format(item_title, item_desc, \
                        category.id, item_slug))

            newItem = Item(title=item_title, description=item_desc,
                cat_id=category.id, slug=item_slug)

            session.add(newItem)
            session.commit()

            # categories = session.query(Category).order_by(asc(Category.name))
            # latest_items = session.query(Item).order_by(desc(Item.id)).limit(5)
            return redirect(url_for('index'))
        except:
            flash('Unable to add duplicate item to the database: %s.' %
                    item_title)
            # categories = session.query(Category).order_by(asc(Category.name))
            # latest_items = session.query(Item).order_by(desc(Item.id)).limit(5)
            return redirect(url_for('index'))


def gen_cat_slug(base):
    """
    gen_cat_slug - Generates a slug for a category, namely, converts to all
    lowercase and replaces ' ' with '-'
    """
    ret = base.lower().replace(' ','-')
    print('slug for category %s - %s' %(base, ret))
    return ret


def gen_item_slug(base):
    """
    gen_item_slug - generates a slug out of the provided base string and 5 random
    alphanumeric characters.
    """
    return base + '-' +''.join(random.SystemRandom().choice(
        string.ascii_lowercase+string.digits) for x in xrange(5))


@app.route('/login', methods=['GET','POST'])
def login():
    """
    login - login handler used to retrieve google OAuth credentials
    """
    # prevent re-login if already logged in
    if 'username' in login_session:
        return redirect(url_for('index'))

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
            return response

        # consume the state provided for this particular login flow
        login_session['state'] = None
        #get the query params from the body of the post
        code = request.data
            # specify that this is the OTC flow that we'll be sending

        # exchange the oauth OTC for a long-term auth token
        try:
            # creats an oauth flow object, adds client secret key
            oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
            # NOTE: despite the redirect URI not being used in this flow, it
            # MUST be set as follows, otherwise Flask throws a 401 -
            # unauthorized error. It does not need to be present in the html
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
        login_session['picture'] = data['picture']
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

        flash('You are now logged in as %s.'%login_session['username'])
        return output


@app.route('/logout')
def logout():
    """
    logout - log a user out
    """
    # get the stored access token
    try:
        access_token = login_session['access_token']
    except KeyError:
        flash('No User currently logged in.')
        return redirect(url_for('index'))

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


######################
# JSON endpoints
######################


@app.route('/api/v1/catalog/JSON')
def catalog_json():
    """
    catalog_json - API endpoint that returns the contents of the catalog
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
        items = session.query(Item).filter_by(cat_id=c.id)
        ret[-1]['Items']= [i.serialize for i in items]
    return jsonify(Category = ret), 200


@app.route('/api/v1/catalog/category/JSON')
def categories_json():
    """
    categories_json - returns a JSON representation of all the categories in the
    DB
    """
    category_list = session.query(Category).order_by(asc(Category.name))
    return jsonify(Category = [c.serialize for c in category_list])


@app.route('/api/v1/catalog/category/<cat_slug>/JSON')
def cat_items_json(cat_slug):
    """
    cat_items_json - returns a JSON representation of all the items in a given
    category in the DB
    """
    try:
        category = session.query(Category).filter_by(slug=cat_slug).one()
        items = session.query(Item).filter_by(cat_id=category.id).all()

        ret = {}
        ret['Category'] = (category.serialize)
        ret['Category']['Items'] = [i.serialize for i in items]

        return jsonify(ret)
    except:
        flash('Error fulfilling request.')
        return redirect(url_for('index'))


@app.route('/api/v1/catalog/item/<item_slug>/JSON')
def item_json(item_slug):
    """
    item_json - returns a JSON representation of the item with the given slug
    stored in the DB
    """
    try:
        item = session.query(Item).filter_by(slug=slug).one()
        return jsonify(Item=item.serialize)
    except:
        flash('Error fulfilling request.')
        return redirect(url_for('index'))


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
