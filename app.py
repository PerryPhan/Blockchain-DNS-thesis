#            Phan Dai - N17DCAT013 - D17CQAT01-N - Blockchain DNS 
# -------------------- 1 UI and Basic NEED -------------------------------------
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import math
# -------------------- 2 Blockchain NEED -------------------------------------
from uuid import  uuid4
import random
import threading
import re
import json
from dnschain.dns import dns_layer as dns

# --------- SETTINGS --------------------------------------
# Common 
app = Flask(__name__)
# ID of this Flask app 
APP_NODE = None

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

IP_REGEX_STRING = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
HOSTNAME_REGEX_STRING = '(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]'
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
    PORT_END = 5999
    def __init__(self):
        pass

    def getNetwork(self):
        return models.Nodes.query.filter(models.Nodes.is_deleted == False).all()

    def getActiveNetwork(self):
        return models.Nodes.query.filter(models.Nodes.is_active == True ,models.Nodes.is_deleted == False).all()
    
    def getNodeWithIP(self, ip):
        return models.Nodes.query.filter(
            models.Nodes.ip == ip,
            models.Nodes.is_deleted == False
            ).all()

    def getNodeWithIPAndPort(self, ip, port):
        return models.Nodes.query.filter(
            models.Nodes.ip == ip,
            models.Nodes.port == port,
            models.Nodes.is_deleted == False
            ).first()

    def activeNode(self, node):
        oldNode = node
        if node.is_active != True :
            node.is_active = True
            return self.updateNode(oldNode, node)
        return node

    def inActiveNode(self, node):
        oldNode = node
        if node.is_active != False :
            node.is_active = False
            return self.updateNode(oldNode, node)
        return node

    def handleNodeInformation(self, ip: str, port: int, nodename = '' ):
        # 5 Cases :  
        #   - Empty network  : Create OK 
        #   - New IP : Create OK  
        #   - New port : Create OK  
        #   - Already been active : Search in nodeIP 
        #   - Not been active yet : Active node OK 
        network = self.getNetwork() # Found all node ( not-working status )
        id = str(uuid4()).replace('-', '') 
        if not network : # Empty network, create new
            return self.registerNode(
                id,
                ip, 
                port,
                nodename,
                True
            )
        else : 
            nodeIP = self.getNodeWithIP(ip)
            if not nodeIP : # Don't have this IP in DB, create new  
                return self.registerNode(
                    id,
                    ip, 
                    port,
                    nodename,
                    True
                )   
            nodeIPPort = self.getNodeWithIPAndPort(ip, port) 
            if not nodeIPPort  : # Have this IP but wrong port, create new with random port 
                return self.registerNode(
                    id,
                    ip, 
                    random.randint( self.PORT_START, self.PORT_END ),
                    nodename,
                    True
                ) 
            elif nodeIPPort.is_active == True: # This node already active
                anotherNode = [ node for node in nodeIP if node.is_active == False and node.ip == nodeIPPort.ip] 
                if len(anotherNode) <= 0: # No node same IP spared 
                    return self.registerNode(
                        id,
                        ip, 
                        random.randint( self.PORT_START, self.PORT_END ),
                        nodename,
                        True
                    )
                else : # This node has same IP, different port and haven't used yet
                    self.activeNode(anotherNode[0])
                    anotherNode[0].is_active = True
                    return anotherNode[0], 201
            else: # This node is not used by anyone
                self.activeNode(nodeIPPort)
                nodeIPPort.is_active = True
                return nodeIPPort, 201

    def validateNode(self,node, noCheckDuplicate = False):
        checked = True
        if not node : # check node ( not null )
            checked = False
        if not node.id or len(node.id) > 40 : # check id ( not null, < 40 chars)
            checked = False
        if len(node.nodename) > 64 : # check nodename ( null, 64 chars)
            checked = False
        if not node.ip or len(node.ip) > 16 : # check IP ( not null, 16 chars, match regex )
            checked = False
        else : 
            checked = False if not re.search(IP_REGEX_STRING, node.ip) else True  
        if not node.port or node.port < self.PORT_START or node.port > self.PORT_END : 
            checked = False
        if noCheckDuplicate and self.getNodeWithIPAndPort( node.ip, node.port ): # check duplicate
            checked = False
        return checked 

    def registerNode(self, id: str, ip: str, port: int, nodename = '', is_active = False ):
        node = models.Nodes(
            id = id,
            ip = ip,
            port = port,
            nodename = nodename,
            is_deleted = False,
            is_active = is_active
        )
        if not self.validateNode(node, True):
            return node, 403
        
        try:
            db.session.add(node)
            db.session.commit()
            return node, 200
        except:
            return node, 404

    def updateNode(self, oldNode ,node ):
        if not self.validateNode(oldNode):
            return oldNode,403
            
        try:
            db.session.query(models.Nodes).filter(
                models.Nodes.id == node.id,
                models.Nodes.is_deleted == False
            ).update({
                "ip" : node.ip
                ,"port": node.port
                ,"nodename" : node.nodename 
                ,"is_active": node.is_active
            })
            db.session.commit()
            return node,200
        except:
            return oldNode,404

    def deleteNode(self, node):
        node = models.Nodes.query.filter(
            models.Nodes.id == node.id,
            models.Nodes.is_deleted == False
        ).first()

        if not self.validateNode(node):
            return node, 403
        try:
            node.is_delete = True
            db.session.commit()
            return node, 200 
        except:
            return node, 404

