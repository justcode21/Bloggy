from flask_wtf import Form
from wtforms import StringField,BooleanField,SubmitField,PasswordField,ValidationError,TextAreaField
from wtforms.validators import Required,Email,Length,Regexp,EqualTo
from models import User

#defining our own loginform class inherited from wtforms(form)
class LoginForm(Form):
	email=StringField('Email',validators=[Required(),Length(1,100),Email()])
	password=PasswordField('Password',validators=[Required()])
	remember_me=BooleanField('Keep Me Logged In')
	submit=SubmitField('Log In')
	
	
#defining the new registration form
class RegistrationForm(Form):
	email=StringField('Email',validators=[Required(),Length(1,100),Email()])
	username = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$'
	, 0,'Usernames must have only letters,numbers, dots or underscores')])
	#bothe the passwords must match
	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
	password2=PasswordField('Confirm Password',validators=[Required()])
	submin=SubmitField('Register')
	
	#check whether the email already exists in the database
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already exists')
	
	#check whether the username already exists in the database
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already exists')
			

#defining the edit information form
class EditProfile(Form):
	name=StringField('Real Name',validators=[Length(0,64)])
	location=StringField('Location',validators=[Length(0,64)])
	about_me=TextAreaField('About Me')
	submit=SubmitField('Submit')
	
#design a form for the posts
class PostForm(Form):
	body=TextAreaField('Whats On Your Mind ?' ,validators=[Required()])
	submit=SubmitField('Submit')
	


		
