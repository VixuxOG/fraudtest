# app/__init__.py
import os
from flask import Flask
from .config import Config
from .extensions import db, login_manager, bcrypt
from datetime import datetime # <--- IMPORT datetime

# ... other imports and extension initializations ...

# Register blueprints AFTER extensions are initialized
from .auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from .main import bp as main_bp
app.register_blueprint(main_bp)

return app