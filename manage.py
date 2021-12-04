from include import *
from business import *


# Declare -------------------------------------------------
accountBusiness = AccountBusiness()
dns = DNSResolver()
# -FRONT --------------------------------------------------
# FOR INDEX
# --------------------------------------------------


@app.route('/')
def home():
    return redirect('/dashboard/transactions')


@app.route('/admin')
def manager():
    if session:
        if 'account' in session:
            if session['account']['type_cd'] == 1:  # admin access
                account_options = {
                    'account_id': session['account']['id'],
                    'account_fullname': session['account']['fullname']
                }
            return redirect('/admin/blocktxs')
    session['regis_email'] = dns.blockchain.nodes.getNode().admin.email

    return redirect('/login')

# -FRONT --------------------------------------------------
# FOR ADMIN
# --------------------------------------------------


@app.route('/admin/blocktxs', methods=['GET', 'POST'])
def blocks_txs_manager():
    # How to know that is his first time => This onl IP was his computer and don't have this email in DB
    # If he try to log again will be email and password empty
    admin = accountBusiness.getAccountById(
        session['account']['id']
    )
    count = dns.blockchain.countBlocksList()
    limit = 3

    # Default
    page = 1
    pages = 1
    offset = 0
    list_of_blocks = []
    list_of_transaction = []

    # Has items
    if count > 0:
        # Page
        page = request.args.get('page', default=1, type=int)
        id = request.args.get('id', default=1, type=int)
        pages = math.ceil(count / limit)

        # Condition
        
        if id <= 0:
            id = 1
        elif id > count:
            id = count
             
        if page <= 0:
            page = 1
        elif page > pages:
            page = pages
        
        # Number
        offset = (page-1) * limit
        list_of_blocks = dns.blockchain.getListBlocksWithOffsetAndLimit(offset, limit)
        list_of_transaction = dns.blockchain.getBlockTransactionWithId(id)
        
    html_options = {
        'title': 'Blocks and Txs manager',
        'admin': admin,
        'id': id,
        # Data 
        'wallet': dns.blockchain.wallet,
        'genesis': dns.blockchain.getGenesisBlock(),
        'node': dns.blockchain.nodes.getNode(),
        # Pagination
        'page': page,
        'previous_page': page - 1 if page - 1 > 1 else 1,
        'next_page': page + 1 if page + 1 < pages else pages,
        'pages': pages,
        'count': count,
        'list_of_blocks': list_of_blocks,
        'list_of_transaction': list_of_transaction,
    }
    if request.method == 'POST':
        # If the first time login in
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        type_cd = 1

        # else show login form
        account, status = accountBusiness.newAccount(
            fullname, email, password, repassword, type_cd)

        return {
            'status': status,
            'account': account.as_dict() if account else None,
        }

    return render_template('_admin_blocktx_manager_template.html', **html_options)


@app.route('/admin/nodes', methods=['GET', 'POST'])
def nodes_manager():
    # How to know that is his first time => This onl IP was his computer and don't have this email in DB
    # If he try to log again will be email and password empty
    count = dns.blockchain.nodes.countNetwork()
    limit = 7

    # Default
    page = 1
    pages = 1
    offset = 0
    list_of_nodes = []
    this_node = None

    # Has items
    if count > 0:
        # Page
        page = request.args.get('page', default=1, type=int)
        pages = math.ceil(count / limit)

        # Condition
        if page <= 0:
            page = 1
        if page > pages:
            page = pages

        # Number
        offset = (page-1) * limit

        list_of_nodes = dns.blockchain.nodes.getNetworkWithOffsetAndLimit(
            offset, limit)
        this_node = dns.blockchain.nodes.getNode()
    
    admin = accountBusiness.getAccountById(
        session['account']['id']
    )

    html_options = {
        'title': 'Nodes manager',
        # Pagination
        'page': page,
        'previous_page': page - 1 if page - 1 > 1 else 1,
        'next_page': page + 1 if page + 1 < pages else pages,
        'pages': pages,
        'count': count,
        'list_of_nodes': list_of_nodes,
        'this_node': this_node,
        'admin': admin,

    }

    return render_template('_admin_nodes_manager_template.html', **html_options)


