from werkzeug.wrappers import response
from include import *
from business import *
'''
  Run file 
  # TODO: Làm Blockchain ở file business DOING 
        * Làm add 2/2                     OK
        * Làm resolve conflict            OK
        * Show chain                      OK 
        * Test bằng route 
            # 1. Turn 2 nodes on          OK
            # 2. Back route: new block    OK
            # 3. Show chain all node      OK
  # TODO: Check duplicate Transaction khi thêm nhiều từ file, ghép xử lý add transactions khi POST       OK
  # TODO: Làm Proof of work chạy trên mọi node bằng Thread -> rồi xét thời gian nhỏ nhất                 OK    
  # TODO: Xử lý lấy wallet và ledger ở Blockchain                                                        OK 
  # TODO: Làm xử lý chia transaction khi add Block                                                       OK
        Số transactions cho UI
        # 1 : Nhỏ hơn LEN -> Không đủ nên không làm 
        # 2 : Bằng LEN    -> Làm như bình thường 
        # 3 : Lớn hơn LEN -> Làm như bình thường và cắt giữ lại phần dư
            Số transactions dư : cho UI 
            # 1 : Nhỏ hơn LEN -> Không đủ nên không làm 
            # 2 : Bằng LEN    -> Đợi thời gian 10p 
            # 3 : Lớn hơn LEN -> Đợi thời gian 10p
  # TODO: Cleaning code và stress test                                                                   OK
'''
# Declare -------------------------------------------------
dns = DNSResolver()
accountBusiness = AccountBusiness()
transactionsBusiness = TransactionBusiness()
# FRONT --------------------------------------------------


@app.route('/')
def home():
    return redirect('/dashboard/transactions')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # How to know that is his first time => This onl IP was his computer and don't have this email in DB
    # If he try to log again will be email and password empty
    html_options = {
        'title': 'Admin',
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

    return render_template('_admin_template.html', **html_options)


@app.route('/dashboard/transactions')
def dashboardTransactions():
    list = dns.blockchain.transactions.getAllTransactions()
    noblocklist = dns.blockchain.transactions.getNoBlockTransactions()
    html_options = {
        'type' : 1,
        'title': 'Transaction Dashboard ',
        'count': len(list) if list else 0,
        'unit' : 'tx',
        'list' : list,
        'no_block_list_count': len(noblocklist),
        'node' : dns.blockchain.nodes.node,
    }
    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname']
            }
            return render_template('_dashboard_template.html', **html_options, **account_options)
    
    return render_template('_dashboard_template.html', **html_options)

@app.route('/dashboard/transactions/detail')
def detailDashboardTransactions():
    id = request.args.get('id', default = 1, type = int)
    
    html_options = {
        'type' : 1,
        'title': 'Transaction Detail',
        'unit' : 'tx',
    }
    
    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname']
            }
            return render_template('_detail_dashboard_template.html', **html_options, **account_options)
    
    return render_template('_detail_dashboard_template.html', **html_options)

@app.route('/dashboard/domains')
def dashboardDomains():
    list = dns.blockchain.transactions.getDomainList()
    
    html_options = {
        'type' : 2,
        'title': 'Domains Dashboard ',
        'count': len(list) if list else 0,
        'unit' : 'domains',
        'list' : list,
        'node_id' : dns.blockchain.node_id,
    }
    
    if session :
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname']
            }
            return render_template('_dashboard_template.html', **html_options, **account_options)
    
    return render_template('_dashboard_template.html', **html_options)

@app.route('/dashboard/domains/detail')
def detailDashboardDomains():
    domain = request.args.get('domain', default = '', type = str)
    
    html_options = {
        'type' : 2,
        'title': 'Domains Detail',
        'unit' : 'domains',
    }
    
    if session:
        if 'account' in session:
            account_options = {
                'account_id': session['account']['id'],
                'account_fullname': session['account']['fullname']
            }
            return render_template('_detail_dashboard_template.html', **html_options, **account_options)
    
    return render_template('_detail_dashboard_template.html', **html_options)

@app.route('/dashboard/operation', methods=['GET','POST'])
def dashboard_operation():
    ALLOWED_EXTS = {"txt"}
    
    def checkFileExtension(file):
        return '.' in file and len(file.rsplit('.')) == 2 and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

    def checkFileNameFormat(filename):
        # Check file name
        if filename == '':
            return render_template('_dnsform_template.html', error_message=MESSAGE['FileError02']), 404

        # Check file extension
        if checkFileExtension(filename) == False:
            return render_template('_dnsform_template.html', error_message=MESSAGE['FileError03']), 404

        # Format that filename can store any where
        filename = secure_filename(filename)
        return filename, 200

    def handleOneRecordForm(form):
        # New transaction
        tran, status = transactionsBusiness.newTransaction(
           form, session['account']['id'], 'add', True
        )
        # Add single Transaction 
        status = transactionsBusiness.addTransactionPool(tran)
        
        return tran, status
    
    def handleMultipleRecordsForm(file):
        filename, status = checkFileNameFormat(file.filename)
        if status != 200:
            return status

        # Check uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Open file and add the content to TRANSACTION
        with open(file_path, "r", encoding="utf-8") as f:
        #    Do like 1 form
            return 200
    
    # Check account 
    if not session or not 'account' in session :
        return redirect('/login')
        
    account_options = {
        'account_id': session['account']['id'],
        'account_fullname': session['account']['fullname'],
    }
    
    html_options = {
        'title': 'Operation',
        'type' : 3,
        **account_options,
    }
    
    if request.method == 'POST':
        status = 0
        if 'file' in request.files:
            status  = handleMultipleRecordsForm(request.files['file'])
            
            return {
            'status' : status, 
            'form'   : request.form,
            'file'  :  request.files['file'].filename
            }
        
        tran, status = handleOneRecordForm(request.form)
        return {
            'status' : status, 
            'transaction'   : tran.as_dict() if tran else None,
        }
            
    return render_template('_operation_template.html', **html_options)
    
