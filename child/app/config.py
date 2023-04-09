#! /Users/droom/Documents/codeshastra_lambda/nenv/bin/python3 
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
#export MONGO_HOST='mongodb+srv://admin_cs:yourpass123@cluster0.gygw6us.mongodb.net/?retryWrites=true&w=majority'
class Config:
    THREADS_PER_PAGE = 2
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'sdansdajsd2@1s1nkn;Sad;0@121('
    
    # MongoDB Stuff
    MONGODB_SETTINGS = {
        "db": "testtest",
        "host": os.environ.get('MONGO_HOST')
    }

    # JWT Stuff
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_SECRET_KEY = "asd89123bkbaksd12" # TODO: Use env vars
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=5)
    JWT_HEADER_NAME = "auth"