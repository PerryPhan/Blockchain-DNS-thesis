from include import db, json, hashlib
''' 
    This file stores what is necessary in Database PgSQL 
'''

def recreate():
    db.drop_all()
    db.create_all()

def set():
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
        print('Can not add block')

def merge_obj(obj, merge_obj):
    for property in merge_obj:
        obj[property] = merge_obj[property]
    return obj

def get():
    return Blocks.query.filter(
            Blocks.id == 1,
    ).first()

def getModelDict(model):
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns)

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
    # transactions = db.relationship('Transactions',backref="owner")
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
     
class Transaction:
    TRANSACTIONS = []


class Record:  # main content of transaction and Others
    pass


# recreate()