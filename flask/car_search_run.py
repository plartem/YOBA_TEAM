import re
from flask import Flask, render_template, request, redirect, url_for
from flask_material import Material 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required
from flask_pymongo import PyMongo

#from token import generate_confirmation_token, confirm_token
#from email import send_email
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)  
Material(app)  
app.config['SECRET_KEY'] = 'USE-YOUR-OWN-SECRET-KEY-DAMNIT'
app.config['SECURITY_PASSWORD_SALT'] = 'SALT'
app.config['RECAPTCHA_PUBLIC_KEY'] = 'TEST'
#app.config['MAIL_DEFAULT_SENDER'] = 'sender'
app.config["MONGO_URI"] = "mongodb://localhost:27017/autoria"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'shoplab7@gmail.com'
app.config['MAIL_PASSWORD'] = 'shoplab7test'
app.config['MAIL_DEFAULT_SENDER'] = 'shoplab7@gmail.com'
mongo = PyMongo(app)
mail = Mail(app)





class ExampleForm(FlaskForm):
	mark_name = StringField('Mark', validators = [validators.required()])
	model_name = StringField('Model')
			
	submit_button = SubmitField('Find me a car!')

class LoginForm(FlaskForm):
	login = StringField('Enter your login', [validators.required()])
	password = StringField('Enter your password', [validators.required()])
	
	
class SignUpForm(FlaskForm):
	login = StringField('Enter login', [validators.required()])
	password = StringField('Enter password', [validators.required()])
	confirm = StringField('Confirm password', [validators.required()])
	name = StringField('Name', [validators.required()])
	surname = StringField('Surname', [validators. required()])
	email = StringField('E-mail', [validators. required()])
	submit_button = SubmitField('Sign Up')
	
#GAVNOGAVNOGAVNO
#GAVNOGAVNOGAVNO	
#gavno
#GAVNOGAVNOGAVNO	
#gavno

def send_email(to, subject, template):
	msg = Message(
		subject,
		sender="TELETSKIYHUY@gmail.com",
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
	
		#return False
	return email

#GAVNOGAVNOGAVNO	
#gavno
#GAVNOGAVNOGAVNO	
#gavno
	
@app.route('/')  
def welcome():
	form = LoginForm()
	return render_template('index.html', form = form)  
	
	if __name__ == '__main__':  
		app.run(debug = True)  
	
	
	
@app.route('/start', methods=['GET', 'POST'])
def start():
	form = ExampleForm(request.form)
	
	if form.validate_on_submit():
		regx = re.compile("^%s$" %(form.mark_name.data), re.IGNORECASE)
		cars = list(mongo.db.new_cars.find( {"mark_name" : regx }))
		return render_template('check.html', data = cars)
	
	return render_template('start.html', form = form)
	
@app.route('/checkDB')
def checkDB():
	cars = list(mongo.db.new_cars.find())
		
	return render_template('check.html', data = cars)

@app.route('/signup', methods = ['GET', 'POST'])
def sign_up():
	form = SignUpForm()
	if form.validate_on_submit():
		token = generate_confirmation_token(form.email.data)
	
		confirm_url = url_for('welcome', _external=True) ##, token=token, _external=True)
		html = render_template('activate.html', confirm_url=confirm_url)
		subject = "Please confirm your email"
		send_email(form.email.data, subject, html)
		
		return redirect('/start')
		
	return render_template('signUp.html', form = form)

@app.route('/confirm/<token>')
def confirm_email():
	email = confirm_token(token)
	return redirect('/')