#            Phan Dai - N17DCAT013 - D17CQAT01-N - Blockchain DNS 
# -------------------- 1 UI and Basic NEED -------------------------------------
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask.scaffold import F
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.orm import backref
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import math
# -------------------- 2 Blockchain NEED -------------------------------------
from uuid import uuid4
import threading
import re
import json
from dnschain.dns import dns_layer as dns

# --------- SETTINGS --------------------------------------
# Common 
app = Flask(__name__)
app.config['SERVER_NAME'] = 'dai:5000'
# ID of this Flask app 
node_identifier = str(uuid4()).replace('-', '') 

# Setting SESSION
app.config['SESSION_PERMANENT'] = True
app.permanent_session_lifetime = timedelta(minutes=30)

# Setting DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/dnschain'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db

# Setting SESSION P2
app.secret_key = 'super secret key'
Session(app)

# --------- SCHEMA -------------------------------------
from schema.AccountSchema import AccountSchema
from schema.DomainSchema import DomainSchema
# --------- MODELS --------------------------------------
import models
# --------- BUSINESS -----------------------------------
class AccountBusiness:
    def __init__(self):
        pass

    def selectAll(self):
        return models.Accounts.query.order_by(models.Accounts.id).all()

    def validateLoginOrReturnErrorCode(self, request):
        email = request.form.get(AccountSchema.EMAIL)
        password = request.form.get(AccountSchema.PASSWORD)
        accounts = models.Accounts.query.filter(models.Accounts.email == email).all()
        # print("models.Accounts: ", account[0].password)
        if accounts :
            if password and check_password_hash(accounts[0].password, password):
                return True
            else:
                return 'LO010001'

        return 'LO010002'

    def getProtectedAccount(self, email):
        account = models.Accounts.query.filter(
            models.Accounts.email == email, models.Accounts.is_deleted == False).first()
        if account : 
            return account
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
        accounts = models.Accounts.query.filter(
            models.Accounts.email == email, models.Accounts.is_deleted == False).all()
        return len(accounts) if len(accounts) > 0 else True

    def insert(self, request, resolve, reject):
        if resolve == None or reject == None or request == None:
            return reject(None, 'RE010002')
        newAccount = models.Accounts(
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
        updatedAccount = models.Accounts.query.get_or_404(id)

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
        deleteAccount = models.Accounts.query.get_or_404(id)

        try:
            db.session.delete(deleteAccount)
            db.session.commit()
            return resolve(deleteAccount)
        except:
            return reject()

class NodesBusiness:
    PORT_START = 5000 
    PORT_END = 50000
    def __init__(self):
        pass

    def getNetwork(self):
        return models.Nodes.query.filter(models.Nodes.is_deleted == False).all()

    def getNode(self, ip, port):
        return models.Nodes.query.filter(
            models.Nodes.ip == ip,
            models.Nodes.port == port,
            models.Nodes.is_deleted == False
            ).first()

    def validateNode(self,node):
        checked = True
        if not node :
            checked = False
        if not node.id or len(node.id) > 40 : 
            checked = False
        if not node.nodename or len(node.nodename) > 64 :
            checked = False
        if not node.ip or len(node.ip) > 16 : 
            checked = False
        else : 
            checked = False if not re.search('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', node.ip) else True  
        if not node.port or node.port <= self.PORT_START or node.port > self.PORT_END : 
            checked = False
        if self.getNode( node.ip, node.port ): 
            checked = False
        return checked 

    def registerNode(self, id, ip, port, nodename = ''):
        node = models.Nodes(
            id = id,
            ip = ip,
            port = port,
            nodename = nodename,
            is_deleted = False
        )
        if not self.validateNode(node):
            return node, 403
        
        try:
            db.session.add(node)
            db.session.commit()
            return node, 200
        except:
            return node, 404

    def updateNode(self, node):
        if not self.validateNode(node):
            return node, 403
            
        try:
            db.session.commit()
            return node, 200
        except:
            return node, 404

    def stopNode(self, node):
        if not self.validateNode(node):
            return node, 403
        try:
            db.session.delete(node)
            db.session.commit()
            return node, 200 
        except:
            return node, 404

# class TransactionBusiness
# class BlockchainBusiness

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
nodeBusiness = NodesBusiness()

# --------- #1. UI ROUTERS --------------------------------------
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

# --------- #2. API ROUTERS --------------------------------------
# Make a DNS layer as resolver - as communicator between Server and Blockchain
dns_resolver = dns(node_identifier = node_identifier)

# Route 1: Make sure this node is working - Need when init  
@app.route('/debug/alive',methods=['GET'])
def check_alive():
	response = 'The node is alive'
	return  jsonify(response),200

# Route 2: Registry a node (Machine) to network - Need when init
@app.route('/nodes/new',methods=['POST'])
def register_node():
	"""
	Calls underlying functions to register new node in network
	"""
	values = request.get_json()
	nodes = values.get('nodes')

	if nodes is None:
		# Nếu không có giá trị gì gửi lên sẽ trả STATUS CODE 400 
		response, return_code = "No node supplied",400
	else:
		for node in nodes:
			# DNS resolver tạo node mới 
			dns_resolver.register_node(node)
		
		# Nếu thêm thành công sẽ trả STATUS CODE 201 và message 	
		response, return_code = {
			'message': 'New nodes have been added',
			'total_nodes': dns_resolver.get_network_size(),
		}, 201

	return jsonify(response),return_code

# Route 3: Add more new DNS - insert code when request POST in /storage 
@app.route('/dns/new',methods=['POST'])
def new_transaction():
	"""
	adds new entries into our resolver instance
	"""
	values = request.get_json()
	# print(values)
	required = ['hostname', 'ip', 'port']
	bad_entries = []

	for value in values:
		#print(k in values[value] for k in required)
		if all(k in values[value] for k in required):
			value = values[value]
			# Nếu các key của giá trị request trùng với các key của required thì sẽ được tạo mới
			dns_resolver.new_entry(value['hostname'],value['ip'],value['port'])
		else:
			bad_entries.append(value)

	if bad_entries:
		return jsonify(bad_entries),400
	else:
		response = 'New DNS entry added'
		return jsonify(response), 201

# Route 4: Sending request to resolver and receive response with data - need to change the table
@app.route('/dns/request',methods=['POST'])
def dns_lookup():
	"""
	receives a dns request and responses after resolving
	"""
	values = request.get_json()
	required = ['hostname']
	if not all(k in values for k in required):
		return 'Missing values', 400

	try:
		# Gửi giá trị của thuộc tính hostname cho DNS resolver để tìm kiếm
		host, port = dns_resolver.lookup(values['hostname'])
		response = {
			'ip':host,
			'port': port
		}
		return_code = 200
	except LookupError:
		response = "No existing entry"
		return_code = 401
	
	# Tìm thấy thì 200 , không thì 401 
	return jsonify(response), return_code

# Route 5: Solving node's conflict from change
@app.route('/nodes/resolve',methods=['GET'])
def consensus():
	"""
	triggers the blockchain to check chain against other neighbors'
	chain, and uses the longest chain to achieve consensus ( đoàn kết )
	"""
	t = threading.Thread(target=dns_resolver.blockchain.resolve_conflicts)
	t.start()

	return jsonify(None), 200

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    # Khi chạy chương trình, -> tự động thêm node vào Database
    # Nếu node đó trùng ip trùng port thì sao ? -> Update port mới 
    # Nếu node đó trùng ip khác port thì sao ? -> Dùng luôn 
    # Nếu node đó khác ip khác port thì sao ? -> Thêm node
    # ------------------------------- 
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    
    args = parser.parse_args()
    port = args.port
    # node = models.Node(
        
    # )
    app.run(host='0.0.0.0', port = port,  debug=True)
