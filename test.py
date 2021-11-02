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