@app.route('/admin/accounts', methods=['GET', 'POST'])
def account_manager():
    # How to know that is his first time => This onl IP was his computer and don't have this email in DB
    # If he try to log again will be email and password empty
    count = accountBusiness.countListAccounts()
    limit = 7

    # Default
    page = 1
    pages = 1
    offset = 0
    list_of_accounts = []

    # Has items
    if count > 0:
        # Page
        page = request.args.get('page', default=1, type=int)
        pages = math.ceil(count / limit)

        # Condition
        if page <= 0:
            page = 1
        if page > pages:
            page = pages

        # Number
        offset = (page-1) * limit

        list_of_accounts = accountBusiness.getListAccountsWithOffsetAndLimit(
            offset, limit)
    
    admin = accountBusiness.getAccountById(
        session['account']['id']
    )
    html_options = {
        'title': 'Accounts manager',
        # Pagination
        'page': page,
        'previous_page': page - 1 if page - 1 > 1 else 1,
        'next_page': page + 1 if page + 1 < pages else pages,
        'pages': pages,
        'count': count,
        'list_of_accounts': list_of_accounts,
        'admin': admin,
    }

    return render_template('_admin_accounts_manager_template.html', **html_options)

# -FRONT --------------------------------------------------
# FOR DASHBOARD
# --------------------------------------------------


@app.route('/dashboard/transactions')
def dashboardTransactions():
    if( dns.blockchain.transactions.countAllNoBlockTransactions() > 0) :
        pass
    # Pagination
    count = dns.blockchain.transactions.countAllTransactions()
    no_block_count = dns.blockchain.transactions.countAllNoBlockTransactions()
    limit = 10

    # Default
    page = 1
    pages = 1
    offset = 0
    list = []

    # Has items
    if count > 0:
        # Page
        page = request.args.get('page', default=1, type=int)
        pages = math.ceil(count / limit)

        # Condition
        if page <= 0:
            page = 1
        if page > pages:
            page = pages

        # Number
        offset = (page-1) * limit
        list = dns.blockchain.transactions.getListTransactionstsWithOffsetAndLimit(
            offset, limit)

    html_options = {
        'type': 1,
        'title': 'Transaction Dashboard ',
        'unit': 'tx',
        # Pagination
        'list': list,
        'node': dns.blockchain.nodes.node,
        'page': page,
        'previous_page': page - 1 if page - 1 > 1 else 1,
        'next_page': page + 1 if page + 1 < pages else pages,
        'pages': pages,
        'count': count,
        'no_block_count': no_block_count,
        'buffer_len': BUFFER_MAX_LEN,
    }

    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname'],
                'isAdmin': session['account']['type_cd'] == 1
            }
            return render_template('_dashboard_template.html', **html_options, **account_options)

    return render_template('_dashboard_template.html', **html_options)


@app.route('/dashboard/domains')
def dashboardDomains():
    # Pagination
    all =  dns.blockchain.transactions.getDomainList()
    count = len(all)
    limit = 10

    # Default
    page = 1
    pages = 1
    offset = 0
    list = []

    # Has items
    if count > 0:
        # Page
        page = request.args.get('page', default=1, type=int)
        pages = math.ceil(count / limit)

        # Condition
        if page <= 0:
            page = 1
        if page > pages:
            page = pages

        # Number
        offset = (page-1) * limit
        list = all[offset : offset + limit]

    html_options = {
        'type': 2,
        'title': 'Domains Dashboard ',
        'unit': 'domains',
        # Pagination
        'list': list,
        'node': dns.blockchain.nodes.node,
        'page': page,
        'previous_page': page - 1 if page - 1 > 1 else 1,
        'next_page': page + 1 if page + 1 < pages else pages,
        'pages': pages,
        'count': count,
    }

    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname'],
                'isAdmin': session['account']['type_cd'] == 1
            }
            return render_template('_dashboard_template.html', **html_options, **account_options)

    return render_template('_dashboard_template.html', **html_options)


@app.route('/dashboard/transactions/detail')
def detailDashboardTransactions():
    
    idhash = request.args.get('idhash', default='', type=str)
    if idhash == '' : 
        return redirect('/dashboard/transactions')

    tran, status = dns.blockchain.transactions.getTransactionWithIdHash(idhash)
    if status != 200 : 
        return redirect('/dashboard/transactions')

    html_options = {
        'type': 1,
        'title': 'Transaction Detail',
        'unit': 'tx',
        # Transaction
        'tran': tran,
        'node': dns.blockchain.nodes.node,
        'record': Records(tran)
    }

    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname'],
                'isAdmin': session['account']['type_cd'] == 1
            }
            return render_template('_detail_dashboard_template.html', **html_options, **account_options)

    return render_template('_detail_dashboard_template.html', **html_options)


