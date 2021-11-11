from include import *
''' 
    This file stores declaration of Global Constant 
'''
MESSAGE = {
    'FileError01' : 'File not found in request',
    'FileError02' : 'File don\'t have a name',
    'FileError03' : 'File wrong format',
}

RECORD_FORMAT = {
    'domain' : '^[a-zA-Z0-9][a-zA-Z0-9-_]{0,61}[a-zA-Z0-9]{0,1}\.([a-zA-Z]{1,6}|[a-zA-Z0-9-]{1,30}\.[a-zA-Z]{2,3})$',   # Tên miền, ex : example.com
    'type'   : '^A$',   # Loại record, ex : A, CNAME
    'ip'     : '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',   # Giá trị IP , ex : 1.1.1.1
    'port'   : '^[1-9][0-9]{1,3}$',   # Giao thức cổng , ex: 80 ( HTTP )
    'ttl'    : '^[0-9]{1,5}$' # Thời gian tồn tại, ex : 14400 ( 4h )
}


COMMENT_CHAR  = '#' 
SPECIAL_CHARS = "''!@#$%^&*()-+?_=,<>/"""