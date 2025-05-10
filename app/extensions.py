# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Where to redirect users if they try to access a protected page without logging in
login_manager.login_view = 'auth.login'
# Message flashed when login is required
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info' # Bootstrap class