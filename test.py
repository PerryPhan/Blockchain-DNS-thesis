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
tb = TransactionBusiness()
# def convertBlockFromBlockRequest( block_request ):
#     #   convert array of transactions
#     transactions = [ tb.formatRecord(block_request[prop]) if re.match('^\d+$',prop) else None for prop in block_request.keys()]
#     transactions = transactions[0: int(block_request['transactions'])]
#     #   new block , add node_id 
#     block_request['transactions'] = transactions
#     block_request['add_by_node_id'] = '1'
#     block = Blocks().from_dict(block_request)
#     #   proof of work 
#     proofOfWork(block)
#     # print(block.as_dict())
#     print(block.hash, block.nonce)
#     print(time.perf_counter())

# convertBlockFromBlockRequest(block_request)
max_len = 20 
transactions = [
    {
       'domain': 'a.com',
        'type': 'A',
        'ip': f'{i}.{i}.{i}.{i}',
        'port': 80,
        'ttl': '14400'
    } for i in range(20)
]
def subTransaction(arr, index, length):
    # if not length :
    #     return arr[index: ]
    # else: 
        return arr[index: length]
    
def prepareMiningBlockTransactions(transactions):
    trans_len = len(transactions) 
    if trans_len >= max_len: # and create_block_countdown end
        return subTransaction(transactions, 0, max_len), subTransaction(transactions, max_len, None)
    else: 
        return transactions, 500 # not enough transactions 
used, left = prepareMiningBlockTransactions(transactions)
print("Used transactions :")
for i in used : 
    print(json.dumps(i))
print("Left transactions :")
for i in left : 
    print(json.dumps(i))
# print( subTransaction(transactions, 10, 1) )