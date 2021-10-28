from .blockchain import Blockchain as bc
import requests

"""
Define the format of DNS transaction here
dns_transaction = {
	'hostname':hostname,
	'ip':ip,
	'port':port
}
"""

# ** 
# * Class dns_layer 
# * là trung gian giao tiếp giữa request và blockchain
# **  
class dns_layer(object):
	# Constructor với node_identifier là 1 dạng của id
	def __init__(self, node_identifier):
		"""
		Initialize a blockchain object
		BUFFER_MAX_LEN is the number of entries per block
		--------------------------------
		Tạo ra một blockchain object 
		BUFFER_MAX_LEN là số entries có thể chứa ở mỗi block
		Mỗi node sẽ nhận được phần thưởng MINE_REWARD sau mỗi lần thêm block thành công
		"""
		self.blockchain = bc(node_identifier)
		self.BUFFER_MAX_LEN = 20
		self.MINE_REWARD = 10
		self.node_identifier = node_identifier 

	# Hàm tìm kiếm dns dựa vào input hostname
	def lookup(self,hostname):
		"""
		Goes through all the blocks in the chain to look
		for a matching transaction.
		---------------------------
		Duyệt tất cả các blocks trong chain 
		để tìm ra transaction phù hợp 

		:param hostname: string, target hostname we are looking for
		:return: a tuple (ip,port)
		"""
		for block in self.blockchain.chain:
			transactions = block['transactions']
			# Duyệt tât cả transaction bên trong mảng transactions :
			# Một Block có thể có nhiều transactions
			for transaction in transactions:
				# print(transaction)
				if 'hostname' in transaction and transaction['hostname'] == hostname:
					return (transaction['ip'],transaction['port'])
		# TODO: Tìm hiểu Raise error 
		raise LookupError('No existing entry matching hostname')

    # Hàm đào
	def mine_block(self):
		"""
		here we assume only the node will full buffer will mine
		once finish mining, broadcast resolve to every node
		all other node add new block but keep buffer
		-------------------------------------------
		Ở đây, ta cho rằng các node sẽ toàn lực "đào" đến khi nào hoàn thành việc đào đó,
		Chuyển kết quả cho các node khác 
		Các node sẽ gắn block mới vào nhưng vẫn giữ buffer
		
		"""
		last_block = self.blockchain.last_block
		# TODO : proof này giữ gì ? -> Proof như là 1 số Nonce của Block trước 
		last_proof = last_block['proof']
		proof = self.blockchain.proof_of_work(last_proof)

		# Forge the new Block by adding it to the chain
		# Rèn block mới bằng cách thêm vào chuỗi 
		previous_hash = self.blockchain.hash(last_block)
		block = self.blockchain.new_block(proof, previous_hash)

		# broadcast request for all neighbor to resolve conflict
		# Phát động request cho tất cả các node để xử lí thay đổi
		self.broadcast_new_block()

		# now add a special transaction that signifies the reward mechanism
		# Giờ thêm transaction 
		new_transaction = {
			'node':self.node_identifier,
			'block_index':block['index'],
			'reward':self.MINE_REWARD
		}

		# ! Vậy là block khác với transaction khi được thêm vào BC ?
		self.blockchain.new_transaction(new_transaction)
		return proof

	# Hàm phát động kết quả block mới sau khi POW thành công
	def broadcast_new_block(self):
		"""
		Broadcast resolve request to all neighbor to force neighbors
		update their chain
		"""
		# Tìm hết tất cả nodes của Blockchain
		neighbors = self.blockchain.nodes

		for node in neighbors:
			print(f"Requesting {node} to resolve")
			response = requests.get(f'http://{node}/nodes/resolve')
			# if response.status_code != 200:
			# 	raise ValueError(f'Node {node} responded bad status code')
			# print(f"{node} resolve completed")

		print("Broadcast Complete")

	# Hàm tạo mới cho blockchain
	def new_entry(self,hostname,ip,port):
		"""
		Adds new entry into current transactions in the blockchain.
		Once we reach a full buffer, mine new block.

		
		:param hostname: string, hostname
		:param ip: string, ip of corresponding hostname
		:param port: int, port of corresponding ip
		""" 
		new_transaction = {
			'hostname':hostname,
			'ip':ip,
			'port':port
		}

		# TODO : quota là cái gì ? buffer_len để chi ? Tại sao có điều kiện dưới ?
		# -> quota là số tiền node kiếm được nhờ mining . buffer_len dùng để kiểm tra đủ transaction trong một block chưa để mining 
		buffer_len = self.blockchain.new_transaction(new_transaction)
		if buffer_len >= self.BUFFER_MAX_LEN or buffer_len >= self.blockchain.quota-self.BUFFER_MAX_LEN:
			self.mine_block()
	
	# Hàm get BChain & độ dài của BChain
	def dump_chain(self):
		response = {
		'chain': self.blockchain.chain,
		'length': len(self.blockchain.chain)
		}
		return response

	# Hàm get transaction hiện tại 
	def dump_buffer(self):
		return self.blockchain.current_transactions

	# Hàm get quota ?
	def get_chain_quota(self):
		return self.blockchain.quota

	# Hàm đăng kí node
	def register_node(self,addr):
		self.blockchain.register_node(addr)

	# Hàm lấy số lượng các node trong network
	def get_network_size(self):
		return len(self.blockchain.nodes)





