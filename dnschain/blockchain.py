"""
Implementation referenced from https://github.com/dvf/blockchain
Modified to fit the DNS scenario
"""

import hashlib
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import json
import requests

# ** 
# * Class Blockchain 
# * 
# **  
class Blockchain(object):
	def __init__(self,node_identifier):
		"""
		Initializes the class:

		Current_transactions is the buffer for new transactions
		before a new block is created

		Chain is the chain of blocks (ledger) storing all data

		Nodes is a set keeping track of all the other nodes.
		This is required since we need to broadcast information to other nodes
		------------------------------------ 
		Khởi tạo class

		Current_transactions là một bộ nhớ đệm để lưu trữ các lần giao dịch 
		trước khi tạo một block

		Chain là chuỗi các block ( sổ cái ) lưu trữ tất cả data

		Nodes là một dãy các máy tính để tiện theo dõi 
		Quan trọng để phát động các thông tin đến máy khác. 
		"""
		self.current_transactions = []
		self.chain = []
		self.nodes = set()
		self.node_identifier = node_identifier

		# create the genesis block
		# this is a hardcoded block which serves as the first block
		# it contains no data
		
		# -----------------------
		# Tạo block chung
		# đóng vai trò như block khởi tạo, đầu của chuỗi
		# không chứa dữ liệu

		self.new_block(previous_hash = '1', proof=100)

	# Hàm tạo node, nodes độc lập với nhau
	def register_node(self, address):
		"""
		Add a new node to the list of nodes

		:param address: Address of new node in network.
		"""
		# print(address)
		# parsed_url = urlparse(address)
		# self.nodes.add(parsed_url.netloc)
		self.nodes.add(address)
		# print(self.nodes)

	# Ép kiểu thành thuộc tính
	@property
	# Tính toán tổng reward qua những transaction
	def quota(self):
		"""
		Go through the chain and calculate the quota (publish cash) we have
		Cash is recorded with a special type of transaction
		--------------------------
		Duyệt các reward từ transaction của block['source'] == self.node_identifier
		Cash được biết như là loại đặc biệt của transaction
		"""
		chain = self.chain
		quota = 10 # Điểm khởi đầu là 10 cash 

		for block in chain:
			own_block = (block['source']==self.node_identifier)
			for transaction in block['transactions']:
				if 'node' in transaction and transaction['node']==self.node_identifier:
					quota += transaction['reward']
				elif own_block: # Trường hợp block được thêm vào nhưng không phải kết quả của Node này
					quota -= 1
		return quota

	# Ép kiểu thành thuộc tính
	@property
	# Lấy block cuối cùng ra 
	def last_block(self):
		"""
		A property method to return the trailing block in the chain
		"""
		return self.chain[-1]

	# Ép kiểu thành thuộc tính
	@property
	# Lấy mảng đệm transaction ra 
	def buffered_transaction(self):
		"""
		A property method to return a list of buffered transactions that
		are not yet written into blocks
		"""
		return self.current_transactions
	
	# Ép kiểu thành phương thức static 
	@staticmethod
	# Hàm mã hóa với SHA-256 
	def hash(block):
		"""
		Creates a SHA-256 hash of a Block

		:param block: Block
		"""

		# sort the dictionary to assert the hash is consistent
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	# Ép kiểu thành phương thức static
	@staticmethod
	# So sánh last_proof và proof có hợp lệ ko 
	def valid_proof(last_proof,proof):
		"""
		Validates the Proof
		In our scenario, there is no need of incentive to create new block
		Therefore, POW should be easy to satisfy
		We use prefix=="00" as criteria

		-------------------------------------------------------------------
		Xác thực the Proof
		Trong kịch bản này, không cần thiết phải tạo block mọi lúc
		Vì vậy, POW dễ được đáp ứng 
		Chúng ta sẽ dùng tiền tố "00" như một tiêu chuẩn đánh giá
		
		:param last_proof: Previous Proof
		:param proof: Current Proof
		:return: True if correct, False if not.
		"""
		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		# Kiểm tra việc encode last_proof và proof với nhau có ra "00xxx" không 
		return guess_hash[:2] == "00"

	# Ép kiểu thành phương thức static
	@staticmethod
	# Hàm tạo số salt
	def salt_generator():
		num = 0
		while True:
			yield num
			num += 1
			if num%100 == 0:
				print("Generating salt...")

	# Hàm proof_of_work
	def proof_of_work(self, last_proof):
		"""
		A proof of work algo. Iterate over different values of salt
		See which salt satisfies valid_proof
		"""
		salt_gen = self.salt_generator()
		salt = next(salt_gen)
		while not self.valid_proof(last_proof,salt):
			salt = next(salt_gen)
		print("POW generated")
		return salt

	# Append transaction tiếp theo vào mảng 
	def new_transaction(self,transaction):
		"""
		Creates a new transaction to go into the next mined Block
		For flexibility, we do not define the format of transactions here

		:param transaction: the new transaction we are appending
		:return: The index of the Block that will hold this transaction
		UPDATE
		:return: The number of transactions in current_transaction
		"""
		self.current_transactions.append(transaction)
		# return self.last_block['index']+1
		return len(self.current_transactions)

	# Append block tiếp theo vào mảng 
	def new_block(self,proof,previous_hash):
		"""
		Create a new Block in the Blockchain

		:param proof: The proof given by the Proof of Work algorithm
		:param previous_hash: Hash of previous Block
		:return: New Block
		"""
		block = {
			'index': len(self.chain) + 1,
			'source': self.node_identifier,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		# Reset the current list of transactions
		self.current_transactions = []

		self.chain.append(block)
		return block        

	# Hàm xử lý khi có sự thay đổi trong chain
	def resolve_conflicts(self):
		"""
		This is our consensus algorithm, it resolves conflicts
		by replacing our chain with the longest one in the network.

		:return: True if our chain was replaced, False if not
		"""

		neighbours = self.nodes
		new_chain = None

		# We're only looking for chains longer than ours
		max_length = len(self.chain)

		# Grab and verify the chains from all the nodes in our network
		for node in neighbours:
			node_addr = f'http://{node}/nodes/chain'
			# print(node_addr)
			response = requests.get(node_addr)

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				# Check if the length is longer and the chain is valid
				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain

		# Replace our chain if we discovered a new, valid chain longer than ours
		if new_chain:
			self.chain = new_chain
			return True

		return False

	#
	@classmethod
	#
	def valid_chain(cls,chain):
		"""
		Determine if a given blockchain is valid

		:param chain: A blockchain
		:return: True if valid, False if not
		"""

		last_block = chain[0]
		current_index = 1

		while current_index < len(chain):
			block = chain[current_index]
			print(f'{last_block}')
			print(f'{block}')
			print("\n-----------\n")
			# Check that the hash of the block is correct
			if block['previous_hash'] != cls.hash(last_block):
				return False

			# Check that the Proof of Work is correct
			if not cls.valid_proof(last_block['proof'], block['proof']):
				return False

			last_block = block
			current_index += 1

		return True




