from flask import Blueprint
bp = Blueprint('main', __name__) # Define bp FIRST
from . import routes # Import routes AFTER bp is defined
from . import utils # Import utils if needed elsewhere, often not needed here