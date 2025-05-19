from flask import Blueprint
bp = Blueprint('auth', __name__) # Define bp FIRST
from . import routes # Import routes AFTER bp is defined
from . import forms # Import forms if needed elsewhere