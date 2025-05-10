# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'app.db') # Place db outside app folder
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'uploads')
    ALLOWED_EXTENSIONS = {'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB limit for uploads

    # Artifacts Paths (relative to basedir or absolute)
    ARTIFACTS_DIR = os.path.join(basedir, '..', 'artifacts')
    PREPROCESSOR_FILE = 'upi_fraud_preprocessor.joblib'
    MODEL_FILE = 'best_model.keras'
    FEATURE_LIST_FILE = 'feature_list.json'
    PREDICTION_THRESHOLD = 0.5 # Adjust as needed