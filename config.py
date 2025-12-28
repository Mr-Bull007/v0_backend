from os import environ
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    DB_HOST = environ.get('DB_HOST')
    DB_USER = environ.get('DB_USER')
    DB_PASSWORD = environ.get('DB_PASSWORD')
    DB_NAME = environ.get('DB_NAME')
    DB_PORT = environ.get('DB_PORT', '3306')

    # URL-encode password to handle special characters like @, #, etc.
    encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
