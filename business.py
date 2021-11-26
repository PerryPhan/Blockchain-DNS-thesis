from re import T
import requests
from requests.models import Response
from include import *
from database import *
from uuid import uuid4
import random
import sys
import threading
import time
'''
    This file includes main Business for App
'''

# One DNSResolver is a System -----------------------------------


class DNSResolver:
    def __init__(self):
        '''
            Each node only has one DNSResolver
            also manage 2 props 
            > Blockchain controls all related process to blockchain
            | > NodeBusiness controls all nodes ( machines ) in the Network 
            | > TransactionBusiness controls transactions flow in transaction buffer 
        '''
        self.blockchain = Blockchain()
        pass

    def initBlockchain(self, node):
        self.blockchain.nodes.setNode(node)
        self.blockchain.loadChain()

    def lookup(self, request_form):
        return self.blockchain.searchTransactionMatchObj(request_form)

# All systems will have only one Blockchain -----------------------------------


class Blockchain:
    def __init__(self):
        '''
        Blockchain first get blocks by loading from DB 
        '''
        self.nodes = NodesBusiness()
        self.transactions = TransactionBusiness()
        self.chain = []
        self.MINE_REWARD = MINE_REWARD
        self.BUFFER_MAX_LEN = BUFFER_MAX_LEN
        self.DIFFICULTY = DIFFICULTY
    
    #  EXTRA PROPERTIES ----------------------------------------------------------
    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def current_transactions(self):
        return self.transactions.getNoBlockTransactions()

    @property
    def all_transactions(self):
        all = []
        for block in self.chain:
            if block.transactions:
                all.extend(block.transactions)
        all.extend(self.current_transactions)
        return all

    @property
    def node_id(self):
        node = self.nodes.getNode()
        return node.id if node else None

    @property
    def ledger(self):
        trans = []
        for block in self.chain:
            if block.transactions:
                for tran in block.transactions:
                    trans.append(tran)
        return trans

    @property
    def wallet(self):
        totalRewards = 0
        for block in self.chain:
            if block.id != 0 and block.add_by_node_id:
                if block.add_by_node_id == self.node_id:
                    totalRewards += self.MINE_REWARD
        return totalRewards

    def dumpChain(self):
        return [block.as_dict() for block in self.chain]
    
    # GET & SHOW CHAIN ----------------------------------------------------------
    def getGenesisBlock(self):
        return Blocks(
            id='0',
            timestamp=time.time(),
            nonce=1,
            hash='0'*64,
            node_id=self.node_id,
            transactions=None
        ) if self.node_id else None

    def loadChain(self):
        '''
            Both init and reload blockchain by loading blocks from DB 
        '''
        genesisBlock = self.getGenesisBlock()

        if not genesisBlock:
            return 500

        self.chain = [genesisBlock]
        # self.chain = []
        try:

            blocks_list = db.session.query(Blocks).all()
            if len(blocks_list) > 0:
                for block in blocks_list:
                    self.chain.append(block)

            return 200

        except:
            print(' Error : something go wrong with Query')
            return 404
    # TODO : check intergity of chain 

    #  STEPS OF MINE BLOCK ----------------------------------------------------------
    def prepareMiningBlockTransactions(self):
        trans = self.current_transactions
        trans_len = len(trans)

        if trans_len >= self.BUFFER_MAX_LEN:
            return trans, 200
        else:
            return trans, 500  

    def mineBlock(self, transactions):
        '''
            This function will use current_transaction
        '''
        # Mining with Proof of work
        responses = self.launchNetworkProofOfWork(transactions)

        fastestBlockResponse = self.findFastestBlockResponse(responses)
        block = Blocks(
            id= fastestBlockResponse['id'],
            timestamp=float(fastestBlockResponse['timestamp']),
            nonce=int(fastestBlockResponse['nonce']),
            transactions=fastestBlockResponse['transactions'],
            previous_hash=fastestBlockResponse['previous_hash'],
            node_id=fastestBlockResponse['node_id'],
            add_by_node_id=fastestBlockResponse['add_by_node_id'] if 'add_by_node_id' in fastestBlockResponse else None
        )
        return block

    #  STEP #1 : POW CONTEST ----------------------------------------------------------
    def launchNetworkProofOfWork(self, transactions):
        '''
            Process step : 
            1. Building request with current transaction
            2. Compress Transaction to list( str ) 
            3. Adding information of this block
            4. Loop to any nodes that active in network -> Send request to any nodes active in network by thread
                4.1. Add Thread here 
        '''
        responses = []

        def sendRequestAndReturn(url, data):
            rep = requests.post(
                url=url,
                data=data,
            )
            responses.append(rep.json())
        # ----------------------------------------
        neighbours = self.nodes.getActiveNetwork()
        
        transactions = [ tran.block_tx_format() for tran in transactions]
        request_block = self.newBlock(transactions).as_dict()
        # ----------------------------------------
        for node in neighbours:
            request_url = f'http://{node.ip}:{node.port}/blockchain/pow'
            # 4.1
            x = threading.Thread(
                target=sendRequestAndReturn,
                args=[ request_url, request_block ]
            )
            x.start()

        for node in neighbours:
            x.join()
        # ----------------------------------------
        
        return responses

    def proofOfWork(self, block):
        '''
            Each time, proof of work will be called by many request, so must gain its prop 'add_by_node_id' 
            Proof of work will generate Nonce number until match condition 
            Hash x nonce = Hash ['0x + 63chars']
        '''
        start = time.perf_counter()
        # ----------------------------
        block.nonce = 0
        while not block.hash().startswith('0' * self.DIFFICULTY):
            block.nonce += 1
        # ----------------------------
        end = time.perf_counter()
        return block, float(end-start)

    def findFastestBlockResponse(self, responses):
        minSpeedtime = sys.float_info.max
        fastestBlockResponse = None
        if len(responses) == 1:
            minSpeedtime = responses[0]['speedtime']
            fastestBlockResponse = responses[0]['block']
            return fastestBlockResponse
        else:
            for response in responses:
                if response['speedtime'] < minSpeedtime:
                    minSpeedtime = response['speedtime']
                    fastestBlockResponse = response['block']

        return fastestBlockResponse
    
    def returnProofOfWorkOutput(self, request_form_dict):
        '''
            Process step : 
                1 Create new Block, add field ['add_by_node_id'] 
                2 Run Proof of work -> return block, speedtest 
        '''
        request_form_dict['add_by_node_id'] = self.node_id

        block = Blocks(
            id= int(request_form_dict['id'][0]),
            timestamp= float(request_form_dict['timestamp'][0]),
            nonce= int(request_form_dict['nonce'][0]),
            transactions= request_form_dict['transactions'],
            previous_hash= request_form_dict['previous_hash'][0],
            node_id= request_form_dict['node_id'][0],
            add_by_node_id=request_form_dict['add_by_node_id'] if 'add_by_node_id' in request_form_dict else None
        )

        return self.proofOfWork(block)

    #  STEP #2 : FORGE, ADD AND BROADCAST BLOCK ----------------------------------------------------------
    def newBlock(self, transactions):
        '''
            Return new block when provide informations
        '''
        previous_hash = self.last_block.hash() if len(
            self.chain) > 1 else '0'*64,  # genesis.hash
        return Blocks(
            id=len(self.chain),
            timestamp=time.time(),
            nonce=0,
            transactions=transactions,
            previous_hash=previous_hash,
            node_id=self.node_id,
            add_by_node_id=None
        )

    def addBlock(self, block):
        try:
            db.session.add(block)
            db.session.commit()
            return block, 200
        except:
            db.session.rollback()
            return block, 404

    def broadcastNewBlock(self):
        '''
            Send request to each machine in active network
        '''
        neighbors = self.nodes.getActiveNetwork()
        for node in neighbors:
            requests.get(
                f'http://{node.ip}:{node.port}/blockchain/overide')

    def overrideTheLongestChain(self):
        '''
            Override the longest chain by reload the blockchain saved in DB 
        '''
        return self.loadChain()

    # GENERAL FUNCTION ----------------------------------------------------------
    def searchTransactionMatchObj(self, obj):
        for transaction in self.all_transactions:
            for key, value in transaction.items():
                if key in obj.keys():
                    if value == obj[key]:
                        return transaction, 200
        return None, 404