@app.route('/dashboard/domains/detail')
def detailDashboardDomains():
    domain = request.args.get('domain', default='', type=str)
    record = dns.blockchain.transactions.getDomain(domain)
    html_options = {
        'type': 2,
        'title': 'Domains Detail',
        'unit': 'domains',
    }

    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname'],
                'isAdmin': session['account']['type_cd'] == 1
            }
            # Transaction Domain
            return render_template('_detail_dashboard_template.html', **html_options, **account_options, record = record)
    
    # Transaction Domain
    return render_template('_detail_dashboard_template.html', **html_options, record = record)


@app.route('/dashboard/operation', methods=['GET', 'POST'])
def dashboard_operation():
    ALLOWED_EXTS = {"txt", "zone"}
    all_transactions = dns.blockchain.transactions.getAllTransactions()
    
    def checkFileNameFormat(filename):
        # Check file name
        if filename == '':
            return filename, 404

        # Check file extension
        if '.' in filename and len(filename.rsplit('.')) == 3 and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTS == False:
            return filename, 500

        # Format that filename can store any where
        filename = secure_filename(filename)
        return filename, 200

    def handleOneRecordForm(form):
        action = 'update' if dns.blockchain.transactions.getDomain( form['domain'], all_transactions) else 'add'
        # New transaction
        transaction, status = dns.blockchain.transactions.newTransaction(
            form, session['account']['id'], action, True
        )
        # Add single Transaction
        status = dns.blockchain.transactions.addTransaction(transaction)
        message = Message.getMessage('TransactionAdding',status )
        
        return  {
            'status': status,
            'message': message,
            'transaction' : transaction if status == 200 else None,
        }

    def handleMultipleRecordsForm(files):
        errors = []
        records = {}
        transactions_arr = []
        status = 404
        
        for file in files:
            # Check
            filename, status = checkFileNameFormat(file.filename)
            if status != 200:
                errors.append(filename)
            else:
                # Upload and save file 
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                # Open 
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        records[data['$origin']] = data
                    except: 
                        errors.append(filename)
                        pass
                    
        if len(records) > 0:
            if len(files) == len(records) : # Enough files
                status = 200
            else : # Not enough files
                status = 202
        else : # No files
            status = 500
            
        data_errors = []
        insert_value = ''

        if status != 500:     
            for record in records.values():
                data_action = 'update' if dns.blockchain.transactions.getDomain( record['$origin'], all_transactions ) else 'add'
                data_tran, data_status = dns.blockchain.transactions.newTransaction(
                    record, session['account']['id'], data_action
                )
                if data_status != 200: 
                    data_errors.append( record['$origin'] )
                else:
                   dns.blockchain.transactions.addTransaction(data_tran)
                   transactions_arr.insert(0, data_tran)
                
        if( len(data_errors) > 0 ) : 
            insert_value += 'data of domain '+','.join(data_errors)+' cannot process properly'
        
        if insert_value != '' :  insert_value += ' and '
        insert_value += ','.join(errors) + " wrong filename or expected $origin properties"
        
        message = Message.getMessage('TransactionAdding',status, insert_value )    
        
        return {
            'status': status,
            'message': message,
            'transactions': transactions_arr,
        }

    # Check account
    if not session or not 'account' in session:
        return redirect('/login')

    account_options = {
        'account_id': session['account']['id'],
        'account_fullname': session['account']['fullname'],
        'isAdmin': session['account']['type_cd'] == 1
    }
    
    # Check list of transaction that account created 
    transactions_list_by_account = dns.blockchain.transactions.getListTransactionsByAccount(account_options['account_id']) 
    html_options = {
        'title': 'Operation',
        'type': 3,
        **account_options,
        'transactions_list' : transactions_list_by_account,
        'unit': 'txs',
        'count': len(transactions_list_by_account)
    }
    appending_transactions = []
    if request.method == 'POST':
        response = {}
        if len(request.files.getlist('file')) != 0:
            files = request.files.getlist('file')
            response = handleMultipleRecordsForm(files)
            appending_transactions = response['transactions']
        else :    
            response = handleOneRecordForm(request.form)
            appending_transactions = [response['transaction']]

        current_transactions =  dns.blockchain.transactions.countAllNoBlockTransactions()
        if current_transactions != 0 and current_transactions >= BUFFER_MAX_LEN :
            # Pre mining
            transactions, status = dns.blockchain.prepareMiningBlockTransactions()
            if status == 500:
                return render_template('_operation_dashboard_template.html', **html_options, **response)

            # Mining
            block = dns.blockchain.mineBlock(transactions)

            if block:
                block, status = dns.blockchain.addBlock(block)
                dns.blockchain.transactions.setCurrentTxsBlockID(block.id)
                dns.blockchain.broadcastNewBlock()
            html_options['transactions_list'] = dns.blockchain.transactions.getListTransactionsByAccount(account_options['account_id'])          
        else:
            for tran in appending_transactions:  
                transactions_list_by_account.insert(0 ,tran)
            html_options['transactions_list'] = transactions_list_by_account
        return render_template('_operation_dashboard_template.html', **html_options, **response)
    
    return render_template('_operation_dashboard_template.html', **html_options)

