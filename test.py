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

from business import *

bc = Blockchain()
bc.current_transactions = ['1','2','3','4']
print ( bc.addBlock() )

