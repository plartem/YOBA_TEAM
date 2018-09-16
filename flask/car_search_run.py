import re
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_materialize import Material
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, ValidationError, RadioField, \
    BooleanField, SubmitField, IntegerField, FormField, PasswordField, validators
from wtforms.validators import Required
from flask_pymongo import PyMongo
from flask_session import Session

from flask_bcrypt import Bcrypt

# from token import generate_confirmation_token, confirm_token
# from email import send_email
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flaskext.mysql import MySQL

app = Flask(__name__)
Material(app)
app.config['SECRET_KEY'] = 'USE-YOUR-OWN-SECRET-KEY-DAMNIT'
app.config['SECURITY_PASSWORD_SALT'] = 'SALT'
app.config['RECAPTCHA_PUBLIC_KEY'] = 'TEST'
# app.config['MAIL_DEFAULT_SENDER'] = 'sender'

app.config["MONGO_URI"] = "mongodb://localhost:27017/autoria"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'shoplab7@gmail.com'
app.config['MAIL_PASSWORD'] = 'shoplab7test'
app.config['MAIL_DEFAULT_SENDER'] = 'shoplab7@gmail.com'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'cars'

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
mail = Mail(app)
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()


class ExampleForm(FlaskForm):
    mark_name = StringField('Mark', validators=[validators.required()])
    model_name = StringField('Model')

    submit_button = SubmitField('Find me a car!')


class LoginForm(FlaskForm):
    login = StringField('Enter your login', [validators.required()])
    password = StringField('Enter your password', [validators.required()])
    submit_button = SubmitField('LOGIN')


class SignUpForm(FlaskForm):
    login = StringField('Enter login', [validators.required()])
    password = PasswordField('Enter password', [validators.required()])
    confirm = PasswordField('Confirm password', [validators.required()])
    name = StringField('Name', [validators.required()])
    surname = StringField('Surname', [validators.required()])
    email = StringField('E-mail', [validators.required()])
    submit_button = SubmitField('Sign Up')


def send_email(to, subject, template):
    msg = Message(
        subject,
        sender="SOME USER",
        recipients=[to],
        html=template
    )
    mail.send(msg)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    email = serializer.loads(
        token,
        salt=app.config['SECURITY_PASSWORD_SALT'],
        max_age=expiration
    )

    # return False
    return email


@app.route('/')
def welcome():
    form = LoginForm()

    return render_template('index.html', form=form, id=session["user_id"])


    if __name__ == '__main__':
        app.run(debug=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, password, token FROM users WHERE login='%s' OR email='%s'"
            % (form.login.data, form.login.data))
        data = cursor.fetchone()
        print(data[2])
        print(data[0])
        if data[2] == '':
            if bcrypt.check_password_hash(data[1], form.password.data):
                session['user_id'] = data[0]
                flash('SUCCESSSSSSS')
                return render_template('base.html')
            else:
                flash('Wrong password')
                return render_template('base.html')
        else:
            flash("Registration isn't finished")
            return render_template('base.html')

    return render_template('login.html', form=form)


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


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm(request.form)
    if form.validate_on_submit():
        print(form.password.data, form.confirm.data)
        if form.password.data == form.confirm.data:
            hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            token = secrets.token_urlsafe(64)
            confirm_url = url_for('confirm_email', token=token, _external=True)

            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(form.email.data, subject, html)

            print()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(email, password, name, surname, login, token) VALUES('%s', '%s', '%s', '%s', '%s', '%s')"
                          %(form.email.data, hash, form.name.data, form.surname.data, form.login.data, token))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                flash('To finish registration follow registration email confirmation link')
            else:
                flash('OOPS...SOMETHING WENT WRONG....')
                #TODO LOG ERROR
                # str(data[0])
        else:
            flash('Passwords do not match')
            return render_template('signUp.html', form=form)
        return render_template('base.html')
    return render_template('signUp.html', form=form)


@app.route('/confirm/<token>')
def confirm_email(token):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET token='' WHERE token='%s'" %(token))
    data = cursor.fetchall()

    if len(data) is 0:
        conn.commit()
        flash('Registration finished')
    else:
        flash('OOPS...SOMETHING WENT WRONG....')
        # TODO LOG ERROR
        # str(data[0])
    return render_template('base.html')