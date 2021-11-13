from sqlalchemy.orm import  sessionmaker, declarative_base
from sqlalchemy import Boolean ,Column, String, Integer, create_engine

Base = declarative_base()
Session = sessionmaker()
engine = create_engine('postgresql://postgres:1234@localhost/dnschain',echo = True)

class Test(Base):
    __tablename__ = 'test'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    fullname = Column(String(40), nullable=False)
    
# Base.metadata.create_all(engine)

local_session = Session(bind = engine)
tests = local_session.query(Test).all()
for test in tests:
    new_test = local_session.query(Test).filter_by( id = test.id ).all()
