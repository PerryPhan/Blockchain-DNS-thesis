from models import db, generate_password_hash, random
from models import Accounts, Transactions
# Accounts -------------------------------------------------------
db.session.add(
    Accounts( 
        fullname='Phan Dai',
        email='phandai@admin.com',
        password=generate_password_hash('Phandai2@'),
        type_cd=1, # ADMIN 
        is_deleted=False
    )
) 
# Nodes ----------------------------------------------------------
# Transactions ---------------------------------------------------
numberOfTransactions = 10
def autoInsertTransaction(number):
    def generateDomains(number):
        FILE = 'words.txt'
        list = []

        with open(FILE) as file:
            for line in file:
                list.append(line[:-1] + '.bit')

        return list
    def generateIPs(number):
        FROM = 0
        TO = 255
        list = []
        for i in range( number ):
            ip = '192.168.'
            ip += str( random.randint( FROM, TO ) )  or '0' 
            ip += '.'
            ip += str( random.randint( FROM, TO ) )  or '0' 
            list.append(ip)
        return list
    ips = generateIPs(number)
    domains = generateDomains(number)
    reward = 10
    port = 80
    for i in range( number ):
        db.session.add(Transactions( 
            hostname= domains[i],
            ip= ips[i],
            reward= reward,
            port= port)) 
autoInsertTransaction(10)
# Blocks ---------------------------------------------------------
# PUSH ALL >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
db.session.commit()