@app.route('/block')
def block_manager():
    html_options = {
        'title': 'Block Manager ',
    }
    return render_template('_block_manager_template.html', **html_options)

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
        message = Message.getMessage('AccountLogin', str(status))
        if account:
            account = account.as_dict()
            # TODO : create safe as_dict function
            # account.pop('password', None):
            account['password'] = ''
            # account.pop('id', None):
            
            session['account'] = account

        response = {'status': status, 'message': message}
        # return render_template('_login_template.html', **html_options, **response)
        return redirect('/dashboard/transactions')

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
        message = Message.getMessage('AccountRegister', str(status))
        response = {'status': status, 'message': message}

        if status == 200:
            session['regis_email'] = email
        else:
            response['fullname'] = fullname
            response['email'] = email

        return render_template('_login_template.html', **html_options, **response)

    return render_template('_login_template.html', **html_options)



# BACK ------------------------------------------------

@app.route('/blockchain/transactions')
def showTransactionsBuffer():
    tranList = dns.blockchain.current_transactions
    return jsonify({
        'status': 200,
        'message': 'Show transaction successfully',
        'len': len(tranList),
        'trans': tranList,
    })


@app.route('/blockchain/transactions/clear')
def clearTransactionsBuffer():
    dns.blockchain.transactions.clearTransaction()
    tranList = dns.blockchain.current_transaction
    return jsonify({
        'status': 200,
        'message': 'Clearing transaction successfully',
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
    # block, status = dns.blockchain.mineBlock()
    # if status == 200:
    #     # 1. here . Don't work
    #     block, status = dns.blockchain.addBlock(block)
    #     dns.blockchain.broadcastNewBlock()
    #     # 2. here . Don't work
    # elif status == 500:
    #     message = f'Don\'t have enough {dns.blockchain.BUFFER_MAX_LEN} transactions to start mining'

    # if status == 200:
    #     message = 'Mine block successfully'
    # else:
    #     message = 'Something goes wrong with adding progress in mining'

    # return jsonify({
    #     'status': status,
    #     'message': message,
    #     'block_id': block.id if block else None
    # })
    return 'Step 1: Check condition -> Step 2: Mine '


@app.route('/blockchain/pow', methods=["POST"])
def proofOfWork():
    block_request = request.form.to_dict(flat=True)
    block, speedtime = dns.blockchain.returnProofOfWorkOutput(block_request)

    return jsonify({
        'status': 200,
        'message': 'Processing proof of work successfully',
        'hash': block.hash(),
        'block': block.as_dict(),
        'speedtime': speedtime,
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


# Run --------------------------------------------------
if __name__ == "__main__":
    from argparse import ArgumentParser
    import socket
    import atexit

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

    atexit.register(onClosingNode)
    # INIT CMD PARAM-------------------------------
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', type=str,
                        help='Any IPv4 string in your network or your local IP in default ')
    parser.add_argument('-p', '--port', nargs="?", const=5000, type=int,
                        help='Port number must be from 5000 - 5999 to access or 5000 in default')
    parser.add_argument('-gp', '--genport', action="store_true",
                        help='Generating random port flag, True : port will be random')
    args = parser.parse_args()

    generatePort = args.genport

    # GET CMD PARAM -------------------------------
    port = args.port if generatePort == False else NodesBusiness.getRandomPort()
    host = args.host or socket.gethostbyname(socket.gethostname())

    # SET NODE -------------------------------
    node, code = dns.blockchain.nodes.handleNodeInformation(host, port)
    print('___________ BLOCKCHAIN DNS CLI ______________ \n')
    print("Config Node Information : ")
    print(f" 1) [Host] : [{node.ip or '_'}]")
    print(f" 2) [Port] : [{node.port or '_'}] \n")
    print('Data is processing please wait ... \n')

    # RETURN CODE MESSAGE -------------------------------
    if code == 200:
        print('//----------------------------------------//')
        print('  WELCOME NODE ', node.id[:-25] + '..xxx')
        print('//----------------------------------------//')
        try:
            dns.initBlockchain(node)
            app.run(host=node.ip, port=node.port,
                    debug=True, use_reloader=False)
            
        except:
            print('\n !!: Program is suddenly paused -> Turning off...')
    elif code == 201:
        print('//----------------------------------------//')
        print('  WELCOME BACK NODE ', node.id[:-20] + '..xxx')
        print('//----------------------------------------//')
        try:
            dns.initBlockchain(node)
            app.run(host=node.ip, port=node.port,
                    debug=True, use_reloader=False)
        except:
            print(' Program is suddenly paused ! Turning off... ')
    else:
        print(
            f"Return code #{code}: WRONG INFORMATION OR NOT FOUND ARGUMENT \n")
        print("Please try again with 2 options bellow :")
        print("1. Append '-p' option to access program \n")
        print("2. -p <port> ( port : must be from [ 5000, 5999 ] )")
        print("   -h <host> ( host : must be same as IPv4 format )")
