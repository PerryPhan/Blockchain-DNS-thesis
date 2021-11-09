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
import threading
import time

block = {
    'nonce': 0,
    'hash' : '',
    'id' : 1,
}
list = []
def proofOfWork( block, index ):
    '''
        Proof of work will generate Nonce number until match condition 
        Hash x nonce = Hash ['0x + 63chars']
    '''
    def getModelDict(model):
        return dict((column.name, getattr(model, column.name))
                    for column in model.__table__.columns)

    def hash(block):
        block_string = json.dumps(
            (block), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    DIFFICULTY = 3
    block['hash'] = hash(block)
    block['nonce'] = 0
    block['id'] = index
    
    while not block['hash'].startswith('0' * DIFFICULTY):
        block['nonce'] += 1
        block['hash'] = hash(block)
    list.append(block)

    print("Time to do task #",index," : ", time.perf_counter())

    return block

# Demo : Testing 3 threads in local 
for i in range(3):
    x = threading.Thread(target=proofOfWork, args=[block, i])
    x.start()

for i in range(3):
    x.join()

# Real : 
for (index, item) in enumerate(list):
    print(f'------------------- Block {index} ----------------------------') 
    print(' ',item)
    print(f'------------------- { time.perf_counter() }-------------\n') 


print(threading.active_count())
print(threading.enumerate())
print(time.perf_counter())

