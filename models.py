from app import db, generate_password_hash, random

db.drop_all()

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

db.create_all()
