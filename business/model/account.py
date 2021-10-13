class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(40))

    def __init__(self, fname):
        self.fname = fname