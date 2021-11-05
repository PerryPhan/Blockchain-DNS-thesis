from app import db
class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    list_of_items = db.Column(db.JSON, nullable=False)
db.drop_all()
db.create_all()
