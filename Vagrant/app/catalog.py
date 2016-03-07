from flask import Flask, render_template, url_for, redirect, flash, request, \
    jsonify

from flask.ext.bootstrap import Bootstrap

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Categories, Items

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

from flask import session as login_session
import random, string

from flask import make_response
import json
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests

from flask.ext.login import LoginManager, login_required

# Initialises app and extension modules
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
bootstrap = Bootstrap(app)


# Database connection
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#APIs
@app.route('/categories/JSON')
def categoryJSON():
    categories = session.query(Categories).all()
    return jsonify(categories = [c.serialize for c in categories])

@app.route('/<string:category_name>/JSON')
def categoryItemsJSON(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])

#Forms
class CategoryForm(Form):
    name = StringField("What is the category you'd like to add?",
                       validators=[DataRequired()])
    submit = SubmitField('submit')

class ItemForm(Form):
    name = StringField("What is the item you'd like to add?",
                       validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    image = StringField("Image URL")
    submit = SubmitField()

class ItemEdit(Form):
        name = StringField("name", validators=[DataRequired()])
        description = TextAreaField("description", validators=[DataRequired()])
        image = StringField("Image URL")
        submit = SubmitField()


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.5/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout,
    #  let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0' \
          '&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

#DISCONNECT - Revoke a current user's token and reset their login-session.
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['facebook_id']
    return  'you have been logged out'


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
        del login_session['provider']
        flash("You have successfully been logged out.")
        return  redirect(url_for('index'))
    else:
        flash('You were not logged in to begin with!')
        return  redirect(url_for('index'))


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
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

#checks if session is logged in
def loggedIn():
    return 'username' in login_session

#checks if owner
def ownerCheck(user_id):
    if 'user_id' in login_session:
        return user_id == login_session['user_id']
    else:
        return None


# Index page
@app.route('/')
@app.route('/categories')
def index():
    categories = session.query(Categories)
    return render_template('index.html', categories=categories)


#category related pages
@app.route('/categories/<string:category_name>')
def category_view(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id)
    return render_template('categories.html', category=category, items=items,
                           owner_check=ownerCheck(category.user_id),
                           logged_in=loggedIn())


@app.route('/categories/categories/add', methods=['GET', 'POST'])
def category_add():
    if not loggedIn():
        return redirect(url_for('login'))

    form = CategoryForm()

    if form.validate_on_submit():
        category = session.query(Categories).filter_by(name = form.name.data).\
            first()
        if category is None:
            category = Categories(name=form.name.data,
                                  user_id=login_session['user_id'])
            session.add(category)
            session.commit()
            flash('Category added!')
        else:
            form.name.data = ''
        return redirect(url_for('index'))
    return render_template('category_add.html', form=form)


@app.route('/categories/<string:category_name>/remove', methods=['Get', 'POST'])
def remove_category(category_name):
    category = session.query(Categories).filter_by(name=category_name).first()

    if not loggedIn() or not ownerCheck(category.user_id):
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash("Category deleted")
        return redirect(url_for('index'))
    else:
        return render_template('category_remove.html',
                               category_name=category_name)


# ITEM related pages
@app.route('/categories/<string:category_name>/add_item', methods=['Get', 'POST'])
def add_item(category_name):
    category = session.query(Categories).filter_by(name=category_name).first()

    if not loggedIn() or not ownerCheck(category.user_id):
        return redirect(url_for('login'))

    form = ItemForm()

    if form.validate_on_submit():
        item = session.query(Items).filter_by(name=form.name.data).first()
        if item is None:
            item = Items(name=form.name.data, description=form.description.data,
                         image=form.image.data, category_id=category.id,
                         user_id=login_session['user_id'])
            session.add(item)
            session.commit()
            flash('Item added')
            return redirect(url_for('category_view',
                                    category_name=category_name))
    else:
        return render_template('item_add.html', form=form)


@app.route('/categories/<string:category_name>/<string:item_name>',
           methods=['GET', 'POST'])
def item_view(category_name, item_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items). filter_by(category_id=category.id,
                                           name=item_name).one()
    return render_template('item_view.html', item=item, category=category,
                           logged_in=loggedIn(), owner_check=ownerCheck(category.user_id))


@app.route('/categories/<string:category_name>/<string:item_name>/edit',
           methods=['Get', 'POST'])
def item_edit(category_name, item_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items). filter_by(category_id=category.id,
                                           name=item_name).one()

    if not loggedIn() or not ownerCheck(item.user_id):
        return redirect(url_for('login'))

    form = ItemEdit(obj=item)

    if form.validate_on_submit():
        form.populate_obj(item)
        item.name=form.name.data
        item.description=form.description.data
        item.description=form.description.data
        session.add(item)
        session.commit()
        flash("Item edited")
        return redirect(url_for('item_view', category_name=category_name,
                                item_name=item_name))
    else:
        return render_template('item_edit.html', category=category, item=item,
                               form=form)


@app.route('/categories/<string:category_name>/<string:item_name>/delete',
           methods=['Get', 'Post'])
def item_remove(category_name, item_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    item = session.query(Items).filter_by(category_id=category.id,
                                          name=item_name).one()

    if not loggedIn() or not ownerCheck(item.user_id):
        return redirect(url_for('login'))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item deleted")
        return redirect(url_for('category_view', category_name=category_name))
    else:
        return render_template('item_remove.html', category_name=category_name,
                               item_name=item_name)

# Error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', e=e), 500


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
