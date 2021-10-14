class AccountSchema():
    FULLNAME = 'fullname'
    EMAIL = 'email'
    PASSWORD = 'password'
    REPASSWORD = 'repassword'
    TYPE_CD = 'type_cd'
    message = {
        # Register
        'RE010001': 'Error in connecting Database',
        'RE010002': 'Error in code : Not found request or resolve or reject',
        'RE010003': 'Validating failed : Not match input type',
        'RE010004': 'Validating failed : This email is already registed',
        'RE01XXXX': 'Registering successfully',
        # Login
        'LO010001': 'Validating failed: Wrong password' 
    }