class TransactionBusiness:
    def __init__(self):
        self.transactions = self.getCurrentTransactions() 
        self.badTransactions = []
    
    def getAllTransactions(self):
        return models.Transactions.query.order_by().all()

    # Transactions that haven't had block id 
    def getCurrentTransactions(self):
        return models.Transactions.query.filter( models.Transactions.block_id == None ).all()

    # Transaction must have corrected format of ip, hostname, port
    def validateTransaction(self, transaction):
        checked = True
        if not transaction : # check transaction ( not null )
            checked = False
        if not transaction.hostname or len(transaction.hostname) > 64 : # check hostname ( not null, <= 64 chars)
            checked = False
        else : 
            checked = False if not re.search(HOSTNAME_REGEX_STRING, transaction.hostname) else True
        if not transaction.ip or len(transaction.ip) > 16 : # check IP ( not null, 16 chars, match regex )
            checked = False
        else : 
            checked = False if not re.search(IP_REGEX_STRING, transaction.ip) else True   
        if not transaction.port or transaction.port <= 0 : # check Port ( not null, > 0)
            checked = False
        if not transaction.reward or transaction.reward <= 0 : # check Reward ( not null, > 0):
            checked = False
        return checked

    # New current Transactions 
    def addTransactions(self, hostname:str, ip:str, port=80 ,reward = 10):
        transaction = models.Transactions( 
            hostname = hostname,
            ip= ip,
            port= port,
            reward = reward
        )

        if not self.validateTransaction(transaction, True):
            return transaction, 403
        
        try:
            db.session.add(transaction)
            db.session.commit()
            self.transactions.append(transaction) # Adding to buffer 
            return transaction, 200
        except:
            return transaction, 404

    
    # No update, delete cause every transaction is unique 

class BlockchainBusiness:
    def __init__(self, node_id ):
        self.node_id = node_id
        self.transactionBusiness = TransactionBusiness()
        self.chain = self.getChain() # Must be load from DB 

    def getChain(self):
        return models.Blocks.query.order_by(models.Blocks.id).all()

    @property 
    def wallet(self): 
        chain = self.chain
        wallet = 10 # Start with 10    

        if len(chain) <= 0 : return wallet
        
        # Get only block which has correct node id 
        for block in [block for block in chain if block.node_id == self.node_id]:          
            for transaction in block.transactions:
                wallet += transaction.reward
        return wallet
    
    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def current_transactions(self):
        return self.transactionBusiness.transactions
    
    @property
    def all_transactions(self):
        return self.transactionBusiness.getAllTransactions()

    # Proof_of_work
    #  sub - Number_generator 

    # Proof_of_work
    def proof_of_work(self, last_proof):
        salt_gen = self.salt_generator()
        salt = next(salt_gen)
        while not self.valid_proof(last_proof,salt):
            salt = next(salt_gen)
        print("POW generated")
        return salt
        
    # Static Override function
    @staticmethod
    def salt_generator(self):
        num = 0
        while True:
            yield num
            num += 1
            if num%100 == 0:
                print("Generating salt...")
    
    # Resolve_conflicts 
    # Tạo
    # Sửa 
    # Tải
    # Thống kê

    def getDomainSet(self):
        # Get source from all Transactions 
        # Get rid of same transactions
        # -> sub-query, group by hostname
        # TODO : Need to read reference again
        return set(self.all_transactions)

class DNSBusiness: 
    def __init__(self):
        self.BUFFER_MAX_LEN = 20
        self.MINE_REWARD = 10
        self.blockchain = BlockchainBusiness()
        pass

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
    # Client don't have permission to go here
    if protectedAccount.type_cd == 3 : return redirect('/table')
    # Pagination
    paginationHelper = PaginationHelper(3,13)
    page = request.args.get('page', default = 1, type = int)
    totalPageNumber = paginationHelper.getCeilingNumber()
    arrayOfIndexingData = paginationHelper.arrayOfIndexingData
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
    from argparse import ArgumentParser
    import atexit
    import socket
    print( 'Data is processing please wait ... ')
    def onClosingNode():    
        if APP_NODE:
            nodeBusiness.inActiveNode(APP_NODE)
            print (f"\n-------- NODE {APP_NODE.id} IS INACTIVE ------")
            print ("-------- GOODBYE !! ------")
    atexit.register(onClosingNode)
    # ------------------------------- 
    parser = ArgumentParser()
    # ------------------------------- 
    parser.add_argument('-host', '--host', default='', type=str, help='IPv4 string in your network or blank in default')
    parser.add_argument('-p', '--port', default=5000, type=int, help='Port Number to listen on or auto-handle in default')
    args = parser.parse_args()
    # -------------------------------   
    port = args.port 
    host = args.host or socket.gethostbyname(socket.gethostname()) 
    # Khai báo node
    APP_NODE, code = nodeBusiness.handleNodeInformation(host, port)
    dns_resolver = dns(node_identifier = APP_NODE.id)
    print('OK')
    if code == 200 : 
        print( '//----------------------------------------//' )
        print( ' WELCOME NODE ', APP_NODE.id )
        print( '//----------------------------------------//' )
        app.run(host=APP_NODE.ip, port = APP_NODE.port,  debug=True, use_reloader=False)
    elif code == 201 :
        print( '//----------------------------------------//' )
        print( ' WELCOME BACK NODE ', APP_NODE.id )
        print( '//----------------------------------------//' )
        app.run(host=APP_NODE.ip, port = APP_NODE.port,  debug=True, use_reloader=False)
    else :
        print( 'WRONG INFORMATION !! PLEASE TRY AGAIN WITH OTHER VALID HOSTNAME OR PORT' )
        print( 'Port must be from [ 5000, 5999] ' )
        print( 'Hostname must have right format of IPv4 ' )
    
