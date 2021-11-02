#            Phan Dai - N17DCAT013 - D17CQAT01-N - Blockchain DNS 
# -------------------- 1 UI and Basic NEED -------------------------------------
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.datastructures import D
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import math
# -------------------- 2 Blockchain NEED -------------------------------------
from uuid import  uuid4
import random
import requests
import threading
import re
import json
import hashlib
import time

from werkzeug.wrappers import response
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
class Accounts(db.Model): 
    __tablename__ = 'accounts'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    type_cd = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)
    # ============== 
    transactions = db.relationship('Transactions',backref="owner")

class Nodes(db.Model):
    __tablename__ = 'nodes'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.String(40), primary_key=True)
    nodename = db.Column(db.String(64), nullable=True)
    ip = db.Column(db.String(16), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    # ============== 
    blocks = db.relationship('Blocks', backref="node")

class Transactions(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), nullable=True)
    ip = db.Column(db.String(16), nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    # ============== 
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    
class Blocks(db.Model):
    __tablename__ = 'blocks'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    nonce = db.Column(db.Integer, nullable=False)
    previous_hash = db.Column(db.String(255), nullable=False)
    # ===============
    node_id = db.Column(db.String(64), db.ForeignKey('nodes.id'))
    transactions = db.relationship('Transactions',backref="block")

# --------- BUSINESS -----------------------------------
class AccountBusiness:
    def __init__(self):
        pass

    def selectAll(self):
        return Accounts.query.order_by(Accounts.id).all()

    def validateLoginOrReturnErrorCode(self, request):
        email = request.form.get(AccountSchema.EMAIL)
        password = request.form.get(AccountSchema.PASSWORD)
        accounts = Accounts.query.filter(Accounts.email == email).all()
        # print("Accounts: ", account[0].password)
        if accounts :
            if password and check_password_hash(accounts[0].password, password):
                return True
            else:
                return 'LO010001'

        return 'LO010002'

    def getProtectedAccount(self, email):
        account = Accounts.query.filter(
            Accounts.email == email, Accounts.is_deleted == False).first()
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
        accounts = Accounts.query.filter(
            Accounts.email == email, Accounts.is_deleted == False).all()
        return len(accounts) if len(accounts) > 0 else True

    def insert(self, request, resolve, reject):
        if resolve == None or reject == None or request == None:
            return reject(None, 'RE010002')
        newAccount = Accounts(
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
        updatedAccount = Accounts.query.get_or_404(id)

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
        deleteAccount = Accounts.query.get_or_404(id)

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
        return Nodes.query.filter(Nodes.is_deleted == False).all()

    def getActiveNetwork(self):
        return Nodes.query.filter(Nodes.is_active == True ,Nodes.is_deleted == False).all()
    
    def getNodeWithIP(self, ip):
        return Nodes.query.filter(
            Nodes.ip == ip,
            Nodes.is_deleted == False
            ).all()

    def getNodeWithIPAndPort(self, ip, port):
        return Nodes.query.filter(
            Nodes.ip == ip,
            Nodes.port == port,
            Nodes.is_deleted == False
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
        node = Nodes(
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
            db.session.query(Nodes).filter(
                Nodes.id == node.id,
                Nodes.is_deleted == False
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
        node = Nodes.query.filter(
            Nodes.id == node.id,
            Nodes.is_deleted == False
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
        self.alltransactions = self.getAllTransactions()
        self.transactions = self.getCurrentTransactions() # -> These are transactions that not in block yet 
        self.badTransactions = []
    
    def getAllTransactions(self):
        return Transactions.query.order_by().all()

    # Transactions that haven't had block id 
    def getCurrentTransactions(self):
        return Transactions.query.filter( Transactions.block_id == None ).all()

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
    def addTransactions(self, hostname:str, ip:str, port= 80 ,reward = 10):
        transaction = Transactions( 
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

    # Get Domain List
    def getDomainNamesList(self):
        if len(self.alltransactions) == 0 : 
            return []
        noDuplicateAndSortedSet = set( [ trans.hostname for trans in self.alltransactions ] )
        return [ hostname for hostname in noDuplicateAndSortedSet ]
    
    # Search Domain due to domainName
    def searchDomainInformation(self, domainName):
        result = [ trans for trans in self.alltransactions if trans.hostname == domainName]
        return result
    
    # No update, delete cause every transaction is unique 

class BlockchainBusiness:
    def __init__(self ):
        self.node_id = None
        self.nodeBusiness = NodesBusiness()
        self.chain = self.loadChain( ) # Must be load from DB 

    def configNodeID( self, node_id ):
        self.node_id = node_id

    def getGenesisBlock( self ):
        return Blocks(
            id = '1',
            timestamp = '1',
            nonce = 1,
            previous_hash = '0'*255,
            node_id = self.node_id,
            transactions = None
        )

    def loadChain(self):
        result = [self.getGenesisBlock()]
        blocksDBList = Blocks.query.order_by(Blocks.id).all()
        if len(blocksDBList) > 0 :
            return [ result.append(block) for block in blocksDBList ] 
        return result

    # 1. Quota - all rewards in blockchain
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
    
    # 2. Get the last block
    @property
    def last_block(self):
        return self.chain[-1]

    # 3. Proof of works support : Generate Nonce  
    @staticmethod
    def saltGenerator():
        num = 0
        while True:
            yield num
            num += 1
            if num%100 == 0:
                print("Generating salt...")
    
    # 4. Proof of works support : check if last_proof and proof hash will be '00xxx'  
    @staticmethod
    def validateProof( last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # Kiểm tra việc encode last_proof và proof với nhau có ra "00xxx" không 
        return guess_hash[:2] == "00"
   
    # 5. Proof of work
    def proofOfWork(self, last_proof):
        salt_gen = self.saltGenerator()
        salt = next(salt_gen)
        while not self.validateProof(last_proof,salt):
            salt = next(salt_gen)
        print("POW generated")
        return salt

    # 6. Resolve_conflicts : Overide the longest chain in whole network 
    def resolveConflicts(self):
        network = self.nodeBusiness.getNetwork()
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in network:
            # TODO: Create route for solving conflict 
            node_addr = f'http://{node.ip}/nodes/chain'
            response = requests.get(node_addr)

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.validateChain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    # 7. Resolve conflicts support : Validate each block in longest chain
    def validateChain( self, chain):
        previous_block = chain[0]
        current_index = 1

        while current_index < len(self.chain):
            block = chain[current_index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False

            if not self.validateProof( previous_block.nonce, block.nonce ):
                return False
            
            previous_block = block
            current_index += 1

        return True

    # 8. Creating Block  
    def newBlock(self, transactions, proof, previous_hash):
        # Declare new Block 
        block = Blocks(
            id = len(self.chain) + 1,
            node_id = self.node_id,
            timestamp = time(),
            transactions = transactions,
            nonce = proof,
            previous_hash = previous_hash or self.hash(self.chain[-1]),
        )
        # Free transactions - DNS 
        # Get last Block 
        self.chain.append(block)
        # Proof of Work 
        try: 
            db.session.add(block)
            db.session.commit()
            return block, 200
        except:
            return block, 404
    
    # 9. Mining Block
    def miningBlock(self, transactions):
        last_block = self.last_block
        last_block_nonce = last_block.nonce
        last_block_hash = self.hash(last_block)
        
        
        pass

    # SHA hashing function
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class DNSBusiness: # This class will interact with request
    def __init__( self ):
        self.MINE_REWARD = 10
        self.BUFFER_MAX_LEN = 20
        self.transactionBusiness = TransactionBusiness()
        self.blockchainBusiness = BlockchainBusiness()
        pass

    def configNodeID( self, node_id ): 
        self.blockchainBusiness.configNodeID( node_id )
    
    def getDomainNamesList( self ):
        return self.transactionBusiness.getDomainNamesList()

    def resolveDomainName( self, domainName ):
        domainInformation = self.transactionBusiness.searchDomainInformation(domainName)
        return domainInformation[0].ip , domainInformation[0].port
    
    def getBlockChain( self ):
        return {
            'chain': self.blockchainBusiness.chain,
            'length': len(self.blockchainBusiness.chain)    
        }
    
    def registerDNS( self, hostname, ip, port ):
        # Add transaction -> TransactionBusiness
        self.transactionBusiness.addTransactions(hostname,ip,port, self.MINE_REWARD ) 
        buffer_len = len( self.transactionBusiness.transactions )
        # Transaction Quantity is larger than MAX_LEN or don't have money to pay failed block in worst decision
        if buffer_len >= self.BUFFER_MAX_LEN or buffer_len >= self.blockchainBusiness.wallet - self.BUFFER_MAX_LEN:
            # Start mining 
            pass
            # return Status code 
        return 0

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
dnsBusiness = DNSBusiness()

# --------- #1. UI ROUTERS --------------------------------------
@app.route('/')
def home():
    list = ''
    for a in dnsBusiness.getDomainNamesList():
        list += f'<a href="resolve?domain={a}">{a}</a><br>'
    return list

@app.route('/resolve')
def resolve():
    domain = request.args.get('domain', default = '', type = str)
    if len(domain) > 0 : # and right format
        ip, port = dnsBusiness.resolveDomainName(domain)
        return "<h1>"+ domain +" in "+ip+" with "+str(port)+"</h1>"
    return "Sorry, can't find it "

@app.route('/debug/dump_chain')
@app.route('/nodes/chain')
def getBlockchain():
    response = dnsBusiness.getBlockChain()
    return jsonify(response), 200

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
    # dns_resolver = dns(node_identifier = APP_NODE.id)
    dnsBusiness.configNodeID(APP_NODE.id)
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
    
