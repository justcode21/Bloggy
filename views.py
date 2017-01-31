from flask import Flask,flash,render_template,request,session,redirect,url_for
from flask_login import current_user,login_user,login_required,logout_user
from app import app,db,mail
from datetime import datetime
from forms import LoginForm,RegistrationForm,EditProfile,PostForm
from emails import *
from models import *

#create the home page
@app.route('/', methods=['GET', 'POST'])
def index():
	newform=PostForm()
	if newform.validate_on_submit():
		post=Post(body=newform.body.data,author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('index'))
	page=request.args.get('page',1,type=int)
	pagination=Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page=current_app.config['POST_PER_PAGE'])
	posts=pagination.items
	return render_template('index.html',form=newform,posts=posts,pagination=pagination)



#create the login page and post login redirect to the home page of the user
@app.route('/login',methods=['GET','POST'])
def login():
	newform=LoginForm()
	if newform.validate_on_submit():
		user=User.query.filter_by(email=newform.email.data).first()
		if user is not None and user.verify_password(newform.password.data):
			login_user(user,newform.remember_me.data)
			if current_user.confirmed is False:
				return render_template('unconfirmed.html',user=current_user)
			current_user.ping()
			return redirect(request.args.get('next') or url_for('user',username=current_user.username))
		flash('Invalid Username or Password')
	return render_template('login.html',form=newform)
	

#create the logout session and redirect to the home page
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('index'))
			
#create the registration page for the new users
@app.route('/register',methods=['GET','POST'])
def register():
	newform=RegistrationForm()
	if newform.validate_on_submit():
		user = User(email=newform.email.data,username=newform.username.data,password=newform.password.data)
		db.session.add(user)
		db.session.commit()
		token=user.generate_confirmation()
		send_email(user.email,'Confirm Account','mail/confirm',user=user,token=token)
		flash('Please confirm the link send to your account')
		return redirect(url_for('login'))
	return render_template('register.html',form=newform)

#the edit profile function
@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
	newform=EditProfile()
	if newform.validate_on_submit():
		current_user.name=newform.name.data
		current_user.location=newform.location.data	
		current_user.about_me=newform.about_me.data
		db.session.add(current_user)
		flash('Profile Updated')
		return redirect(url_for('user',username=current_user.username))
	newform.name.data=current_user.name
	newform.location.data=current_user.location
	newform.about_me.data=current_user.about_me
	return render_template('edit_profile.html',form=newform)
	

#the edit post function
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('The post has been updated.')
		return redirect(url_for('posts', id=post.id))
	form.body.data = post.body
	return render_template('edit_post.html', form=form)
	
	
#the confirmation page for the new registered users
@app.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('index'))
	if current_user.confirm_status(token):
		flash('Account confirmed! You can login now')
	else:
		flash('The confirmation link is invalid or Expired.')
	return redirect(url_for('index'))

#resend the confirmation link to the user
@app.route('/resendconfirm')
@login_required
def resendconfirm():
	token=current_user.generate_confirmation()
	send_email(current_user.email,'Confirm Account','mail/confirm',user=current_user,token=token)
	flash('A new confirmation link is send to your inbox')
	return redirect(url_for('index'))
	
#homepage for each user
@app.route('/user/<username>')
def user(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	return render_template('user.html',user=user)
	
#permanenet link for posts
@app.route('/posts/<int:id>')
def posts(id):
	post=Post.query.get_or_404(id)
	return render_template('post.html',posts=[post])
	

#page not found exception
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404


#internal server error	
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500


