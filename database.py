from include import db, json, hashlib, datetime
import time
''' 
    This file stores what is necessary in Database PgSQL 
'''

def recreate():
    db.drop_all()
    db.create_all()

def insertBlock():
    block = Blocks(
        id = 1,
        timestamp = 1.1,
        nonce = 1,
        transactions = [
            {
                'domain' : 'a',
                'type' : 'A',
                'ip' : '1.1.1.1',
                'port' : 80,
                'ttl' : 14400
            } for i in range( 20 )
        ],
        previous_hash = '00',
        node_id = None,
        add_by_node_id = None
    )
    try :
        db.session.add(block)
        db.session.commit()
    except:
        db.session.rollback()
        print('Can not add block')

def getFirstBlock():
    return Blocks.query.filter(
            Blocks.id == 1,
    ).first()

def insertTransaction():
    timestamp = time.time()
    tran = Transactions(
        id = '123456789',
        action = 'Add',
        domain = 'example.com',
        soa = {
		"mname": "ns1.example.com",
		"rname": "admin.example.com",
		"serial": "{time}",
		"refresh": 3600,
		"retry": 600,
		"expire": 30,
		"minimum": 86400
        },
        ns = [
		{"host": "ns1.example.com"},
		{"host": "ns2.example.com"}
	    ],
        a = [
		{"name": "@",
		  "ttl": 400,
		  "value": "192.168.1.7"
		},
		{"name": "@",
		  "ttl": 400,
		  "value": "11.0.0.2"
		},
		{"name": "@",
		  "ttl": 400,
		  "value": "11.0.0.3"
		}
	    ],
        ttl = 3600,
        timestamp = timestamp
    )
    try :
        db.session.add(tran)
        db.session.commit()
    except:
        db.session.rollback()
        print('Can not add tran')

def getTransaction():
    return Transactions.query.all()

def merge_obj(obj, merge_obj):
    for property in merge_obj:
        obj[property] = merge_obj[property]
    return obj


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
    # To String 

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Blocks(db.Model):
    __tablename__ = 'blocks'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    nonce = db.Column(db.Integer, nullable=False)
    transactions = db.Column(db.JSON, nullable=False)
    previous_hash = db.Column(db.String(255), nullable=False)
    # ===============
    node_id = db.Column(db.String(64), db.ForeignKey('nodes.id'))
    add_by_node_id = db.Column(db.String(64), nullable=True)
    mined_transactions = db.relationship('Transactions', backref="block")
    hash = None
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def from_dict(self, json):
        self.id                 = json['id']
        self.timestamp          = float(json['timestamp'])
        self.nonce              = int(json['nonce']) 
        self.transactions       = json['transactions']
        self.previous_hash      = json['previous_hash'] 
        self.node_id            = json['node_id'] 
        self.add_by_node_id     = json['add_by_node_id'] if 'add_by_node_id' in json else None
        return self
        
    def hash(self):
        block_string = json.dumps(
            self.as_dict(), sort_keys=True).encode()
        hash = hashlib.sha256(block_string).hexdigest()
        return hash
     
class Transactions(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    action = db.Column(db.String(64), nullable=False)
    domain = db.Column(db.String(64), nullable=False)
    soa = db.Column(db.JSON, nullable=True)
    ns = db.Column(db.JSON, nullable= True)
    a = db.Column(db.JSON, nullable = False)
    ttl = db.Column(db.Integer, nullable= False)
    timestamp = db.Column(db.Float, nullable=False)
    # ===============
    account_id = db.Column(db.Integer(), db.ForeignKey('accounts.id'), nullable=True)
    block_id  = db.Column(db.Integer(), db.ForeignKey('blocks.id'), nullable=True)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def hash(self):
        block_string = json.dumps(
            self.as_dict(), sort_keys=True
        ).encode()
        hash = hashlib.sha256(block_string).hexdigest()
        return hash
    
    def block_tx_format(self):
        return  self.hash() + '|' + str(self.id) 

    def datetime_format(self):
        return datetime.fromtimestamp(self.timestamp).strftime("%d/%m/%Y, %H:%M:%S") if self.timestamp else None

class Records :
    def __init__(self, transaction = None) :
        self.domain = ''
        self.soa = None 
        self.ns  = None
        self.a   = None
        self.ns_count = None
        self.a_count  = None
        self.ttl = 3600,
        self.account_id = 0
        if transaction :
            return self.fromTransaction(transaction)
    
    def fromTransaction(self, transaction):
        self.domain     = transaction.domain
        self.soa        = transaction.soa
        self.ns         = transaction.ns
        self.ns_count   = len(transaction.ns) if self.ns else 0
        self.a          = transaction.a
        self.a_count    = len(transaction.a) if self.a else 0
        self.ttl        = transaction.ttl
        self.account_id = transaction.account_id

class Message:
    @staticmethod
    def getMessage( action, status, inserted_value = None ):
        messages = {
            'AccountLogin' : {
                403: 'Wrong email or password',
                404: 'This account haven\'t registered yet',
                200: 'Sign in successfully',
            },
            'AccountRegister' : {
                501: 'Please choose another email. This one is taken',
                500: 'Wrong format input',
                404: 'Already have had this email',
                401: 'Sorry ! There is error in database',
                200: 'Sign up successfully',
            },
            'BlockMining' :{
                501: 'Mining block didn\'t return value',
                500: f'Don\'t have enough {inserted_value} transactions to start mining',
                404: 'Something goes wrong with adding progress in mining',
                200: 'Mine block successfully',
            }
        }
        if action and action in messages :
            return messages[action][status] if messages[action].get(status) else 'Unexpected problem'
        return 'Message not found'
