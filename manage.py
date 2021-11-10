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
  # TODO: Làm Proof of work chạy trên mọi node bằng Thread -> rồi xét thời gian nhỏ nhất             1/2 OK    
  # TODO: Làm xử lý chia transaction khi add Block 
        Số transactions 
        # 1 : Nhỏ hơn LEN -> Không đủ nên không làm 
        # 2 : Bằng LEN    -> Làm và gắn reward cho ai nhanh nhất 
        # 3 : Lớn hơn LEN -> Cắt ra và giữ lại phần dư
            Số transactions dư :
            # 1 : Nhỏ hơn LEN -> Không đủ nên không làm 
            # 2 : Bằng LEN    -> Đợi thời gian 10p 
            # 3 : Lớn hơn LEN -> Đợi thời gian 10p
            
  # TODO: Xử lý lấy wallet và ledger ở Blockchain  
  # TODO: Tạo form style để chụp hình vào Word
'''
# Declare -------------------------------------------------
dns = DNSResolver()

# FRONT --------------------------------------------------
@app.route('/')
def index():
    return redirect('/dns/form')

@app.route('/dns/form', methods=['POST','GET'])
def form():
    ALLOWED_EXTS  = {"txt"}
    
    def checkFileExtension( file ):
        return '.' in file and len(file.rsplit('.')) == 2 and file.rsplit('.',1)[1].lower() in ALLOWED_EXTS 
    
    def checkFileNameFormat( filename ):
        # Check file name 
        if filename == '':
            return render_template('index.html', error_message= MESSAGE['FileError02']), 404
        
        # Check file extension 
        if checkFileExtension(filename) == False:
            return render_template('index.html', error_message= MESSAGE['FileError03']), 404
        
        # Format that filename can store any where 
        filename = secure_filename(filename)    
        return filename, 200
    
    def handleOneRecordForm(form): 
        dns.blockchain.addTransaction( form )
        return 200

    def handleMultipleRecordsForm(file): 
        filename, status = checkFileNameFormat(file.filename)
        if status != 200:
            return status

        # Check uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        #Open file and add the content to TRANSACTION
        with open(file_path, "r", encoding="utf-8") as f :
            for line in f:
                if line != '' and line != '\n' and line != '\r' and not any(c in SPECIAL_CHARS for c in line):
                    dns.blockchain.addTransaction( line )
            return 200

    # 2. Insert record từ form ( một hoặc nhiều ), xử lý cho ra dữ liệu khi nhận route 
    if request.method == 'POST':
        status = 0
        if 'file' not in request.files:
            status = handleOneRecordForm(request.form)
        else :
            status = handleMultipleRecordsForm(request.files['file'])
        
        if status == 200: 
            return redirect('/blockchain/transactions')
        else :
            return 'Status code '
    
    return render_template('index.html', domainFormat = RECORD_FORMAT['domain'], ipFormat = RECORD_FORMAT['ip'])

@app.route('/blockchain/show')
def showBlockchain():
    return dns.blockchain.showChainDict()

@app.route('/blockchain/transactions')
def showTransactionsBuffer():
    tranList = dns.blockchain.current_transaction
    return jsonify({ 
        'len' : len(tranList),
        'trans' : tranList,
    })

@app.route('/blockchain/transactions/clear')
def clearTransactionsBuffer():
    dns.blockchain.transactions.clearTransaction()
    tranList = dns.blockchain.current_transaction
    return jsonify({ 
        'len' : len(tranList),
        'trans' : tranList,
    })

# BACK ------------------------------------------------
@app.route('/dns/resolve', methods=['GET', 'POST'])
def resolve():
    # 1. Tạo route để phân giải
    if request.method == 'POST':
        domain = request.form['domain']
        for tran in Transaction.TRANSACTIONS:
            if 'domain' in tran and tran['domain'] == domain: 
                return tran
    return "Hi"

@app.route('/blockchain/overide')
def overideBlockchain():
    return dns.blockchain.overrideTheLongestChain()

@app.route('/blockchain/add_block')
def addNewBlock():
    block, status = dns.blockchain.addBlock()
    return jsonify({
        'status': status,
        'block' : block,
    })
@app.route('/blockchain/launchpow')
def broadcastPOW():
    responses = dns.blockchain.launchProofOfWork()
    print( 'Response: ',responses )
    return jsonify({
        'len' : len(responses),
        'responses': responses
    })
    
@app.route('/blockchain/pow', methods=["POST"])
def proofOfWork():
    # TODO: 
    # Take block from request param 
    
    block_request = request.form.to_dict(flat=True)
    print( 'Reiceive: ',block_request )
    
    # Convert that block into table Model
    block = dns.blockchain.convertBlockFromBlockRequest(block_request)
    # Return block and exec_time 
    # response = dns.blockchain.proofOfWork(block)
    return block_request
    '''
    {
        'node_id': 1,
        'nonce': 0,
        'hash': '',
        'time': time.perf_counter(),    
    }
    '''
       
    
# Run --------------------------------------------------
if __name__ == "__main__":
    from argparse import ArgumentParser
    import socket
    import atexit
    
    def onClosingNode():
        try :
            node = dns.blockchain.nodes.getNode()
            if node:
                dns.blockchain.nodes.inActiveNode(node)
                print (f"\n-------- NODE {node.id[:-20] + '..xxx'} IS INACTIVE ------")
                dns.blockchain.nodes.setNode(None)
        finally:
                print ("\n-------- GOODBYE !! ------")
    
    atexit.register(onClosingNode)
    # INIT CMD PARAM------------------------------- 
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', type=str, help='Any IPv4 string in your network or your local IP in default ')
    parser.add_argument('-p', '--port', nargs="?", const= 5000 , type=int, help='Port number must be from 5000 - 5999 to access or 5000 in default')
    parser.add_argument('-gp', '--genport', action="store_true", help='Generating random port flag, True : port will be random')
    args = parser.parse_args()
    
    generatePort = args.genport

    # GET CMD PARAM ------------------------------- 
    port = args.port if generatePort == False else NodesBusiness.getRandomPort()
    host = args.host or socket.gethostbyname(socket.gethostname())
    
    # SET NODE ------------------------------- 
    node, code = dns.blockchain.nodes.handleNodeInformation(host, port)
    print('___________ BLOCKCHAIN DNS CLI ______________ \n')
    print("Config Node Information : " )
    print(f" 1) [Host] : [{node.ip or '_'}]" )
    print(f" 2) [Port] : [{node.port or '_'}] \n" )
    print('Data is processing please wait ... \n')

    # RETURN CODE MESSAGE ------------------------------- 
    if code == 200 : 
        print( '//----------------------------------------//' )
        print( '  WELCOME NODE ', node.id[:-25] + '..xxx' )
        print( '//----------------------------------------//' )
        try :
            dns.initBlockchain( node )
            app.run(host=node.ip, port = node.port,  debug=True, use_reloader=False)
        except:
            print('\n !!: Program is suddenly paused -> Turning off...') 
    elif code == 201 :
        print( '//----------------------------------------//' )
        print( '  WELCOME BACK NODE ', node.id[:-20] + '..xxx' )
        print( '//----------------------------------------//' )
        try :
            dns.initBlockchain( node )
            app.run(host=node.ip, port = node.port,  debug=True, use_reloader=False)
        except:
            print(' Program is suddenly paused ! Turning off... ') 
    else :
        print( f"Return code #{code}: WRONG INFORMATION OR NOT FOUND ARGUMENT \n")
        print( "Please try again with 2 options bellow :" )
        print( "1. Append '-p' option to access program \n")
        print( "2. -p (port) must be from [ 5000, 5999 ]")
        print( "   -h (host) must be same as IPv4 format" )