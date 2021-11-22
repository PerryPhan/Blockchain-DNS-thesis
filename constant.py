# For Configuration purpose ---------------
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/dnschain'
SESSION_TYPE = 'sqlalchemy'
UPLOAD_FOLDER = 'uploads'

# For Managing purpose --------------------
''' 
    This file stores declaration of Global Constant 
'''
MESSAGE = {
    'FileError01' : 'File not found in request',
    'FileError02' : 'File don\'t have a name',
    'FileError03' : 'File wrong format',
}
IP_FORMAT = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
RECORD_FORMAT = {
    'domain' : '^[a-zA-Z0-9][a-zA-Z0-9-_]{0,61}[a-zA-Z0-9]{0,1}\.([a-zA-Z]{1,6}|[a-zA-Z0-9-]{1,30}\.[a-zA-Z]{2,3})$',   # Tên miền, ex : example.com
    'a' : {
        'value' : IP_FORMAT,   # Giá trị IP , ex : 1.1.1.1
        'port'   : '^[1-9][0-9]{1,3}$',   # Giao thức cổng , ex: 80 ( HTTP )
        'ttl'    : '^[1-9]{1}[0-9]{1,4}$' # Thời gian tồn tại, ex : 14400 ( 4h )
    }
}

ACCOUNT_FORMAT = {
    'fullname'  : '^[a-zA-Z]+[ a-zA-Z]*$',
    'email'     : '^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
    'password'  : '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$@!%&*?])[A-Za-z\d#$@!%&*?]{8,30}$',
    'repassword': '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$@!%&*?])[A-Za-z\d#$@!%&*?]{8,30}$',
    'type_cd'   : '^[0-9]+$'
}


COMMENT_CHAR  = '#' 
SPECIAL_CHARS = "''!@#$%^&*()-+?_=,<>/"""