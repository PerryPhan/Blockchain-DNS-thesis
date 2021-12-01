from database import recreate
from business import NodesBusiness, AccountBusiness
import socket, random, re
from werkzeug.security import generate_password_hash

# recreate()
# CREATE NODES 
nodes = NodesBusiness()
host = socket.gethostbyname(socket.gethostname())
port = 5000
FILENAME = 'names.txt'
number = 10

def generateName(number):
    FILE = FILENAME
    list = []
    numberOfLine = 0
    # Read File  
    with open(FILE) as file:
        for line in file:
            list.append(line[:-1].lower())
            numberOfLine = numberOfLine + 1

    numberOfLine = 100 if numberOfLine == 0 else numberOfLine
    return [list[random.randint(i, numberOfLine)] for i in range(0, number)]

def create_nodes( number ):
    # Get random names
    names = generateName(number)

    for i in range(number):
        print( str(i), ". " )
        node, code = nodes.handleNodeInformation( host , port , True, 'Node '+ names[i] , False)
        print( " NODE ",{
                node.id,
                host,
                port,
                node.nodename
        }," with code ", code ) 
        if code == 200 :
            admin, status = create_admin(node, names[i])
            if status == 200:
                node.account_id = admin.id
                nodes.updateNode(node)

# CRAETE ADMIN
accounts = AccountBusiness()
def create_admin(node, name):
    # Get random fullname
    fullname = name + ' ' + name
    email = name + '@' + ''.join(re.split('\W+', node.nodename.lower())) + '.dnschain'
    secret = 'Phandai2@'
    type_cd = 1 

    admin, status =  accounts.newAccount(fullname, email, secret, secret, type_cd) 
    status = accounts.addAccount( admin )
    print( "ADMIN ",{
        fullname,
        email,
    }," with code ", status )
    return admin, status

create_nodes(number)