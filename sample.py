# from models import db, generate_password_hash, random
import random, json
# from models import Accounts, Transactions
# Accounts -------------------------------------------------------
# db.session.add(
#     Accounts( 
#         fullname='Phan Dai',
#         email='phandai@admin.com',
#         password=generate_password_hash('Phandai2@'),
#         type_cd=1, # ADMIN 
#         is_deleted=False
#     )
# ) 
# Nodes ----------------------------------------------------------
# Transactions ---------------------------------------------------
numberOfTransactions = 10
def autoInsertTransaction(number):
    HEADER = "#[domain] [type] [ip] [port] [ttl-Timetolive]\n"
    CONTENTS = []
    FILENAME = 'names.txt'

    def generateDomains(number):
        FILE = FILENAME
        list = []
        numberOfLine = 0
        with open(FILE) as file:
            for line in file:
                list.append(line[:-1].lower() + '.bit')
                numberOfLine = numberOfLine + 1
        numberOfLine = 100 if numberOfLine == 0 else numberOfLine
        return [ list[random.randint(i, numberOfLine)] for i in range(0,number)]
    
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
    
    def generateRecordTransaction(domain, ip, type = 'A', port = 80, ttl = 14400):
        return {
            'domain' : domain,
            'type' : type,
            'ip' : ip,
            'port' : port,
            'ttl' : ttl
        }
    
    domains = generateDomains(number)
    ips = generateIPs(number)
    trans = [ generateRecordTransaction( domains[i], ips[i] ) for i in range(number)]
    CONTENTS = [ f"{tran['domain']} {tran['type']}  {tran['ip']} {tran['port']} {tran['ttl']}\n" for tran in trans]
    
    f = open("sample.txt", "w")
    f.write(HEADER)
    for content in CONTENTS:
        f.write(content)
    f.close()
    
    
    return json.dumps({
        'len' : len(trans),
        'transactions' : trans
    })
    # for i in range( number ):
    #     db.session.add(Transactions( 
    #         hostname= domains[i],
    #         ip= ips[i],
    #         reward= reward,
    #         port= port)) 

autoInsertTransaction(numberOfTransactions)
# Blocks ---------------------------------------------------------
# PUSH ALL >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# db.session.commit()