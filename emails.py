from flask import render_template
from app import app,mail
from flask_mail import Message

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['BLOGGY_MAIL_SUBJECT_PREFIX'] + subject,
	sender=app.config['BLOGGY_MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	mail.send(msg)
	

