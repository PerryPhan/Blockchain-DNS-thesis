from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/students'

db = SQLAlchemy(app)

# TODO: Create Model for account ( id , fullname, email, password, type, is_deleted )
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(40))
    lname = db.Column(db.String(40))
    pet = db.Column(db.String(40))

    def __init__(self, fname, lname, pet):
        self.fname = fname
        self.lname = lname
        self.pet = pet


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        return render_template('login.html')
    else:
        return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
