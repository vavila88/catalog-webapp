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


@app.route('/')
def index():
    return 'TODO: display the landing page with the following info:\n'\
        '\t- Page header including log-in/out button\n'\
        '\t- List of categories\n'\
        '\t- List of latest items added to the catalog\n'\
        '\t- if the use is logged in, show an option to add an item\n'


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
