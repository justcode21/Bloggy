from app import app

app.config['POST_PER_PAGE']=5
app.config['MAIL_SERVER']='smtp.gmail.com'
#username and password of the sender's account
#we can use os.environ.get() to get the valuse from the environment variables of the system

app.config['MAIL_USERNAME'] = 'psrivast7788@gmail.com'#os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = 'xxxzzzxxx'#os.environ.get('MAIL_PASSWORD')

#username of the reciver or the admin in this case
app.config['BLOGGY_ADMIN']='juststartedcd@gmail.com'#os.environ.get('FLASKY_ADMIN')

app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['BLOGGY_MAIL_SUBJECT_PREFIX'] = '[BLOGGY]'
app.config['BLOGGY_MAIL_SENDER'] = 'Bloggy Admin <bloggy@example.com>'