# TransactionBusiness  -----------------------------------


class TransactionBusiness:
    def __init__(self):
        self.TIME_TO_LIVE = 3600
   
    def convertRequestToTransactionObj(self, request_form):
        return {
            "domain": request_form['domain'],

            'soa': {
                "mname": request_form['soa_mname'],
                "rname": request_form['soa_rname'],
                "refresh": request_form['soa_refresh'],
                "retry": request_form['soa_retry'],
                "expire": request_form['soa_expire'],
                "minimum": request_form['soa_minimum'],
            },

            'ns':  [
                {"host": request_form['ns_host1']},
                {"host": request_form['ns_host2']},
            ],

            'a':  [
                {
                    "name": request_form['a_name_1'],
                    "ttl": request_form['a_ttl_1'],
                    "value": request_form['a_value_1']
                },
                {
                    "name": request_form['a_name_2'],
                    "ttl": request_form['a_ttl_2'],
                    "value": request_form['a_value_2']
                },
                {
                    "name": request_form['a_name_3'],
                    "ttl": request_form['a_ttl_3'],
                    "value": request_form['a_value_3']
                },
            ],
        }

    def checkTransactionFormat(self, obj):
        checked = copy(RECORD_FORMAT)
        if 'domain' in obj:
            if obj['domain'] :
                checked['domain'] = copy(checked['domain'])
                checked['domain'] = True if re.match( checked['domain'], obj['domain']) else False
        
        checked['soa'] = copy(checked['soa'])
        if 'soa' in obj:
            if obj['soa'] :
                for key in obj['soa'].keys():
                    checked['soa'][key] = True if obj['soa'][key] and re.match( checked['soa'][key], obj['soa'][key]) else False
        
        checked['soa'] = all([ checked['soa'][key] for key in checked['soa'].keys() ])
        
        checked['ns'] = copy(checked['ns'])
        if 'ns' in obj:
            if obj['ns'] :
                for i in range(len(obj['ns'])):
                    checked['ns'][i] = copy(checked['ns'][i])
                    checked['ns'][i]['host'] = copy(checked['ns'][i]['host'])
                    checked['ns'][i]['host'] = True if obj['ns'][i]['host'] and re.match( checked['ns'][i]['host'], obj['ns'][i]['host']) else False
        
        checked['ns'] = all([ ns['host'] for ns in checked['ns'] ])
        
        checked['a'] = copy(checked['a']) 
        if 'a' in obj:
            if obj['a'] :
                for i in range(len(obj['a'])):
                    if obj['a'][i]['value'] != "":
                        for key in obj['a'][i].keys():
                            checked['a'][i] = copy(checked['a'][i])
                            checked['a'][i][key] = copy(checked['a'][i][key])
                            checked['a'][i][key] = True if obj['a'][i][key] and re.match( checked['a'][i][key], obj['a'][i][key]) else False
            
        for spec in checked['a']:
            spec = all([ spec[key] for key in spec.keys() ])
            
        checked['a'] = all([spec for spec in checked['a']])
        
        return all([checked[key] for key in checked.keys()])

    def newTransaction(self, request_form, account_id, action, convertToObj = False):
        obj = request_form
        if convertToObj == True:  
            obj = self.convertRequestToTransactionObj( obj )
        if self.checkTransactionFormat(obj) == True:
            #  Add serial & ttl to SOA 
            obj['soa']['serial'] = time.time()
            obj['ttl'] = self.TIME_TO_LIVE
            tran =  Transactions(
                domain = obj['domain'],
                action = action,
                soa    = obj['soa'],
                ns     = obj['ns'],
                a      = obj['a'],
                ttl    = obj['ttl'],
                timestamp = time.time(),
                account_id = account_id,
            )
            return tran, 200
        return None, 500

    def addTransaction(self, transaction):
        try:
            db.session.add(transaction)
            db.session.commit()
            return 200
        except:
            db.session.rollback()
            return 401

    def updateTransaction(self, transaction):
        try:
            db.session.query(Transactions).filter(
                Transactions.id == transaction.id,
            ).update({
                'block_id' : transaction.block_id
            })
            db.session.commit()
            return transaction, 200
        except:
            return transaction, 404

    def setCurrentTxsBlockID(self, block_id):
        no_block_txs_list = self.getNoBlockTransactions()
        for transaction in no_block_txs_list:
            transaction.block_id = block_id
            self.updateTransaction( transaction )
    
    def getNoBlockTransactions(self):
        return Transactions.query.filter(Transactions.block_id == None).all()
    
    def getAllTransactions(self):
        return Transactions.query.all()

    def getDomainList(self):
        # TODO : Pool + Blockchain
        records = []
        for transaction in self.getAllTransactions():
            # TODO : Add + Update Tx
            if transaction.action == 'add':
                records.append(Records(transaction))
            elif transaction.action == 'Update':
                pass
        return records

    def getTransactionById(self, id):
        return Transactions.query.filter(Transactions.id == id).first()
