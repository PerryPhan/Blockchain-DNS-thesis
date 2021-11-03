class A:
    REWARD = 0
    def __init__(self, reward) :
        self.REWARD = reward
        print('REWARD = ',self.REWARD)

    def calc(self, multi = REWARD) :
        print('MULTI = ',multi)
        return self.REWARD*multi
class B:
    a = A(10)

b = B()
print( b.a.calc() ) 
from models import Parent, db
parent_one = Parent(list_of_items=[{
    'id': '1',
    'name': 'Dai'
}, {
    'id': '2',
    'name': 'Duc    '}]) 
db.session.add(parent_one)
db.session.commit()
# Each one when query here, it'll become Type 'dict'

