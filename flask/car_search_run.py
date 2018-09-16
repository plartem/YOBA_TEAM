import re
from flask import Flask, render_template, request, redirect, url_for
from flask_materialize import Material
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, ValidationError, RadioField, \
    BooleanField, SubmitField, IntegerField, FormField, PasswordField, validators
from wtforms.validators import DataRequired
from flask_pymongo import PyMongo

app = Flask(__name__)
Material(app)
app.config['SECRET_KEY'] = 'USE-YOUR-OWN-SECRET-KEY-DAMNIT'
app.config['RECAPTCHA_PUBLIC_KEY'] = 'TEST'
app.config["MONGO_URI"] = "mongodb://localhost:27017/autoria"
mongo = PyMongo(app)


class ExampleForm(FlaskForm):
    mark_name = StringField('Mark', validators=[validators.required()])
    model_name = StringField('Model')
    submit_button = SubmitField('Find me a car!')


class LoginForm(FlaskForm):
    login = StringField('Enter your login', validators=[validators.required()])
    password = PasswordField('Enter your password', validators=[validators.required()])


# remember_me = BooleanField('remember_me')


@app.route('/')
def welcome():
    form = LoginForm()
    return render_template('index.html', form=form)

    if __name__ == '__main__':
        app.run(debug=True)


@app.route('/start', methods=['GET', 'POST'])
def start():
    form = ExampleForm(request.form)

    if form.validate_on_submit():
        regx = re.compile("^%s$" % (form.mark_name.data), re.IGNORECASE)
        cars = list(mongo.db.new_cars.find({"mark_name": regx}))
        return render_template('check.html', data=cars)

    return render_template('start.html', form=form)


@app.route('/checkDB')
def checkDB():
    cars = list(mongo.db.new_cars.find())

    return render_template('check.html', data=cars)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        #flash('Login requested for ' + form.login.data + '", remember_me=' + str(form.remember_me.data))
        return redirect('/index')
    return render_template('register.html',
                           title='Sign In',
                           form=form)