# NodeBusiness  -----------------------------------


class NodesBusiness:
    def __init__(self):
        self.node = None
        self.PORT_START = 5000
        self.PORT_END = 5999
        pass

    @staticmethod
    def getRandomPort():
        PORT_START = 5000
        PORT_END = 5999
        return random.randint(PORT_START, PORT_END)

    def setNode(self, node):
        self.node = node

    def getNode(self):
        return self.node

    def getNetwork(self):
        return db.session.query(Nodes).filter(Nodes.is_deleted == False).all()

    def getActiveNetwork(self):
        return db.session.query(Nodes).filter(Nodes.is_active == True, Nodes.is_deleted == False).all()

    def getNodeWithIP(self, ip):
        return db.session.query(Nodes).filter(
            Nodes.ip == ip,
            Nodes.is_deleted == False
        ).all()

    def getNodeWithIPAndPort(self, ip, port):
        return db.session.query(Nodes).filter(
            Nodes.ip == ip,
            Nodes.port == port,
            Nodes.is_deleted == False
        ).first()

    def activeNode(self, node):
        if node.is_active != True:
            node.is_active = True
            return self.updateNode( node)
        return node

    def inActiveNode(self, node):
        if node.is_active != False:
            node.is_active = False
            return self.updateNode( node)
        return node

    def handleNodeInformation(self, ip: str, port: int, nodename=''):
        """
            Handle 5 Cases :
                Empty network  : Create OK
                Node with new IP : Create OK
                Node with new port : Create OK
                Node has already been active : Search another node inactive in nodeIP
                Node han't been active yet : Active node OK
        """
        network = self.getNetwork()  # Found all node ( not-working status )
        id = str(uuid4()).replace('-', '')
        if not network:  # 1. Empty network, create new
            return self.registerNode(
                id,
                ip,
                port,
                nodename,
                True
            )
        else:
            nodeIP = self.getNodeWithIP(ip)
            if not nodeIP:  # 2. Don't have this IP in DB, create new
                return self.registerNode(
                    id,
                    ip,
                    port,
                    nodename,
                    True
                )
            nodeIPPort = self.getNodeWithIPAndPort(ip, port)
            if not nodeIPPort:  # 3. Have this IP but don't have this port, create new
                return self.registerNode(
                    id,
                    ip,
                    port,
                    nodename,
                    True
                )
            elif nodeIPPort.is_active == True:  # 4. This node already active
                anotherNode = [
                    node for node in nodeIP if node.is_active == False and node.ip == nodeIPPort.ip]
                if len(anotherNode) <= 0:  # No node same IP spared
                    return self.registerNode(
                        id,
                        ip,
                        random.randint(self.PORT_START, self.PORT_END),
                        nodename,
                        True
                    )
                else:  # This node has same IP, different port and haven't used yet
                    self.activeNode(anotherNode[0])
                    return anotherNode[0], 201

            else:  # 5. This node is not used by anyone
                self.activeNode(nodeIPPort)
                return nodeIPPort, 201

    def validateNode(self, node, noCheckDuplicate=False):
        checked = True
        # Check node ( not null )
        if not node:
            checked = False
        # Check id ( not null, < 40 chars)
        if not node.id or len(node.id) > 40:
            checked = False
        # Check nodename ( null, 64 chars)
        if len(node.nodename) > 64:
            checked = False
        # Check IP ( not null, 16 chars, match regex )
        if not node.ip or len(node.ip) > 16:
            checked = False
        else:
            checked = False if not re.search(
                IP_FORMAT, node.ip) else True
        if not node.port or node.port < self.PORT_START or node.port > self.PORT_END:
            checked = False
        # Check duplicate
        if noCheckDuplicate and self.getNodeWithIPAndPort(node.ip, node.port):
            checked = False
        return checked

    def registerNode(self, id: str, ip: str, port: int, nodename='', is_active=False):
        node = Nodes(
            id=id,
            ip=ip,
            port=port,
            nodename=nodename,
            is_deleted=False,
            is_active=is_active
        )

        if not self.validateNode(node, True):
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
            db.session.query(Nodes).filter(
                Nodes.id == node.id,
                Nodes.is_deleted == False
            ).update({
                "ip": node.ip, "port": node.port, "nodename": node.nodename, "is_active": node.is_active
            })
            db.session.commit()
            return node, 200
        except:
            return node, 404

    def deleteNode(self, node):
        node = db.session.query(Nodes).filter(
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

# AccountBusiness  -----------------------------------


class AccountBusiness:
    # Login
    def getAccountByEmail(self, email, password=None):
        account = Accounts.query.filter(
            Accounts.email == email, Accounts.is_deleted == False).first() or None
        if password:
            return account if account and check_password_hash(account.password, password) else None
        return account

    def getAccountById(self, id=0):
        return Accounts.query.filter(Accounts.id == id, Accounts.is_deleted == False).first()

    def getListAccounts(self):
        return Accounts.query.order_by(Accounts.id).all()

    def authenticateAccount(self, email, password):
        status = 405
        if not email:
            return None, status
        if not password:
            return None, status

        account = self.getAccountByEmail(email, password)
        if not account:
            status = 404
            if self.getAccountByEmail(email):
                status = 403
        else:
            status = 200

        return account, status

    # Register

    def checkAccountInformation(self, fullname, email, password, repassword, type_cd):
        check = copy(ACCOUNT_FORMAT)

        check['fullname'] = True if fullname and re.match(
            check['fullname'], fullname) else False

        check['email'] = True if email and re.match(
            check['email'], email) else False

        check['password'] = True if password and re.match(
            check['password'], password) else False

        check['repassword'] = True if repassword and re.match(
            check['repassword'], repassword) else False

        check['type_cd'] = True if type_cd and re.match(
            check['type_cd'], str(type_cd)) else False

        return all([check[key] for key in check.keys()])

    def newAccount(self, fullname, email, password, repassword, type_cd):
        # Check format
        if self.checkAccountInformation(fullname, email, password, repassword, type_cd) == False:
            return None, 500

        # Check duplicate
        if self.getAccountByEmail(email, None):
            return None, 501

        # Encrypt
        password = generate_password_hash(password)

        return Accounts(
            fullname=fullname,
            email=email,
            password=password,
            type_cd=type_cd,
            is_deleted=False
        ), 200

    def addAccount(self, newAccount):
        try:
            db.session.add(newAccount)
            db.session.commit()
            return 200
        except:
            db.session.rollback()
            return 401

    def updateAccount(self):
        pass

    def deleteAccount(self):
        pass
