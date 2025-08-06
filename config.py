import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///food_manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AZURE_VISION_KEY = os.environ.get('AZURE_VISION_KEY')
    AZURE_VISION_ENDPOINT = os.environ.get('AZURE_VISION_ENDPOINT')
    AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
    AZURE_SPEECH_REGION = os.environ.get('AZURE_SPEECH_REGION')
    # RECIPE_API_KEY = os.environ.get('RECIPE_API_KEY')
    RECIPE_API_KEY = "a2e31ae104b447c6b484a1a737bd1052"
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    AZURE_MAPS_KEY = os.environ.get('AZURE_MAPS_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

