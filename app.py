from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import redirect
from business.model.account import AccountSchema
import json

# --------- SETTINGS --------------------------------------
app = Flask(__name__)
# Setting SESSION
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/students'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)
# Setting DB
db = SQLAlchemy(app)


# --------- MODELS --------------------------------------
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(), nullable=False)
    type_cd = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)

    def __init__(self, fullname, email, password, type_cd, is_deleted):
        self.fullname = fullname
        self.email = email
        self.password = password
        self.type_cd = type_cd
        self.is_deleted = is_deleted
# --------- BUSINESS -----------------------------------
class AccountBusiness:
    def __init__(self):
        pass

    def selectAll(self):
        return Account.query.order_by(Account.id).all()

    def validate(self, request):
        email = request.form.get(AccountSchema.EMAIL)
        password = request.form.get(AccountSchema.PASSWORD)
        account = Account.query.filter(Account.email == email).all()
        # print("Account: ", account[0].password)
        if(account[0].password == password):
            return True
        return False

    def insert(self, request, resolve, reject):
        newAccount = Account(
            fullname=request.form.get(AccountSchema.FULLNAME),
            email=request.form.get(AccountSchema.EMAIL),
            password=request.form.get(AccountSchema.PASSWORD),
            type_cd=request.form.get(AccountSchema.TYPE_CD),
            is_deleted=False,
        )
        try:
            db.session.add(newAccount)
            db.session.commit()
            return resolve(newAccount)
        except:
            return reject()

    def update(self, id, request, resolve, reject):
        updatedAccount = Account.query.get_or_404(id)
        
        if(updatedAccount.fullname != request.form.get(AccountSchema.FULLNAME) and request.form.get(AccountSchema.FULLNAME) != None):
            updatedAccount.fullname = request.form.get(AccountSchema.FULLNAME)

        if(updatedAccount.email != request.form.get(AccountSchema.EMAIL) and request.form.get(AccountSchema.EMAIL) != None):
            updatedAccount.email = request.form.get(AccountSchema.EMAIL)

        if(updatedAccount.password != request.form.get(AccountSchema.PASSWORD) and request.form.get(AccountSchema.PASSWORD) != None):
            updatedAccount.password = request.form.get(AccountSchema.PASSWORD)

        if(updatedAccount.type_cd != request.form.get(AccountSchema.TYPE_CD) and request.form.get(AccountSchema.TYPE_CD) != None):
            updatedAccount.type_cd = request.form.get(AccountSchema.TYPE_CD)

        try:
            db.session.commit()
            return resolve(updatedAccount)
        except:
            return reject()

    def delete(self, id, resolve, reject):
        deleteAccount = Account.query.get_or_404(id)
        
        try:
            db.session.delete(deleteAccount)
            db.session.commit()
            return resolve(deleteAccount)
        except:
            return reject()
# --------- INIT --------------------------------------
accountBusiness = AccountBusiness()
# --------- ROUTERS --------------------------------------
@app.route('/')
def home():
    if not session.get("email"):
        return redirect('/login')
    else :
        return 'Someone is Logged'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        return render_template('register.html')
    else:
        return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # TODO : authentication with AccountBusiness.validate
        isPassed = accountBusiness.validate(request)
        # print('isPassed from Login page : ',isPassed)
        if isPassed:
            session['email'] = request.form.get(AccountSchema.EMAIL)
            return redirect('/')   
        return render_template('login.html')
    else:
        return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
