from include import *
from business import *

'''
  Run file 
  TODO: Làm Blockchain ở file business DOING 
        * Làm add 2/2 OK
        * Làm resolve conflict OK
        * Show chain OK 
        * Test bằng route 
            # 1. Turn 2 nodes on OK
            # 2. Back route: new block OK
            # 3. Show chain all node OK
        * 
  TODO: Check duplicate Transaction khi thêm từ file, ghép xử lý add Block khi POST vào 
  TODO: Xử lý lấy wallet và ledger ở Blockchain  
  TODO: Tạo form style để chụp hình vào Word
  TODO: Làm Proof of work chạy trên mọi node bằng Thread -> rồi xét thời gian nhỏ nhất   
'''
# Declare -------------------------------------------------
dns = DNSResolver()
def check_file_extension( file ):
    return '.' in file and len(file.rsplit('.')) == 2 and file.rsplit('.',1)[1].lower() in ALLOWED_EXTS 


# FRONT --------------------------------------------------
@app.route('/')
def index():
    return 'hi'

@app.route('/dns/form', methods=['POST','GET'])
def form():
    def checkFileNameFormat( filename ):
        # Check file name 
        if filename == '':
            return render_template('index.html', error_message= MESSAGE['FileError02']), 404
        # Check file extension 
        if check_file_extension(filename) == False:
            return render_template('index.html', error_message= MESSAGE['FileError03']), 404
        # Format that filename can store any where 
        filename = secure_filename(filename)    
        return filename, 200

    def checkRecordFormat( str: str ):
        checked = copy(RECORD_FORMAT)
        str = str.strip()
        # Check if str don't start with special chars
        if str[0].isalpha() or str[0].isnumeric(): 
            if not any(c in SPECIAL_CHARS for c in str): 
                props = str.split()
                checked['domain'] = True if re.match(RECORD_FORMAT['domain'],props[0]) else False
                checked['type'] = True if re.match(RECORD_FORMAT['type'],props[1]) else False
                checked['ip'] = True if re.match(RECORD_FORMAT['ip'],props[2]) else False
                checked['port'] = True if re.match(RECORD_FORMAT['port'],props[3]) else False
                checked['ttl'] = True if re.match(RECORD_FORMAT['ttl'],props[4]) else False

            if checked['domain'] == True and checked['type'] == True and checked['ip'] == True and checked['port'] == True and checked['ttl'] == True : 
                return True

        return False

    def convertRecords( str: str ):
        props = str.split()
        return {
            'domain' : props[0],
            'type' : props[1],
            'ip' : props[2],
            'port': int(props[3]),
            'ttl': int(props[3])
        }
    
    def handleOneRecordForm(form): 
        Transaction.TRANSACTIONS.append(form)
        return 200

    def handleMultipleRecordsForm(file): 
        filename, status = checkFileNameFormat(file.filename)
        if status != 200:
            return checkFileNameFormat(file.filename)

        # Check uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        #Open file and add the content to TRANSACTION
        with open(file_path, "r", encoding="utf-8") as f :
            for line in f:
                if checkRecordFormat(line) == True : 
                   Transaction.TRANSACTIONS.append(convertRecords(line))
            return 200

    # 2. Insert record từ form ( một hoặc nhiều ), xử lý cho ra dữ liệu khi nhận route 
    if request.method == 'POST':
        if 'file' not in request.files:
            # Xử lý một record
            handleOneRecordForm(request.form)
        else :
            # Xử lý nhiều records
            handleMultipleRecordsForm(request.files['file'])
        # print(Transaction.TRANSACTIONS)
        # Transaction.TRANSACTIONS = list(set(Transaction.TRANSACTIONS))
        return jsonify(Transaction.TRANSACTIONS) 
    # 1. Tạo simple form 
    return render_template('index.html', domainFormat = RECORD_FORMAT['domain'], ipFormat = RECORD_FORMAT['ip'])

@app.route('/blockchain/show')
def showBlockchain():
    return dns.blockchain.showChainDict()

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

@app.route('/blockchain/solving_conflict')
def solvingConflict():
    return dns.blockchain.overrideTheLongestChain()

@app.route('/blockchain/add_block')
def addNewBlock():
    dns.blockchain.current_transactions = ['1','1','2','2']
    block, status = dns.blockchain.addBlock()
    return jsonify({'status': status})

# Run --------------------------------------------------
if __name__ == "__main__":
    from argparse import ArgumentParser
    import socket
    import atexit
    
    print( 'Data is processing please wait ... ')
    def onClosingNode():
        node = dns.blockchain.nodes.getNode()
        if node:
            dns.blockchain.nodes.inActiveNode(node)
            print (f"\n-------- NODE {node.id} IS INACTIVE ------")
            print ("-------- GOODBYE !! ------")
    
    atexit.register(onClosingNode)
    # INIT CMD PARAM------------------------------- 
    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default='', type=str, help='IPv4 string in your network or blank in default')
    parser.add_argument('-p', '--port', default=5000, type=int, help='Port Number to listen on or auto-handle in default')
    args = parser.parse_args()
    # GET CMD PARAM ------------------------------- 
    port = args.port 
    host = args.host or socket.gethostbyname(socket.gethostname())
    
    # SET NODE ------------------------------- 
    node, code = dns.blockchain.nodes.handleNodeInformation(host, port)
    dns.initBlockchain( node )
    # RETURN CODE MESSAGE ------------------------------- 
    if code == 200 : 
        print( '//----------------------------------------//' )
        print( ' WELCOME NODE ', node.id )
        print( '//----------------------------------------//' )
        app.run(host=node.ip, port = node.port,  debug=True, use_reloader=False)
    elif code == 201 :
        print( '//----------------------------------------//' )
        print( ' WELCOME BACK NODE ', node.id )
        print( '//----------------------------------------//' )
        app.run(host=node.ip, port = node.port,  debug=True, use_reloader=False)
    else :
        print( 'WRONG INFORMATION !! PLEASE TRY AGAIN WITH OTHER VALID HOSTNAME OR PORT' )
        print( 'Port must be from [ 5000, 5999] ' )
        print( 'Hostname must have right format of IPv4 ' )