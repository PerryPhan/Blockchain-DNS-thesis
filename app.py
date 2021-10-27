from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import redirect
from business.model.account import AccountSchema
from business.model.domainvalue import DomainSchema
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import math
import json
# --------- SETTINGS --------------------------------------
app = Flask(__name__)

# Setting SESSION
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(minutes=30)
# Setting DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/dnschain'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
# Setting SESSION 2
app.secret_key = 'super secret key'
Session(app)

# --------- MODELS --------------------------------------

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(255), nullable=False)
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

    def validateLoginOrReturnErrorCode(self, request):
        email = request.form.get(AccountSchema.EMAIL)
        password = request.form.get(AccountSchema.PASSWORD)
        accounts = Account.query.filter(Account.email == email).all()
        # print("Account: ", account[0].password)
        if accounts :
            if password and check_password_hash(accounts[0].password, password):
                return True
            else:
                return 'LO010001'

        return 'LO010002'

    def getProtectedAccount(self, email):
        account = Account.query.filter(
            Account.email == email, Account.is_deleted == False).all()
        if account : 
            return account[0]
        else: 
            return None

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
        if password != repassword:
            return False
        if type_cd == 0:
            return False
        # print('Validating register: ', isPassed)
        return True

    def onReturn(self, data):
        response = {
            'isSuccess': True,
            'data': data,
            'message': AccountSchema.message['RE01XXXX']
        }
        # print('Success: ', response['isSuccess'])
        # print('Data : ', data.email)
        return response

    def onError(self, data, message_cd):
        response = {
            'isSuccess': False,
            'data': data,
            'message': AccountSchema.message[message_cd]
        }
        # print('Success: ', response['isSuccess'])
        # print('Error Message : ', error_message)
        return response

    def encodingPassword(self, password):
        return generate_password_hash(password)

    def checkDuplicatingAccount(self, email):
        accounts = Account.query.filter(
            Account.email == email, Account.is_deleted == False).all()
        return len(accounts) if len(accounts) > 0 else True

    def insert(self, request, resolve, reject):
        if resolve == None or reject == None or request == None:
            return reject(None, 'RE010002')
        newAccount = Account(
            fullname=request.form.get(AccountSchema.FULLNAME),
            email=request.form.get(AccountSchema.EMAIL),
            password=self.encodingPassword(
                request.form.get(AccountSchema.PASSWORD)),
            type_cd=int(request.form.get(AccountSchema.TYPE_CD) or '0'),
            is_deleted=False,
        )
        if not self.validateRegister(request):
            return reject(newAccount, 'RE010003')

        if not self.checkDuplicatingAccount(newAccount.email):
            return reject(newAccount, 'RE010004')

        try:
            db.session.add(newAccount)
            db.session.commit()
            return resolve(newAccount)
        except:
            return reject(newAccount, 'RE010001')

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

# --------- HELPER ------------------------------------
class PaginationHelper:
    def __init__(self, perPage, numberOfData ):
        self.perPage = perPage
        self.numberOfData = numberOfData
        self.arrayOfIndexingData = self.getArrayOfIndexingData()
    
    def getCeilingNumber(self):
        return math.ceil(self.numberOfData / self.perPage)

    def getArrayOfIndexingData(self):
        n = self.getCeilingNumber()
        arrayOfIndexing = []
        for x in range(n):
            distance = (x)*self.perPage + self.perPage 
            toValue = distance if distance <= self.numberOfData else self.numberOfData 
            arrayOfIndexing.append( { 
                'from' : (x)*self.perPage,
                'to' : toValue
            } )
        return arrayOfIndexing

# --------- INIT --------------------------------------
accountBusiness = AccountBusiness()
# --------- ROUTERS --------------------------------------

@app.route('/')
def home():
    if session and session.get("protected_account"):
        type_cd = session.get("protected_account").type_cd
        if type_cd and type_cd != 1: #ADMIN
            return redirect('/table')
        else : 
            return render_template('index.html')
    else:
        return redirect('/login')

@app.route('/table', methods=['POST','GET'])
def table():
    if not session or not session.get("protected_account"):
        return redirect('/login')
    if request.method == 'POST':
        pass
    else :
        protectedAccount = session.get("protected_account")
        # Pagination
        paginationHelper = PaginationHelper(12,13)
        page = request.args.get('page', default = 1, type = int)
        totalPageNumber = paginationHelper.getCeilingNumber()
        arrayOfIndexingData = paginationHelper.arrayOfIndexingData
        page = totalPageNumber if page >= totalPageNumber else page
        # print( json.dumps(arrayOfIndexingData) )
        paginationObj = {
            'page': page,
            'totalPageNumber': totalPageNumber,
            'from': arrayOfIndexingData[page-1]['from'],
            'to': arrayOfIndexingData[page-1]['to']
        } 
        # print(page)
        # print(totalPageNumber)
        # for i in range(len(arrayOfIndexingData)):
        #     print( json.dumps( arrayOfIndexingData[i] ) )

        return render_template('table.html', protectedAccount = protectedAccount, paginationObj = paginationObj )

@app.route('/storage', methods=['POST','GET'] )
def storage():
    if not session or not session.get("protected_account"):
        return redirect('/login')
    if request.method == 'POST':
        domainName = request.form.get(DomainSchema.DOMAINNAME)
        ipAddress = request.form.get(DomainSchema.IPADDRESS)
        hosterName = request.form.get(DomainSchema.HOSTER)
        status = request.form.get(DomainSchema.STATUS)
        createdDate = request.form.get(DomainSchema.CREATEDDATE)
        # TODO : THINKING WORKING BLOCKCHAIN
        return domainName + " " + ipAddress + " " + hosterName + " " + status + " " + createdDate

    protectedAccount = session.get("protected_account")
    # Pagination
    paginationHelper = PaginationHelper(3,13)
    page = request.args.get('page', default = 1, type = int)
    totalPageNumber = paginationHelper.getCeilingNumber()
    arrayOfIndexingData = paginationHelper.arrayOfIndexingData
    print( json.dumps(arrayOfIndexingData) )
    page = totalPageNumber if page >= totalPageNumber else page
    paginationObj = {
        'page': page,
        'totalPageNumber': totalPageNumber,
        'from': arrayOfIndexingData[page-1]['from'],
        'to': arrayOfIndexingData[page-1]['to']
    } 
    return render_template('storage.html', protectedAccount = protectedAccount, paginationObj = paginationObj)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        response = accountBusiness.insert(
            request, accountBusiness.onReturn, accountBusiness.onError)
        message = response['message']
        data = response['data']
        isSuccess = response['isSuccess']
        if response['isSuccess']:
            return render_template('login.html', email=data.email)
        else:
            # print ('Data: ', error,data,isSuccess)
            # print ('Type_cd: ',data.type_cd)
            return render_template('register.html', message=message, email=data.email, fullname=data.fullname, type_cd=data.type_cd, isSuccess=isSuccess)
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        isPassedOrErrorCode = accountBusiness.validateLoginOrReturnErrorCode(request)
        if isPassedOrErrorCode == True:
            session['email'] = request.form.get(AccountSchema.EMAIL)
            session['protected_account'] = accountBusiness.getProtectedAccount(session.get('email'))
            return redirect('/')
        else : 
            return render_template('login.html', email=request.form.get(AccountSchema.EMAIL), message=AccountSchema.message[isPassedOrErrorCode], isSuccess=False)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('protected_account', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