# -FRONT --------------------------------------------------
# FOR LOGIN
# --------------------------------------------------


@app.route('/logout')
def logout():
    session.pop('account', None)
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    panel_options = {
        'panel_p_text': 'Haven\'t had an account?',
        'panel_a_link': '/register',
        'panel_a_text': 'Sign up',
    }
    html_options = {
        'title': 'Sign In',
        'form_header_title': 'Welcome to DNSChain',
        'form_header_action': 'Take advantage of your accessibility',
        'hero_image': 'img/hero-image.png',
        **panel_options
    }
    if request.method == 'POST':
        # Get email and password
        email = request.form.get('email')
        password = request.form.get('password')

        account, status = accountBusiness.authenticateAccount(email, password)
        # Return message
        message = Message.getMessage('AccountLogin', status)
        if account:
            account = account.as_dict()
            account['password'] = ''
            session['account'] = account

        response = {'status': status, 'message': message}
        return render_template('_login_template.html', **html_options, **response) if status != 200 else redirect('/dashboard/transactions')

    regis_email = ''
    if session and session.get('regis_email'):
        regis_email = session.get('regis_email')
        session.pop('regis_email', None)

    return render_template('_login_template.html', **html_options, regis_email=regis_email)


@app.route('/register', methods=['GET', 'POST'])
def register():
    panel_options = {
        'panel_p_text': 'Already have had an account?',
        'panel_a_link': '/login',
        'panel_a_text': 'Sign in',
    }
    html_options = {
        'title': 'Sign Up',
        'form_header_title': 'Become one with DNSChain',
        'form_header_action': 'Be with us, joy with us',
        'hero_image': 'img/hero-image3.png',
        **panel_options
    }
    if request.method == 'POST':
        # Check format and add new Account
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        type_cd = request.form.get('type_cd')

        account, status = accountBusiness.newAccount(
            fullname, email, password, repassword, type_cd)

        if account:
            status = accountBusiness.addAccount(account)

        # Return message
        message = Message.getMessage('AccountRegister', status)
        response = {'status': status, 'message': message}

        if status == 200:
            session['regis_email'] = email
        else:
            response['fullname'] = fullname
            response['email'] = email

        return render_template('_login_template.html', **html_options, **response)

    return render_template('_login_template.html', **html_options)


# -BACK ------------------------------------------------
# FOR DNS SERVER
# --------------------------------------------------
@app.route('/dns/load')
def load_domain_list():
    return {
        'status': 200,
        'data': dns.blockchain.transactions.getRawDomainData()
    }

# -BACK ------------------------------------------------
# FOR POSTMAN
# --------------------------------------------------


@app.route('/blockchain/transactions')
def showTransactionsBuffer():
    tranList = [tran.as_dict() for tran in dns.blockchain.current_transactions]
    return jsonify({
        'status': 200,
        'message': 'Show transaction successfully',
        'len': len(tranList),
        'trans': tranList,
    })


@app.route('/blockchain/dump')
def dumpChain():
    chain = dns.blockchain.dumpChain()

    return jsonify({
        'status': 200,
        'message': 'Getting chain successfully',
        'chain':
        {
            'len': len(chain),
            'blocks': chain,
        }
    })


