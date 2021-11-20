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
from werkzeug.security import generate_password_hash, check_password_hash
import re

# [ CONSTANT INCLUDE ]-----------------------------------------
from constant import *

# [ DATABASE INCLUDE ]-----------------------------------------
app = Flask(__name__)

# Setting SESSION
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(minutes=30)

# Setting DB
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SESSION_TYPE'] = SESSION_TYPE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={
    'expire_on_commit': False
})
app.config['SESSION_SQLALCHEMY'] = db
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Setting SESSION P2
app.secret_key = hashlib.sha256(SQLALCHEMY_DATABASE_URI.encode()).hexdigest()
Session(app)
