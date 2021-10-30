# --------- #2. API ROUTERS --------------------------------------
# Make a DNS layer as resolver - as communicator between Server and Blockchain
# Route 1: Make sure this node is working - Need when init  
@app.route('/debug/alive',methods=['GET'])
def check_alive():
	response = 'The node is alive'
	return  jsonify(response),200

# Route 2: Registry a node (Machine) to network - Need when init
@app.route('/nodes/new',methods=['POST'])
def register_node():
	"""
	Calls underlying functions to register new node in network
	"""
	values = request.get_json()
	nodes = values.get('nodes')

	if nodes is None:
		# Nếu không có giá trị gì gửi lên sẽ trả STATUS CODE 400 
		response, return_code = "No node supplied",400
	else:
		for node in nodes:
			# DNS resolver tạo node mới 
			dns_resolver.register_node(node)
		
		# Nếu thêm thành công sẽ trả STATUS CODE 201 và message 	
		response, return_code = {
			'message': 'New nodes have been added',
			'total_nodes': dns_resolver.get_network_size(),
		}, 201

	return jsonify(response),return_code

# Route 3: Add more new DNS - insert code when request POST in /storage 
@app.route('/dns/new',methods=['POST'])
def new_transaction():
	"""
	adds new entries into our resolver instance
	"""
	values = request.get_json()
	# print(values)
	required = ['hostname', 'ip', 'port']
	bad_entries = []

	for value in values:
		#print(k in values[value] for k in required)
		if all(k in values[value] for k in required):
			value = values[value]
			# Nếu các key của giá trị request trùng với các key của required thì sẽ được tạo mới
			dns_resolver.new_entry(value['hostname'],value['ip'],value['port'])
		else:
			bad_entries.append(value)

	if bad_entries:
		return jsonify(bad_entries),400
	else:
		response = 'New DNS entry added'
		return jsonify(response), 201

# Route 4: Sending request to resolver and receive response with data - need to change the table
@app.route('/dns/request',methods=['POST'])
def dns_lookup():
	"""
	receives a dns request and responses after resolving
	"""
	values = request.get_json()
	required = ['hostname']
	if not all(k in values for k in required):
		return 'Missing values', 400

	try:
		# Gửi giá trị của thuộc tính hostname cho DNS resolver để tìm kiếm
		host, port = dns_resolver.lookup(values['hostname'])
		response = {
			'ip':host,
			'port': port
		}
		return_code = 200
	except LookupError:
		response = "No existing entry"
		return_code = 401
	
	# Tìm thấy thì 200 , không thì 401 
	return jsonify(response), return_code

# Route 5: Solving node's conflict from change
@app.route('/nodes/resolve',methods=['GET'])
def consensus():
	"""
	triggers the blockchain to check chain against other neighbors'
	chain, and uses the longest chain to achieve consensus ( đoàn kết )
	"""
	t = threading.Thread(target=dns_resolver.blockchain.resolve_conflicts)
	t.start()

	return jsonify(None), 200