@app.route('/dns/resolve', methods=['GET', 'POST'])
def resolve():
    # 1. Tạo route để phân giải
    if request.method == 'POST':
        tran, status = dns.lookup(request.form)
        message = 'Resolving successfully with inputed domain' if status == 200 else 'Not found record with inputed domain'
        return jsonify({
            'status': status,
            'method': 'POST',
            'message': message,
            'record': tran,
        })

    return jsonify({
        'status': 200,
        'method': 'GET',
        'message': 'Resolver webpage'
    })


@app.route('/blockchain/ledger')
def getLedger():
    ledger = dns.blockchain.ledger
    message = 'Getting ledger successfully'
    return jsonify({
        'status': 200,
        'message': message,
        'len': len(ledger),
        'ledger': ledger
    })


@app.route('/blockchain/wallet')
def getWallet():
    wallet = dns.blockchain.wallet
    message = 'Getting wallet successfully'
    return jsonify({
        'status': 200,
        'message': message,
        'wallet': wallet
    })

# -BACK ------------------------------------------------
# FOR CALLING
# --------------------------------------------------


@app.route('/blockchain/overide')
def overideBlockchain():
    status = dns.blockchain.overrideTheLongestChain()
    if status == 200:
        message = 'Overiding and getting chain successfully'
    elif status == 500:
        message = 'Don\'t have genesis block in chain'
    else:
        message = 'Something go wrong with getting blocks in database'
    chain = dns.blockchain.dumpChain()

    return jsonify({
        'status': status,
        'message': message,
        'chain':
        {
            'len': len(chain),
            'blocks': chain,
        }
    })

@app.route('/blockchain/hash_list')
def getHashList():
    return { "hash" : dns.blockchain.block_transactions_hash }

@app.route('/blockchain/add_block')
def addNewBlock():
    block, status = dns.blockchain.addBlock()
    message = 'Adding block successfully' if status == 200 else 'Something goes wrong with adding progress'
    return jsonify({
        'status': status,
        'message': message,
        'block': block,
    })


@app.route('/blockchain/mine')
def mineBlock():
    # Pre mining
    transactions, status = dns.blockchain.prepareMiningBlockTransactions()
    if status == 500:
        return Message.getMessage('BlockMining', status, dns.blockchain.BUFFER_MAX_LEN)

    # Mining
    block = dns.blockchain.mineBlock(transactions)

    if block:
        block, status = dns.blockchain.addBlock(block)
        dns.blockchain.transactions.setCurrentTxsBlockID(block.id)
        dns.blockchain.broadcastNewBlock()
        
    message = Message.getMessage('BlockMining', status or 501)

    return jsonify({
        'status': status,
        'message': message,
        'block_id': block.id if block else None
    })


@app.route('/blockchain/pow', methods=["POST"])
def proofOfWork():
    request_form_dict = request.form.to_dict(flat=False)
    block, speedtime = dns.blockchain.returnProofOfWorkOutput(
        request_form_dict)
    
    return jsonify({
        'status': 200,
        'message': 'Processing proof of work successfully',
        'hash': block._hash(),
        'block': block.as_dict(),
        'speedtime': speedtime,
    })


