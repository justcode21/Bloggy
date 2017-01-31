from flask import Flask
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#from flask_script import Manager
from config import *

#create various objects
app=Flask(__name__)
#manager=Manager(app)
bootstrap=Bootstrap(app)
moment=Moment(app)
db = SQLAlchemy(app)
login_manager=LoginManager(app)


from databases import *
mail=Mail(app)
from models import *
db.create_all()
from views import *
from forms import *
if __name__=='__main__':
	app.run(debug=True)

