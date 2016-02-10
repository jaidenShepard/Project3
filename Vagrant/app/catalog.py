from flask import Flask, render_template, url_for, redirect, flash
from flask.ext.bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
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
    return render_template('remove_category.html', categories=categories)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