# Run --------------------------------------------------
if __name__ == "__main__":
    from argparse import ArgumentParser
    import socket
    import atexit
    import getpass

    def onClosingNode():
        try:
            node = dns.blockchain.nodes.getNode()
            if node:
                dns.blockchain.nodes.inActiveNode(node)
                print(
                    f"\n-------- NODE {node.id[:-20] + '..xxx'} IS INACTIVE ------")
                dns.blockchain.nodes.setNode(None)
        finally:
            print("\n-------- GOODBYE !! ------")

    def createNodeAdminCLI(node):
        # Ask question about fullname, generate email, password, retype password
        format = ACCOUNT_FORMAT

        print('\n_________ CREATE NODE ADMIN CLI ___________ \n')

        print('ADMIN INFORMATION ( fullname, password ) : ')
        # Fullname
        fullname = input(
            "1) Fullname ( ex: Phan Dai ) or [Enter] :") or 'Phan Dai'
        print()

        # Email
        while(True):
            email_fullname = "_".join(re.split('\W+', fullname.lower()))
            email = input("2) Email ( ex: <full_name>@<node>.<any> ) or [Enter] :") or email_fullname + '@' + "".join(
                re.split('\W+', node.nodename.lower())) + '.dnschain'
            print('Checking email ', email, '..')
            if re.match(format['email'], email):
                if not accountBusiness.getAccountByEmail(email):
                    print('-> Final email : ', email)
                    break
                else:
                    print(" This email is exsited ")
            else:
                print(' This email has wrong format')
        print()

        # Password and Repassword
        while(True):
            password = getpass.getpass(
                "2) Password ( auto hide, required 8+ chars, 1 special, 1 lower, 1 upper ) :")
            repassword = getpass.getpass("RePassword :")
            if re.match(format['password'], password):
                if password == repassword:
                    break
                else:
                    print('Password and repassword not the same')
            else:
                print('Wrong password format')

        # Type_cd
        type_cd = ADMIN_CD

        admin, status = accountBusiness.newAccount(
            fullname, email, password, repassword, type_cd)

        if status != 200:
            print("Sorry please try again with different properties' values")
            print("____ FAIL TO CREATE ADMIN  ", admin.email, "______\n")
            return admin, status

        print("____ CREATE ADMIN SUCCESSFULLY ", admin.email, "______\n")
        accountBusiness.addAccount(admin)
        return admin, status

    atexit.register(onClosingNode)

    # INIT CMD PARAM-------------------------------
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', type=str,
                        help='Any IPv4 string in your network or your local IP in default ')
    parser.add_argument('-n', '--name', nargs="?", const='', type=str,
                        help='Custom node name or auto node name')
    parser.add_argument('-p', '--port', nargs="?", const=5000, type=int,
                        help='Port number must be from 5000 - 5999 to access or 5000 in default')
    parser.add_argument('-gp', '--genport', action="store_true",
                        help='Generating random port flag, True : port will be random')
    args = parser.parse_args()

    generatePort = args.genport

    # GET CMD PARAM -------------------------------
    host = args.host or socket.gethostbyname(socket.gethostname())
    name = args.name or None
    port = args.port if generatePort == False else NodesBusiness.getRandomPort()
    genport_flag = args.genport

    # SET NODE -------------------------------
    node, code = dns.blockchain.nodes.handleNodeInformation(
        host, port, genport_flag, name)

    print('___________ BLOCKCHAIN DNS CLI ______________ \n')
    print("Config Node Information : ")
    print(f" 1) [Host] : [{node.ip or '_'}]")
    print(f" 2) [Port] : [{node.port or '_'}] \n")
    print("Data is processing please wait ... \n")

    # RETURN CODE MESSAGE -------------------------------
    # - NEW NODE -------------------------------
    if code == 200:
        print('//----------------------------------------//')
        print('  WELCOME NODE ', node.id[:-25] + '..xxx')
        print('//----------------------------------------//')
        try:
            admin, status = createNodeAdminCLI(node)
            if status != 200:
                exit(0)
            status = dns.initBlockchain(node, admin)
            if status != 200:
                print('!!: REPORT CHANGE IN DATA CAUSE SHUT DOWN !!')
                exit(0)
            app.run(host=node.ip, port=node.port,
                    debug=True, use_reloader=False)
        except:
            print('\n !!: Program is suddenly paused -> Turning off...')
            onClosingNode()
    # - REGISTED NODE -------------------------------
    elif code == 201:

        print('//----------------------------------------//')
        print('  WELCOME BACK NODE ', node.id[:-20] + '..xxx')
        print('//----------------------------------------//')
        try:
            if not node.account_id:
                admin, status = createNodeAdminCLI(node)
                if status != 200:
                    exit(0)
            else:
                print(" Admin: ", node.admin.email, "\n")
            status = dns.initBlockchain(node)
            if status != 200:
                print('!!: REPORT CHANGE IN DATA CAUSE SHUT DOWN !!')
                exit(0)
            app.run(host=node.ip, port=node.port,
                    debug=True, use_reloader=False)
        except:
            print(' Program is suddenly paused ! Turning off... ')
            onClosingNode()
    # - NOT FOUND NODE -------------------------------
    else:
        print(
            f"Return code #{code}: WRONG INFORMATION OR THIS NODE IS RUNNING AND NO NODES LEFT \n")
        print("Please try again with 2 options bellow :")
        print("1. Append '-p' option to access program \n")
        print(
            "2. -p <port> ( port : must be from [ 5000, 5999 ] ) or -gp to generate random port ")
        print("   -h <host> ( host : must be same as IPv4 format )")
