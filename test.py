# Đi từ 1. - 8. trong mô hình nguyên lý hoạt động
# 1, 2, 7, 8. Tạo form để nhập record hoặc import file .txt, sau đó gửi lên Database ( Quan trọng )
# > Database dưới dạng Blockchain sẽ lưu như thế nào ? - Blocks
# > Một Block như vậy thì sẽ lưu gì để đáp ứng nhu cầu biến hóa của Transaction ? - JSON
# > Khi tạo một Block thì sẽ có các bước gì 
# FUNC : INSERT, SELECT, BACKUP

RECORD_FORMAT = {
    'domain' : 'example.com', # Tên miền
    'type'   : 'A',           # Loại record
    'value'  : '192.0.2.1',   # Giá trị IP
    'ttl'    : 14400          # Thời gian tồn tại
}
import hashlib, json
# import threading
import time, re
from copy import copy
from database import Blocks
from business import TransactionBusiness
block = {
    'nonce': 0,
    'hash' : '',
    'id' : 1,
}
list = []

# def proofOfWork( block, index ):
#     '''
#         Proof of work will generate Nonce number until match condition 
#         Hash x nonce = Hash ['0x + 63chars']
#     '''
#     def getModelDict(model):
#         return dict((column.name, getattr(model, column.name))
#                     for column in model.__table__.columns)

#     def hash(block):
#         block_string = json.dumps(
#             (block), sort_keys=True).encode()
#         return hashlib.sha256(block_string).hexdigest()
    
#     DIFFICULTY = 3
#     block['hash'] = hash(block)
#     block['nonce'] = 0
#     block['id'] = index
    
#     while not block['hash'].startswith('0' * DIFFICULTY):
#         block['nonce'] += 1
#         block['hash'] = hash(block)
#     list.append(block)

#     print("Time to do task #",index," : ", time.perf_counter())

#     return block

# Demo : Testing 3 threads in local 
# for i in range(3):
#     x = threading.Thread(target=proofOfWork, args=[block, i])
#     x.start()

# for i in range(3):
#     x.join()

# # Real : 
# for (index, item) in enumerate(list):
#     print(f'------------------- Block {index} ----------------------------') 
#     print(' ',item)
#     print(f'------------------- { time.perf_counter() }-------------\n') 


# print(threading.active_count())
# print(threading.enumerate())
# print(time.perf_counter())

