from app import app,db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from flask_login import UserMixin,AnonymousUserMixin
from datetime import datetime
import hashlib

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class Permission:
	FOLLOW=0x01
	COMMENT=0x02
	WRITE_ARTICLES=0x04
	MODERATE_COMMENTS=0x08
	ADMINISTER=0X80

#define the database tables
class Role(db.Model):
	__tablename__='roles'
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(64),unique=True)
	default=db.Column(db.Boolean,default=False,index=True)
	permissions=db.Column(db.Integer)
	users=db.relationship('User',backref='role',lazy='dynamic')
	
	
	#assign various roles for the users...by default every user will get the User role
	#some will get Moderator or Administrator
	@staticmethod
	def insert_roles():
		roles = {
		'User': (Permission.FOLLOW |
				Permission.COMMENT |
				Permission.WRITE_ARTICLES, True),
		'Moderator': (Permission.FOLLOW |
					Permission.COMMENT |
					Permission.WRITE_ARTICLES |
					Permission.MODERATE_COMMENTS, False),
		'Administrator': (0xff, False)}
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()
		
	def __repr__(self):
		return '<name %r>'%self.name
		

#define table for post with many to one relationship for the users		
class Post(db.Model):
	__tablename__='posts'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
	
	

#using UserMixin allows us to automatically integrate the login methods such as is_active etc,by
#dfeining functions like login_manager.user_loader
class User(db.Model,UserMixin):
	#table name
	__tablename__='users'
	
	#primary key 
	id=db.Column(db.Integer,primary_key=True)
	
	#----------------------USER INFORMATION--------------------------
	username=db.Column(db.String(64),unique=True)
	email=db.Column(db.String(100),unique=True,index=True)
	password_hash=db.Column(db.String(128))
	#whether user has confirmed email or not
	confirmed = db.Column(db.Boolean, default=False)
	name=db.Column(db.String(64))
	location=db.Column(db.String(64))
	member_since=db.Column(db.DateTime(),default=datetime.utcnow)
	last_seen=db.Column(db.DateTime(),default=datetime.utcnow)
	about_me=db.Column(db.String(200))
	avatar_hash=db.Column(db.String(32))
	#set the many relationship for roles side
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
	#set the one relationship for the one side
	posts=db.relationship('Post',backref='author',lazy='dynamic')
	
	
	#-----------------ASSIGNMENT OF ROLES TO NEW USERS-------------------------
	#to assign roles to newly registered users and store the gavatar hash values
	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['BLOGGY_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
		#store the gavatar hash value as soon as an email is registered...becoz its cpu intensive
		#to calculate again and again if there are many gavtars on same page
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash=hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
				
	#-----------------VERIFICATION OF ROLES-----------------------------------			
	def can(self, permissions):
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)
		
	#-----------------CLASS FOR ANONYMUS USERS-------------------------------	
	class AnonymousUser(AnonymousUserMixin):
		def can(self, permissions):
			return False
		def is_administrator(self):
			return False
			
	#-------------------USER PROFILE PIC USING GRAVATAR------------------------
	def gravatar(self,size=100,default='identicon',rating='g'):
		if request.is_secure:
			url='https://secure.gravatar.com/avatar'
		else:
			url='http://www.gravatar.com/avatar'
		hash=self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
		url=url,hash=hash,size=size,default=default,rating=rating)
				
	
	#------------------OTHER METHODS FOR USERS--------------------------------
	#set up the method to hashpassword and check password to be stored in the database
	@property
	def password(self):
		raise AttributeError('password is not an attribute')
	
	#function to set the password after encrypting the password
	@password.setter
	def password(self,password):
		self.password_hash=generate_password_hash(password)
	
	#decrypt the password from the database and check it	
	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)
	
	#generate a cofirmation key for the new user by using TimedJSONWebSignatureSerializer for the current user id
	def generate_confirmation(self):
		s=Serializer(current_app.config['SECRET_KEY'],3600)
		return s.dumps({'confirm':self.id})
	
	#check if the status of the current user is confirmed or not 
	def confirm_status(self,token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data=s.loads(token)
		except:
			return False
		if data.get('confirm')!=self.id:
			return False
		self.confirmed=True;
		db.session.add(self)
		return True
	
	#refresh the last seen of the user
	def ping(self):
		self.last_seen=datetime.utcnow()
		db.session.add(self)
		
	def __repr__(self):
		return '<username %r>'%self.username

