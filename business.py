import requests
from requests.models import Response
from constant import *
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
        self.MINE_REWARD = 10
        self.BUFFER_MAX_LEN = 20
        self.DIFFICULTY = 1

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def current_transactions(self):
        return self.transactions.current_transactions

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
        return self.nodes.getNode().id

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

    def launchNetworkProofOfWork(self, transactions):
        def sendRequestAndReturn(url, data):
            rep = requests.post(
                url=url,
                data=data,
            )
            responses.append(rep.json())
        '''
            Process step : 
            1. Building request with current transaction
            2. Compress Transaction to list( str ) 
            3. Adding information of this block
            4. Loop to any nodes that active in network -> Send request to any nodes active in network by thread
                4.1. Add Thread here 
        '''
        neighbours = self.nodes.getActiveNetwork()

        # 1
        responses = []

        # 2
        compress_trans = [self.transactions.toString(
            tran) for tran in transactions]

        # 3
        request_block = merge_obj(
            dict(
                {str(i): item for i, item in enumerate(compress_trans)}
            ),
            getModelDict(self.newBlock(len(compress_trans)))
        )
        # print('Neighbours length: ', len(neighbours), " : Neighbours ",neighbours )
        # 4
        for node in neighbours:
            request_url = f'http://{node.ip}:{node.port}/blockchain/pow'
            # 4.1
            x = threading.Thread(target=sendRequestAndReturn, args=[
                                 request_url, request_block])
            x.start()

        for node in neighbours:
            x.join()

        return responses

    def returnProofOfWorkOutput(self, block_request):
        '''
            Process step : 
                1. From request ,convert array of transactions
                2. Create new Block, add field ['add_by_node_id'] 
                3. Run Proof of work -> return block, speedtest 
        '''
        #   1.
        numbered_transactions = [self.transactions.formatRecord(block_request[prop]) if re.match(
            '^\d+$', prop) else None for prop in block_request.keys()]
        transactions = []
        for transaction in numbered_transactions:
            if transaction:
                transactions.append(transaction)

        #   2.
        block_request['transactions'] = transactions
        block_request['add_by_node_id'] = self.node_id
        #   3.
        block = Blocks(
            id=block_request['id'],
            timestamp=float(block_request['timestamp']),
            nonce=int(block_request['nonce']),
            transactions=block_request['transactions'],
            previous_hash=block_request['previous_hash'],
            node_id=block_request['node_id'],
            add_by_node_id=block_request['add_by_node_id'] if 'add_by_node_id' in block_request else None
        )
        return self.proofOfWork(block)

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

    def prepareMiningBlockTransactions(self):
        trans = self.current_transactions
        trans_len = len(trans)

        if trans_len >= self.BUFFER_MAX_LEN:  # and create_block_countdown end
            return self.transactions.subTransaction(start=0, length=self.BUFFER_MAX_LEN), 200
        else:
            return trans, 500  # not enough transactions

    def mineBlock(self):
        '''
            This function will use current_transaction
        '''
        # self.transactions.createSampleTransactions(20)

        # Init and check transactions status
        transactions, status = self.prepareMiningBlockTransactions()
        if status != 200:
            return None, status

        # Mining with Proof of work
        responses = self.launchNetworkProofOfWork(transactions)
        fastestBlockResponse = self.findFastestBlockResponse(responses)
        block = Blocks(
            id=fastestBlockResponse['id'],
            timestamp=float(fastestBlockResponse['timestamp']),
            nonce=int(fastestBlockResponse['nonce']),
            transactions=fastestBlockResponse['transactions'],
            previous_hash=fastestBlockResponse['previous_hash'],
            node_id=fastestBlockResponse['node_id'],
            add_by_node_id=fastestBlockResponse['add_by_node_id'] if 'add_by_node_id' in fastestBlockResponse else None)

        return block, status

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
        return self.loadChain()

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
        self.current_transactions = []

    def createSampleTransactions(self, number):
        chain = []
        for i in range(number):
            chain.append({
                'domain': f'sample{i}.com',
                'type': 'A',
                'ip': f'{i}.{i}.{i}.{i}',
                'port': 80,
                'ttl': '14400'
            })

        self.current_transactions = chain

    def isExisted(self, tran):
        try:
            return self.current_transactions.index(tran)
        except:
            return False

    def convertRecordsFromBlockRequest(self, obj):
        pass

    def toString(self, tran):
        return f"{tran['domain']} {tran['type']} {tran['ip']} {tran['port']} {tran['ttl']}"

    def formatRecord(self, str, final=True):
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
                if checked[str(key)] == False:
                    return False
        return True

    def subTransaction(self,  start=None, length=None):
        used_block_transactions = self.current_transactions[start: length]
        self.current_transactions = self.current_transactions[length:]
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

    def setTransaction(self, trans):
        self.current_transactions = trans

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
            if not nodeIPPort: # 3. Have this IP but don't have this port, create new
                return self.registerNode(
                    id,
                    ip,
                    port,
                    nodename,
                    True
                )
            elif nodeIPPort.is_active == True:  #4. This node already active
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
                
            else:  #5. This node is not used by anyone
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
