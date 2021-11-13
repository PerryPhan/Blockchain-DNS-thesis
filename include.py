from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import timedelta

# [ TEMP INCLUDE ]-----------------------------------------
import os
import json
import hashlib
from copy import copy
from werkzeug.utils import secure_filename
import re



# [ DATABASE INCLUDE ]-----------------------------------------
app = Flask(__name__)
# Setting SESSION
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(minutes=30)

# Setting DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/dnschain'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options = {
    'expire_on_commit': False
})

app.config['SESSION_SQLALCHEMY'] = db

# Setting SESSION P2
app.secret_key = 'super secret key'
Session(app)



UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


