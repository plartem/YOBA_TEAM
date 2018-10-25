import re
import sys
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session, json, jsonify
from flask_materialize import Material
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, ValidationError, RadioField, \
    BooleanField, SubmitField, IntegerField, FormField, PasswordField, validators, SelectField
from wtforms.validators import Required, DataRequired
from flask_pymongo import PyMongo
from flask_session import Session

import subprocess

import os


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


from flask_bcrypt import Bcrypt

# from token import generate_confirmation_token, confirm_token
# from email import send_email
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flaskext.mysql import MySQL

from logger import Logger
import config

app = Flask(__name__)
Material(app)
app.config['SECRET_KEY'] = 'USE-YOUR-OWN-SECRET-KEY-DAMNIT'
app.config['SECURITY_PASSWORD_SALT'] = 'SALT'
app.config['RECAPTCHA_PUBLIC_KEY'] = 'TEST'
# app.config['MAIL_DEFAULT_SENDER'] = 'sender'

app.config["MONGO_URI"] = "mongodb://localhost:27017/crawler_db"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'shoplab7@gmail.com'
app.config['MAIL_PASSWORD'] = 'shoplab7test'
app.config['MAIL_DEFAULT_SENDER'] = 'shoplab7@gmail.com'

app.config['MYSQL_DATABASE_HOST'] = config.MYSQL_CONFIG['host']
app.config['MYSQL_DATABASE_PORT'] = config.MYSQL_CONFIG['port']
app.config['MYSQL_DATABASE_USER'] = config.MYSQL_CONFIG['user']
app.config['MYSQL_DATABASE_PASSWORD'] = config.MYSQL_CONFIG['password']
app.config['MYSQL_DATABASE_DB'] = config.MYSQL_CONFIG['dbname']

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
mail = Mail(app)
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()

logger = Logger()

class ExampleForm(FlaskForm):
    mark_name = StringField('Mark')
    model_name = StringField('Model')
    transmission = StringField('Transmission')
    year = IntegerField('Year', validators=[validators.Optional()])
    mileage = IntegerField('Maximum Mileage', validators=[validators.Optional()])
    low_price = IntegerField('Lower price', validators=[validators.Optional()])
    high_price = IntegerField('Higher price', validators=[validators.Optional()])
    reparse = StringField('Reparse')
    submit_button = SubmitField('Find me a car!')


class LoginForm(FlaskForm):
    login = StringField('Enter your login', [validators.required()])
    password = PasswordField('Enter your password', [validators.required()])
    submit_button = SubmitField('LOGIN')


class SignUpForm(FlaskForm):
    login = StringField('Enter login', [validators.required()])
    password = PasswordField('Enter password', [validators.required(), validators.equal_to('confirm')])
    confirm = PasswordField('Confirm password', [validators.required()])
    name = StringField('Name', [validators.required()])
    surname = StringField('Surname', [validators.required()])
    email = StringField('E-mail', [validators.required(), validators.email()])
    submit_button = SubmitField('Sign Up')


def send_email(to, subject, template):
    msg = Message(
        subject,
        sender="SOME USER",
        recipients=[to],
        html=template
    )
    logger.log("Sender", "Send mail to %s" % (to))
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


@app.route('/marks')
def marks():
    data = list(mongo.db.cars.aggregate([
        {
            "$group": {
                "_id": {"$toUpper": "$mark_name"},
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": None,
                "counts": {
                    "$push": {
                        "mark": "$_id",
                        "value": "$count"
                    }
                }
            }
        }
    ]))
    for d in data:
        print(d["counts"])
    return jsonify(data[0]["counts"])


