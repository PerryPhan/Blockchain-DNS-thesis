from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import redirect
from business.model.account import AccountSchema

# --------- SETTINGS --------------------------------------
app = Flask(__name__)

# Setting SESSION
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/dnschain2'
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

    def validateLogin(self, request):
        email = request.form.get(AccountSchema.EMAIL)
        password = request.form.get(AccountSchema.PASSWORD)
        account = Account.query.filter(Account.email == email).all()
        # print("Account: ", account[0].password)
        if(account[0].password == password):
            return True
        return False

    def validateRegister(self, request):
        fullname = request.form.get(AccountSchema.FULLNAME)
        email = request.form.get(AccountSchema.EMAIL)
        password = request.form.get(AccountSchema.PASSWORD)
        repassword = request.form.get(AccountSchema.REPASSWORD)
        type_cd = request.form.get(AccountSchema.TYPE_CD)
        # print("Fullname : ",fullname)
        # print("Email : ",email)
        # print("Password : ",password)
        # print("RePassword : ",repassword)
        # print("Type code : ",type_cd)
        isPassed = False
        isPassed = type_cd != None
        isPassed = password == repassword 
        # print('Validating register: ', isPassed)
        return isPassed

    def onReturn(self, data ) :
        if data != None : data.password = None
        response = {
            'isSuccess' : True,
            'data' : data,
            'error' : None 
        }
        # print('Success: ', response['isSuccess'])
        # print('Data : ', data.email)
        return response

    def onError(self ,data ,error_message ):
        if data != None : data.password = None
        response = {
            'isSuccess' : False,
            'data' : data,
            'error' : error_message 
        }
        # print('Success: ', response['isSuccess'])
        # print('Error Message : ', error_message)
        return response

    def insert(self, request, resolve, reject):
        # TODO : set error message in Dist
        insertErrorMessage = '[E0100001] Error in inserting account' 
        insertEmptyErrorMessage = '[E0100002] Data not match' 
        if  resolve == None or reject == None or request == None : 
            return reject( None , insertEmptyErrorMessage )
        newAccount = Account(
            fullname=request.form.get(AccountSchema.FULLNAME),
            email=request.form.get(AccountSchema.EMAIL),
            password=request.form.get(AccountSchema.PASSWORD),
            type_cd= int(request.form.get(AccountSchema.TYPE_CD)),
            is_deleted=False,
        )
        if  not self.validateRegister(request):
            return reject( newAccount , insertEmptyErrorMessage )

        try:
            # db.session.add( newAccount )
            # db.session.commit()
            return resolve( newAccount )
        except:
            return reject( newAccount, insertErrorMessage )

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
        response = accountBusiness.insert(request, accountBusiness.onReturn , accountBusiness.onError)
        error = response['error']
        data = response['data']
        isSuccess = response['isSuccess']
        if response['isSuccess'] :
            return render_template('login.html', error = error, data = data, isSuccess = isSuccess)
        else: 
            # print ('Data: ', error,data,isSuccess)
            # print ('Type_cd: ',data.type_cd)
            return render_template('register.html', error = error, email = data.email, fullname = data.fullname, type_cd = data.type_cd, isSuccess = isSuccess)
    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # TODO : Encoding password & tokens maybe 
        isPassed = accountBusiness.validateLogin(request)
        # print('isPassed from Login page : ',isPassed)
        if isPassed:
            session['email'] = request.form.get(AccountSchema.EMAIL)
            return redirect('/')   
        return render_template('login.html')
    else:
        return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
