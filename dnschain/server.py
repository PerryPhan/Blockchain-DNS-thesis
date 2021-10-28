from flask import Flask, jsonify, request # Ok
import json # Ok
import dns # Ok
from uuid import uuid4 # Ok
import threading # Ok

"""
This layer takes care of DNS request and reponse packets
Additionally support packets adding new entries, which should require
authentication. Other routes implement methods required to maintain
integrity and consistency of the blockchain.
"""

# Khởi tạo node app Flask 
app = Flask(__name__) # Ok

# Tạo một địa chỉ globally duy nhất cho node này 
node_identifier = str(uuid4()).replace('-', '') #Ok

# Khởi tạo the DNS resolver object
dns_resolver = dns.dns_layer(node_identifier = node_identifier) #Ok 

# Node : Node App còn hoạt động hay không ? Ok
@app.route('/debug/alive',methods=['GET'])
def check_alive():
	response = 'The node is alive'
	return  jsonify(response),200

# Node : Tạo mới các node trong mạng network Ok 
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

# DNS : Tạo DNS mới 
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

# DNS : Gửi request và nhận response từ DNS Resolver
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

# Node : Kiểm tra các node có đồng bộ hay chưa ?
@app.route('/nodes/resolve',methods=['GET'])
def consensus():
	"""
	triggers the blockchain to check chain against other neighbors'
	chain, and uses the longest chain to achieve consensus ( đoàn kết )
	"""
	t = threading.Thread(target=dns_resolver.blockchain.resolve_conflicts)
	t.start()

	# if replaced:
	# 	response = {
	# 		'message': 'Our chain was replaced',
	# 		'new_chain': dns_resolver.dump_chain()
	# 	}
	# else:
	# 	response = {
	# 		'message': 'Our chain is authoritative',
	# 		'chain': dns_resolver.dump_chain()
	# 	}

	return jsonify(None), 200

# TEST
# TODO : Cần vào sâu các function con để hiểu 
# 1:  
@app.route('/debug/dump_chain',methods=['GET'])
@app.route('/nodes/chain',methods=['GET'])
def dump_chain():
	response = dns_resolver.dump_chain()
	return jsonify(response), 200

# 2:
@app.route('/debug/dump_buffer',methods=['GET'])
def dump_buffer():
	response = dns_resolver.dump_buffer()
	return jsonify(response), 200

# 3:
@app.route('/debug/force_block',methods=['GET'])
def force_block():
	response = dns_resolver.mine_block()
	return jsonify(f"New block mined with proof {response}"), 200

# 4:
@app.route('/debug/get_quota',methods=['GET'])
def get_chain_quota():
	response = dns_resolver.get_chain_quota()
	return jsonify(response),200

if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()
	# default port for DNS should be 53
	parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port

	app.run(host='0.0.0.0', port=port, debug=True)