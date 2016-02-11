from flask import Flask, render_template, url_for, redirect, flash, request
from flask.ext.bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


# Initialises app and extension modules
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)


# Database connection
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class CategoryForm(Form):
    name = StringField("What is the category you'd like to add?", validators=[DataRequired()])
    submit = SubmitField('submit')

class ItemForm(Form):
    name = StringField("What is the item you'd like to add?", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField()

@app.route('/')
def index():
    categories = session.query(Categories)
    return render_template('index.html', categories=categories)


@app.route('/category/add', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = session.query(Categories).filter_by(name = form.name.data).first()
        if category is None:
            category = Categories(name=form.name.data)
            session.add(category)
            session.commit()
            flash('Category added!')
        else:
            form.name.data = ''
        return redirect(url_for('index'))
    return render_template('add_category.html', form=form)


@app.route('/category/remove', methods=['Get', 'POST'])
def remove_category():
    categories = session.query(Categories)
    if request.method == 'POST':
        if request.form['name']:
            deleteItem = session.query(Categories).filter_by(name=request.form['name'])
            session.delete(deleteItem)
            session.commit()
            flash('Category deleted')
            return redirect(url_for('index'))
    else:
        return render_template('remove_category.html', categories=categories)

@app.route('/<string:category_name>/add_item', methods=['Get', 'POST'])
def add_item(category_name):
    category = session.query(Categories).filter_by(name=category_name).first()

    form = ItemForm()
    if form.validate_on_submit():
        item = session.query(Items).filter_by(name = form.name.data).first()
        if item is None:
            item = Items(name=form.name.data, description=form.description.data, category_id=category.id)
            session.add(item)
            session.commit()
            flash('Item added')
            return redirect(url_for('category_view', category_name=category_name))
    else:
        return render_template('add_item.html', form=form)


@app.route('/<string:category_name>')
def category_view(category_name):
    category = session.query(Categories).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category_id=category.id)
    return render_template('categories.html', category=category, items=items)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
