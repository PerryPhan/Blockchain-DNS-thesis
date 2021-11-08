import requests
from requests.models import Response
from constant import *
from database import *
from uuid import uuid4
import random
from time import time

'''
    This file includes main Business for App
'''

# One DNSResolver is a System -----------------------------------


class DNSResolver:
    def __init__(self):
        '''
        Each node only has one DNSResolver
        also manage 2 props 
            NodesBusiness nodes : Control of node in network
            Blockchain : Control of node in blockchain
        '''
        
        self.blockchain = Blockchain()
        pass

    def initBlockchain(self, node):
        self.blockchain.nodes.setNode(node)
        self.blockchain.loadChainFromDB()

# All systems will have only one Blockchain -----------------------------------
class Blockchain:
    MINE_REWARD = 10
    BUFFER_MAX_LEN = 20
    DIFFICULTY = 1

    def __init__(self):
        '''
        Blockchain first get blocks by loading from DB 
        '''
        self.nodes = NodesBusiness()
        self.current_transactions = []
        self.chain = []

    def showChainDict(self):
        return {
            'chain' : [ get_model_dict(block) for block in self.chain],
            'len' : len(self.chain)
        }
        pass

    def getGenesisBlock(self):
        return Blocks(
            id='1',
            timestamp=time(),
            nonce=1,
            hash='0'*64,
            node_id=self.node_id,
            transactions=None
        ) if self.node_id else None

    def loadChainFromDB(self):
        genesisBlock = self.getGenesisBlock()
        if not genesisBlock:
            return 404
        self.chain = [genesisBlock]
        blocks_list = Blocks.query.order_by(Blocks.id).all()
        if len(blocks_list) > 0:
            for block in blocks_list:
                self.chain.append(block)
        return 200

    def proofOfWork(self, block):
        '''
            Proof of work will generate Nonce number until match condition 
            
        '''
        # Base on self.Difficulty 
        hash = self.hash(block)
        block.nonce = 0 
        while not hash.startswith('0' * self.DIFFICULTY):
            block.nonce += 1
            hash = self.hash(block)
        return block  

    def newBlock(self, transactions, node_id):
        # For adding purpose, so there is nothing on it
        return Blocks(
            id = len(self.chain) + 1,
            timestamp = time(),
            nonce = 0,
            transactions = transactions, 
            previous_hash = self.hash(self.last_block) if len(self.chain)  > 1 else '0'*64, #genesis.hash
            node_id = node_id,
        )

    def addBlock(self):  # Mining new Block
        # Launch Proof of Work -> return block
        block = self.newBlock( self.current_transactions, self.node_id )
        block = self.proofOfWork( block )
        
        # Broadcast new Block -> Overide the longest chain

        try:
            db.session.add(block)
            db.session.commit()
            self.broadcastNewBlock()
            return block,200
        except:
            return block, 404
        
    def addTransaction(self, tran):
        self.current_transactions.append(tran)

    def broadcastNewBlock(self):
        neighbors = self.nodes.getActiveNetwork()
        # 1. Send request to check database of every nodes
        for node in neighbors:
            requests.get(f'http://{node.ip}:{node.port}/blockchain/solving_conflict')
        
    def overrideTheLongestChain(self):
        # 2. Override the longest chain - with this pj is the one in the Database
        return self.loadChainFromDB()
        # ! Is there any time 2 block is sending to database ?
        
    @staticmethod
    def hash( block ):
        block_string = json.dumps( get_model_dict(block) , sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def node_id(self):
        return self.nodes.getNode().id
# NodeBusiness  -----------------------------------


class NodesBusiness:
    PORT_START = 5000
    PORT_END = 5999

    def __init__(self):
        self.node = None
        pass
    
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
        # 5 Cases :
        #   - Empty network  : Create OK
        #   - New IP : Create OK
        #   - New port : Create OK
        #   - Already been active : Search in nodeIP
        #   - Not been active yet : Active node OK
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
            if not nodeIPPort:  # Have this IP but wrong port, create new with random port
                return self.registerNode(
                    id,
                    ip,
                    random.randint(self.PORT_START, self.PORT_END),
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
        if not node:  # check node ( not null )
            checked = False
        if not node.id or len(node.id) > 40:  # check id ( not null, < 40 chars)
            checked = False
        if len(node.nodename) > 64:  # check nodename ( null, 64 chars)
            checked = False
        # check IP ( not null, 16 chars, match regex )
        if not node.ip or len(node.ip) > 16:
            checked = False
        else:
            checked = False if not re.search(
                RECORD_FORMAT['ip'], node.ip) else True
        if not node.port or node.port < self.PORT_START or node.port > self.PORT_END:
            checked = False
        # check duplicate
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
