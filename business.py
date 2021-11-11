import requests
from requests.models import Response
from constant import *
from database import *
from uuid import uuid4
import random, sys
import threading, time
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

# All systems will have only one Blockchain -----------------------------------
class Blockchain:
    def __init__(self):
        '''
        Blockchain first get blocks by loading from DB 
        '''
        self.nodes = NodesBusiness()
        self.transactions = TransactionBusiness()
        self.chain = []
        self.MINE_REWARD = 10
        self.BUFFER_MAX_LEN = 20
        self.DIFFICULTY = 1
    

    def showChainDict(self):
        self.loadChain()
        return {
            'len': len(self.chain),
            'chain': [block.as_dict() for block in self.chain],
        }

    def getGenesisBlock(self):
        return Blocks(
            id=1,
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
            return 404

        self.chain = [genesisBlock]
        blocks_list = Blocks.query.order_by(Blocks.id).all()
        if len(blocks_list) > 0:
            for block in blocks_list:
                self.chain.append(block)
        
        db.session.expunge_all()
        db.session.close()

        return 200
    
    def findFastestBlockResponse(self, responses):
        minSpeedtime = sys.float_info.max 
        fastestBlockResponse = None
        for response in responses:
            if response['speedtime'] < minSpeedtime:
                minSpeedtime = response['speedtime']
                fastestBlockResponse = response['block']

        return fastestBlockResponse
    
    def launchNetworkProofOfWork(self, transactions):
        '''
            Process step : 
            
        '''
        neighbours = self.nodes.getActiveNetwork()
        # Building request with current transaction
        responses = []
        
        def sendRequestAndReturn( url, data ):
            rep = requests.post(
                url  = url,
                data = data,
            )
            responses.append(rep.json())

        # Compress Transaction to list( str ) 
        compress_trans = [ self.transactions.toString(tran) for tran in transactions]
        
        # Adding information of this block
        request_block = merge_obj(
            dict(
                { str(i) : item for i, item in enumerate(compress_trans) }
            ),
            getModelDict( self.newBlock( len(compress_trans) ) )
        )

        # Loop to any nodes that active in network -> Send request to any nodes active in network by thread
        for node in neighbours:  
            request_url = f'http://{node.ip}:{node.port}/blockchain/pow'
            # Add Thread here 
            x = threading.Thread(target=sendRequestAndReturn, args=[request_url, request_block])
            x.start()
            
        for node in neighbours:    
            x.join()

        return responses
    
    def returnProofOfWorkOutput(self, block_request ):
        '''
            Process step : 
                1. From request ,convert array of transactions
                2. Create new Block, add field ['add_by_node_id'] 
                3. Run Proof of work -> return block, speedtest 
        '''
        #   1.
        transactions = [ self.transactions.formatRecord(block_request[prop]) if re.match('^\d+$',prop) else None for prop in block_request.keys()]
        transactions = transactions[0: int(block_request['transactions'])]
        #   2.
        block_request['transactions'] = transactions
        block_request['add_by_node_id'] = self.node_id
        #   3.
        block = Blocks().from_dict(block_request)
        return self.proofOfWork(block)

    def proofOfWork(self, block):
        '''
            Each time, proof of work will be called by many request, so must gain its prop 'add_by_node_id' 
            Proof of work will generate Nonce number until match condition 
            Hash x nonce = Hash ['0x + 63chars']
        '''
        start = time.perf_counter()
        # ----------------------------
        block.hash = self.hash(block)
        block.nonce = 0
        while not block.hash.startswith('0' * self.DIFFICULTY):
            block.nonce += 1
            block.hash = self.hash(block)
        # ----------------------------
        end = time.perf_counter()
        return block, float(end-start)

    def newBlock(self, transactions):
        '''
            Return new block when provide informations
        '''
        return Blocks(
            id=len(self.chain) +1,
            timestamp=time.time(),
            nonce=0,
            transactions=transactions,
            previous_hash=self.hash(self.last_block) if len(
                self.chain) > 1 else '0'*64,  # genesis.hash
            node_id=self.node_id,
            add_by_node_id = None
        )

    def addBlock(self, block):  
        '''
            Adding block steps : [ /blockchain/launchpow as preparation ]
                1) Launch Proof of Work in Network
                2) Find the fastest hashing block 
                3) Add that block 
            + : New Block and status 200 
            - : New Block and status 404 
        '''
        try:
            db.session.add(block)
            db.session.commit()
            return block, 200
        except:
            return block, 404

    def prepareMiningBlockTransactions(self):
        trans = self.current_transaction
        trans_len = len(trans) 
        
        if trans_len >= self.BUFFER_MAX_LEN: # and create_block_countdown end
            return self.transactions.subTransaction( start = 0, length = self.BUFFER_MAX_LEN ), 200
        else: 
            return trans, 500 # not enough transactions 
        
    def mineBlock(self ):
        '''
            This function will use current_transaction
        '''
        # Init and check transactions status  
        transactions, status = self.prepareMiningBlockTransactions()
        message = 'Mining block successfully' if status == 200 else f'Not enough {self.BUFFER_MAX_LEN} transaction to process'
        if status != 200:
            return {
                'status': status,
                'message': message,
            }
        # Mining with Proof of work 
        responses = self.launchNetworkProofOfWork(transactions)
        fastestBlockResponse = self.findFastestBlockResponse(responses)
        block = Blocks().from_dict(fastestBlockResponse)
        
        # Adding the block to all network
        block, status = self.addBlock(block)
        self.broadcastNewBlock()

        # Getting message 
        return {
            'status' : status,
            'message': message,
            'block'  : block.id
        }
    
    def addTransaction(self, tran):
        return self.transactions.addTransaction(tran)

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
        # ! Is there any time 2 block is sending to database ?
        return self.showChainDict()

    @staticmethod
    def hash(block):
        block_string = json.dumps(
            getModelDict(block), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def current_transaction(self):
        return self.transactions.current_transactions

    @property
    def node_id(self):
        return self.nodes.getNode().id

    @property
    def ledger(self):
        trans = []
        for block in self.chain: 
                if block.transactions :
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

# TransactionBusiness  -----------------------------------
class TransactionBusiness:
    def __init__(self):
        self.current_transactions = []

    def isExisted(self, tran):
        try:
            return self.current_transactions.index(tran)
        except:
            return False
    
    def convertRecordsFromBlockRequest(self, obj):
        pass

    def toString(self, tran):
        return f"{tran['domain']} {tran['type']} {tran['ip']} {tran['port']} {tran['ttl']}"    
        
    def formatRecord(self, str, final = True):
        props = str.split()
        return {
            'domain': props[0],
            'type': props[1],
            'ip': props[2],
            'port': props[3] if final == False else int(props[3]),
            'ttl': props[4] if final == False else int(props[4])
        }

    def checkRecordFormat(self, tran):
        checked = copy(RECORD_FORMAT)
        if type(tran) == str:
            tran = tran.strip()
            tran = self.formatRecord(tran, False)
        # Check if tran has the same key and ammount of keys as checked
        if tran.keys() == checked.keys():
            for key in checked.keys():
                checked[str(key)] = True if re.match(
                    checked[str(key)], tran[str(key)]) else False
                if checked[str(key)] == False : return False      
        return True
    
    def subTransaction(self,  start = None, length = None ):
        used_block_transactions = self.current_transactions[ start : length ]
        self.current_transactions = self.current_transactions[ length : ]
        return used_block_transactions
    
    def clearTransaction(self,):
        self.current_transactions = []
        return self.current_transactions

    def addTransaction(self, tran):
        if self.checkRecordFormat(tran) == False:
            return 500  # wrong format

        if type(tran) == str:
            tran = self.formatRecord(tran)
            
        if self.isExisted(tran) == False:
            self.current_transactions.append(tran)
        else:
            return 501  # duplicate
            
        return 200

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
        return Nodes.query.filter(Nodes.is_deleted == False).all()

    def getActiveNetwork(self):
        return Nodes.query.filter(Nodes.is_active == True, Nodes.is_deleted == False).all()

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
        if node.is_active != True:
            node.is_active = True
            return self.updateNode(oldNode, node)
        return node

    def inActiveNode(self, node):
        oldNode = node
        if node.is_active != False:
            node.is_active = False
            return self.updateNode(oldNode, node)
        return node

    def handleNodeInformation(self, ip: str, port: int, nodename=''):
        """
            Handle 5 Cases :
                - Empty network  : Create OK
                - Node with new IP : Create OK
                - Node with new port : Create OK
                - Node has already been active : Search another node inactive in nodeIP
                - Node han't been active yet : Active node OK
        """
        network = self.getNetwork()  # Found all node ( not-working status )
        id = str(uuid4()).replace('-', '')
        if not network:  # Empty network, create new
            return self.registerNode(
                id,
                ip,
                port,
                nodename,
                True
            )
        else:
            nodeIP = self.getNodeWithIP(ip)
            if not nodeIP:  # Don't have this IP in DB, create new
                return self.registerNode(
                    id,
                    ip,
                    port,
                    nodename,
                    True
                )
            nodeIPPort = self.getNodeWithIPAndPort(ip, port)
            if not nodeIPPort:  # Have this IP but don't have this port, create new
                return self.registerNode(
                    id,
                    ip,
                    port,
                    nodename,
                    True
                )
            elif nodeIPPort.is_active == True:  # This node already active
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
                    anotherNode[0].is_active = True
                    return anotherNode[0], 201
            else:  # This node is not used by anyone
                self.activeNode(nodeIPPort)
                nodeIPPort.is_active = True
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
                RECORD_FORMAT['ip'], node.ip) else True
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

    def updateNode(self, oldNode, node):
        if not self.validateNode(oldNode):
            return oldNode, 403

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
            return oldNode, 404

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