@app.route('/')
def index():
    return render_template('index.html')

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
        if data[2] == '':
            if bcrypt.check_password_hash(data[1], form.password.data):
                session['user_id'] = data[0]
                logger.log("Session", "User %i login" % (int(session["user_id"])))
                flash('SUCCESSSSSSS')
                return redirect(url_for('index'))
            else:
                flash('Wrong password')
                logger.log("Session", "User %i wrong password" % (int(session["user_id"])))
                return render_template('login.html', form=form)
        else:
            flash("Registration isn't finished")
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/start', methods=['GET', 'POST'])
def start():
    form = ExampleForm(request.values)

    if form.validate_on_submit() or form.submit_button.data:
        temp = 0

        link = url_for('add_query', data={
            'mark': form.mark_name.data,
            'model': form.model_name.data,
            'high_price': -1 if form.high_price.data is None else form.high_price.data,
            'low_price': -1 if form.low_price.data is None else form.low_price.data,
            'year': -1 if form.year.data is None else form.year.data,
            'mileage': -1 if form.mileage.data is None else form.mileage.data
        })

        if form.mark_name.data == "":
            form.mark_name.data = ".+"
        if form.model_name.data == "":
            form.model_name.data = ".+"
        if form.transmission.data == "":
            form.transmission.data = ".+"
        if form.mileage.data is None:
            form.mileage.data = sys.maxsize
        if form.year.data is None:
            form.year.data = 2020
        else:
            temp = form.year.data
        if form.low_price.data is None:
            form.low_price.data = -sys.maxsize
        if form.high_price.data is None:
            form.high_price.data = sys.maxsize

        regx_mark = re.compile("^%s$" % form.mark_name.data, re.IGNORECASE)
        regx_model = re.compile("^%s$" % form.model_name.data, re.IGNORECASE)
        regx_transmission = re.compile("^%s$" % form.transmission.data, re.IGNORECASE)

        if form.reparse.data != '':
            with cd("crawler"):
                cmdCommand = "python start_all.py"  # specify your cmd command
                process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
                process.communicate()

        cars = list(mongo.db.cars.find({"mark_name": regx_mark, "model_name": regx_model,
                                        "transmission": regx_transmission,
                                        "mileage": {"$lte": form.mileage.data},
                                        "year": {"$gte": temp, "$lte": form.year.data},
                                        "price": {"$gte": form.low_price.data, "$lte": form.high_price.data}}))

        return render_template('check.html', data=cars, link=link)

    return render_template('start.html', form=form)


@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm(request.form)
    if form.validate_on_submit():
        if form.password.data == form.confirm.data:
            hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            token = secrets.token_urlsafe(64)

            confirm_url = url_for('confirm_email', token=token, _external=True)

            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(form.email.data, subject, html)
            logger.log("Sign Up", "Need confirm for %s" % (form.email.data))

            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users(email, password, name, surname, login, token) VALUES('%s', '%s', '%s', '%s', '%s', '%s')"
                    % (form.email.data, hash, form.name.data, form.surname.data, form.login.data, token))
                data = cursor.fetchall()
            except:
                flash('OOPS...SOMETHING WENT WRONG....')

            if len(data) is 0:
                conn.commit()
                flash('To finish registration follow registration email confirmation link')
            else:
                flash('OOPS...SOMETHING WENT WRONG....')
        else:
            flash('Passwords do not match')
            return render_template('signUp.html', form=form)
        return redirect(url_for('index'))
    return render_template('signUp.html', form=form)


@app.route('/confirm/<token>')
def confirm_email(token):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET token='' WHERE token='%s'" % (token))
    data = cursor.fetchall()
    if len(data) is 0:
        conn.commit()
        logger.log("Session", "User %i finished ewgistration" % (int(session["user_id"])))
        flash('Registration finished')
    else:
        flash('OOPS...SOMETHING WENT WRONG....')
    return redirect(url_for('index'))


@app.route('/addQuery', methods=['GET'])
def add_query():
    if session['user_id']:
        print(str(request.values['data']))
        data = json.loads(str(request.values['data']).replace('\'', '\"'))
        print(data)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queries(mark, model, high_price, low_price, year, mileage, user_id) VALUES('%s', '%s', '%f', '%f', '%d', '%d', '%d')"
            % (data['mark'], data['model'], data['high_price'], data['low_price'],
               data['year'], data['mileage'], int(session['user_id'])))
        db_data = cursor.fetchall()
        logger.log("Query", "User %i added query" % (int(session['user_id'])))
        return redirect("/queries")
    return redirect('/')


@app.route('/queries')
def queries():
    if session['user_id']:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, mark, model, high_price, low_price, year, mileage FROM queries WHERE user_id=%d"
            % (int(session['user_id'])))
        db_data = cursor.fetchall()
        data = []
        for row in db_data:
            data.append({
                'id': row[0],
                'mark': row[1],
                'model': row[2],
                'high_price': row[3],
                'low_price': row[4],
                'year': row[5],
                'mileage': row[6],
                'url': url_for('start', mark_name=row[1],
                               model_name=row[2],
                               high_price=row[3] if row[3] != -1 else None,
                               low_price=row[4] if row[4] != -1 else None,
                               year=row[5] if row[5] != -1 else None,
                               mileage=row[6] if row[6] != -1 else None,
                               submit_button=True)
            })
        return render_template("queries.html", data=data)
    return redirect('/')


@app.route('/removeQuery/<id>')
def remove_query(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM queries WHERE id='%d' AND user_id='%d'" % (int(id), int(session["user_id"])))
    data = cursor.fetchall()
    logger.log("Query", "User %i removed query" % (int(session["user_id"])))
    if len(data) is 0:
        conn.commit()
        flash('Query removed')
    else:
        flash('OOPS...SOMETHING WENT WRONG....')
    return redirect(url_for('queries'))


@app.route('/logout')
def logout():
    session.clear()
    logger.log("Session", "User %i logout" % (int(session["user_id"])))
    return redirect('/')