def proofOfWork( block):
    '''
        Each time, proof of work will be called by many request, so must gain its prop 'node_id' 
        Proof of work will generate Nonce number until match condition 
        Hash x nonce = Hash ['0x + 63chars']
    '''
    DIFFICULTY = 3
    
    def hash(block):
        block_string = json.dumps(
            block.as_dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    block.hash = hash(block)
    block.nonce = 0
    while not block.hash.startswith('0' * DIFFICULTY):
        block.nonce += 1
        block.hash = hash(block)

    return block

block_request = {
    "0": "a A 1.1.1.1 80 14400",
    "1": "a A 1.1.1.1 80 14400",
    "2": "a A 1.1.1.1 80 14400",
    "3": "a A 1.1.1.1 80 14400",
    "4": "a A 1.1.1.1 80 14400",
    "5": "a A 1.1.1.1 80 14400",
    "6": "a A 1.1.1.1 80 14400",
    "7": "a A 1.1.1.1 80 14400",
    "8": "a A 1.1.1.1 80 14400",
    "9": "a A 1.1.1.1 80 14400",
    "10": "a A 1.1.1.1 80 14400",
    "11": "a A 1.1.1.1 80 14400",
    "12": "a A 1.1.1.1 80 14400",
    "13": "a A 1.1.1.1 80 14400",
    "14": "a A 1.1.1.1 80 14400",
    "15": "a A 1.1.1.1 80 14400",
    "16": "a A 1.1.1.1 80 14400",
    "17": "a A 1.1.1.1 80 14400",
    "id": "3",
    "node_id": "9d8a4a0554334c76ba029ad3cdf45d4d",
    "nonce": "0",
    "previous_hash": "4bcf60a6651a53c1a40d5e510cedf9ca37ca804de48650ff56027480af9d7421",
    "timestamp": "1636553694.7218995",
    "transactions": "18"
}

RECORD_FORMAT = {
    'domain' : '^[a-zA-Z0-9][a-zA-Z0-9-_]{0,61}[a-zA-Z0-9]{0,1}\.([a-zA-Z]{1,6}|[a-zA-Z0-9-]{1,30}\.[a-zA-Z]{2,3})$',   # Tên miền, ex : example.com
    'a' : {
        'ip' : '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',   # Giá trị IP , ex : 1.1.1.1
        'port'   : '^[1-9][0-9]{1,3}$',   # Giao thức cổng , ex: 80 ( HTTP )
        'ttl'    : '^[1-9]{1}[0-9]{1,4}$' # Thời gian tồn tại, ex : 14400 ( 4h )
    }
}

def checkTransactionFormat( domain, a, soa = None, ns = None, account_id = None):
    # TODO : check like account
    checked = copy(RECORD_FORMAT)
    checked['domain'] = True if domain and re.match(checked['domain'], domain ) else False
    if 'a' in checked :
        regex = copy(checked['a'])
        checked['a'] = []
        checked['port'] = []
        checked['ttl'] = []
        for a_record in a :
            
            # Check A IP ----------------------------------------------------------------------
            if 'ip' in a_record and a_record['ip'] and re.match(regex['ip'], a_record['ip']):
                checked['a'].append(True)
            else :
                checked['a'].append(False)

            # Check A PORT ----------------------------------------------------------------------
            if 'port' in a_record and a_record['port'] and re.match(regex['port'], a_record['port']):
                checked['port'].append(True)
                print( "CHECKING IP PORT : ",regex['port'], a_record['port'], True if re.match(regex['port'], a_record['port']) else False)
            else :
                checked['port'].append(False)

            # Check A TTL ----------------------------------------------------------------------
            if 'ttl' in a_record :
                if a_record['ttl'] and re.match(regex['ttl'], a_record['ttl']):
                    checked['ttl'].append(True)
                else:
                    checked['ttl'].append(False)
            else:
                checked['ttl'].append(False)
            
            print( "CHECKING IP ADDRESS : ", a_record['ip'] or None, True if 'ip' in a_record and a_record['ip'] and re.match(regex['ip'], a_record['ip']) else False)
            print( "CHECKING IP PORT : ", a_record['port'] or None, True  if 'port' in a_record and a_record['port'] and re.match(regex['port'], a_record['port']) else False)
            print( "CHECKING IP TTL : ", a_record['ttl'] or None ,True if 'ttl' in a_record and a_record['ttl'] and re.match(regex['ttl'], a_record['ttl']) else False)
            
            print()

        checked['a'] = all( checked['a'] )
        checked['port'] = all( checked['port'] )
        checked['ttl'] = all( checked['ttl'] )
    
    print('A after checking: ',checked['a'] )
    print('Port after checking: ',checked['port'] )
    print('Ttl after checking: ',checked['ttl'] )
    print('After all, checked will be: ',checked)
    return all( [ checked[key] for key in checked.keys() ] )

# record = {
#     'domain': 'example.com',
#     'a' : [{
#         'ip': '1.1.1.a',
#         'port': '80',
#         'ttl': '14400',
#     },{
#         'ip': '1.1.1.2',
#         'port': '80',
#         'ttl': '14400',
#     },
#     # {
#     #     'ip': '1.1.1.3',
#     #     'port': '80',
#     #     'ttl': '0',
#     # }
#     ]
# }

# print ('CHECKED : ', checkTransactionFormat(
#     **record
# ))

# def testUpdate():
#     tx = TransactionBusiness()
#     tran_list = tx.getTransactionsPool()
#     if tran_list :
#         old_tran = tran_list[0]
#         tran = copy(old_tran) 
#         tran.id = '123123123'
#         tx.updateTransaction( old_tran, tran)

# testUpdate()


import os 
# os.system('run_server.sh')

food = 0 
import threading

def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()

def foo():
    global food
    food += 2
    print( food )

# using
setInterval(foo,2)