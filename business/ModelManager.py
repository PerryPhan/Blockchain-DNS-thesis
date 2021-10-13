from .model.account import Account
from .model.student import Student
from ..app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app.app)
student = Student(db.Model)
account = Account(db.Model)
