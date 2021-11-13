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
  # TODO: Tạo form style để chụp hình vào Word  - UI                                                     P  
        Làm 3 trang : 
            1. Node manager  : Quản lý node 
            2. Block manager : Quản lý block và tình trạng blockchain 
            3. Transaction Viewer : Xem các transaction đã tồn tại trong block hoặc transaction nằm trong buffer 
               / Transaction Maker: Thêm transaction bằng input hoặc nhận file

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

# BACK ------------------------------------------------
@app.route('/blockchain/transactions')
def showTransactionsBuffer():
    tranList = dns.blockchain.current_transaction
    return jsonify({
        'status'  : 200,
        'message' : 'Show transaction successfully', 
        'len'     : len(tranList),
        'trans'   : tranList,
    })

@app.route('/blockchain/transactions/clear')
def clearTransactionsBuffer():
    dns.blockchain.transactions.clearTransaction()
    tranList = dns.blockchain.current_transaction
    return jsonify({ 
        'status'  : 200,
        'message' : 'Clearing transaction successfully',
        'len'     : len(tranList),
        'trans'   : tranList,
    })

@app.route('/blockchain/dump')
def dumpChain():
    chain = dns.blockchain.dumpChain()
    
    return jsonify({
        'status'   : 200,
        'message'  : 'Getting chain successfully',
        'chain'    : 
        {
            'len'    : len(chain),
            'blocks' : chain,
        }
    })

@app.route('/dns/resolve', methods=['GET', 'POST'])
def resolve():
    # 1. Tạo route để phân giải
    if request.method == 'POST':
        tran, status = dns.lookup(request.form)
        message = 'Resolving successfully with inputed domain' if status == 200 else 'Not found record with inputed domain'
        return jsonify({
            'status' : status,
            'method' : 'POST',
            'message': message,
            'record' : tran,
        })
        
    return jsonify({
        'status' : 200,
        'method' : 'GET',
        'message': 'Resolver webpage'
    })

@app.route('/blockchain/overide')
def overideBlockchain():
    status  = dns.blockchain.overrideTheLongestChain()
    if status == 200: 
        message = 'Overiding and getting chain successfully'
    elif status == 500:
        message = 'Don\'t have genesis block in chain'
    else : 
        message = 'Something go wrong with getting blocks in database'
    chain   = dns.blockchain.dumpChain()
    
    return jsonify({
        'status'   : status,
        'message'  : message,
        'chain'    : 
        {
            'len'    : len(chain),
            'blocks' : chain,
        }
    })

@app.route('/blockchain/add_block')
def addNewBlock():
    block, status = dns.blockchain.addBlock()
    message = 'Adding block successfully' if status == 200 else 'Something goes wrong with adding progress'
    return jsonify({
        'status' : status,
        'message': message,
        'block'  : block,
    })

@app.route('/blockchain/mine')
def mineBlock():
    block, status = dns.blockchain.mineBlock()
    if status == 200 :
        # 1. here . Don't work 
        block, status = dns.blockchain.addBlock(block)
        dns.blockchain.broadcastNewBlock()
        # 2. here . Don't work 
    elif status == 500 :
        message = f'Don\'t have enough {dns.blockchain.BUFFER_MAX_LEN} transactions to start mining'
    
    if status == 200 :
        message = 'Mine block successfully'
    else :
        message = 'Something goes wrong with adding progress in mining' 
    
    return jsonify({
        'status'  : status,
        'message' : message,
        'block_id': block.id if block else None
    })
    
@app.route('/blockchain/pow', methods=["POST"])
def proofOfWork():
    block_request = request.form.to_dict(flat=True)
    block, speedtime = dns.blockchain.returnProofOfWorkOutput(block_request)
    
    return jsonify({
        'status'   : 200,
        'message'  : 'Processing proof of work successfully',
        'hash'     : block.hash(),
        'block'    : block.as_dict(),
        'speedtime': speedtime,    
    })

@app.route('/blockchain/ledger')
def getLedger():
    ledger = dns.blockchain.ledger
    message = 'Getting ledger successfully'
    return jsonify({
        'status'  : 200,
        'message' : message,
        'len'     : len(ledger),
        'ledger'  : ledger
    })

@app.route('/blockchain/wallet')
def getWallet():
    wallet = dns.blockchain.wallet
    message = 'Getting wallet successfully'
    return jsonify({
        'status'  : 200,
        'message' : message,
        'wallet'  : wallet
    })

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