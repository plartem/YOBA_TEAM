# email.py

from flask_mail import Message

import app, mail


def send_email(to, subject, template):
	msg = Message(
		subject,
		sender="test@gmail.com",
		recipients=[to],
		html=template
	)
	mail.send(msg)
