from include import db
''' 
    This file stores what is necessary in Database PgSQL 
'''


def recreate():
    db.drop_all()
    db.create_all()


def get_model_dict(model):
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
    hash = None
    
    
class Transaction:
    TRANSACTIONS = []


class Record:  # main content of transaction and Others
    pass
