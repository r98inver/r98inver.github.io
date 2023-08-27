# https://dl.acm.org/doi/pdf/10.1145/3433210.3453099 <- protocol
# https://eprint.iacr.org/2022/838.pdf <- attack

# nc chals.sekai.team 3023
from pwn import *
import networkx as nx
import json
import datetime

from tree_stuff import *

def get_menu(r):
	r.recvuntil(b'==============================\n')

def get_graph(r):
	r.sendline(b'1')
	for i in range(5): # flush
		line = r.recvline().decode()
		if "Edges" in line:
			break
	assert "Edges" in line, line 
	edges_str = line.split("Edges:")[-1].strip()
	edges = eval(edges_str)
	return edges

def get_responses(r):
	def query_to_chunk(q):
		chunks = []
		while q != '':
			chunks.append(q[:64])
			q = q[64:]
		return chunks

	r.sendline(b'2')
	Q = {} 
	# Q is a dictionary of the SDSP for each token, i.e. { 'last token' : SDSP('last token')}
	# Each SDSP is a dictionary { node : [SP from root to node] }
	while True:
		line = r.recvline().decode().strip()
		if 'MENU' in line:
			return Q
		if '>' in line:
			continue

		token = line.split(' ')[0]
		token = query_to_chunk(token)
		# Format SDSP
		source = token[0]
		dest = token[-1]
		token = token[::-1]

		tok_SDSP = Q.get(dest, {})
		tok_SDSP[source] = token
		Q[dest] = tok_SDSP	

def get_challenge(r):
	while True:
		line = r.recvline().decode().strip()
		if 'Token:' in line:
			tok = line.split('Token:')[-1].strip()
		elif 'Query Response:' in line:
			res = line.split('Query Response:')[-1].strip()
			break

	L = len(res) // 2
	res = res[:L]
	return tok + res


while True:
	# Probably useless: reject multi-component graph
	r = remote('chals.sekai.team', 3023)
	r.sendline(b'SEKAI{3ff1c13nt_GES_4_Shortest-Path-Queries-_-}')

	get_menu(r)
	edges = get_graph(r)
	get_menu(r)
	G = nx.Graph()
	G.add_edges_from(edges)
	conn_cp = list(nx.connected_components(G))
	if len(conn_cp) == 1 and len(edges) == 59:
		log.success('Got Connected Tree!')
		break
	log.warning('Bad graph')
	r.close()

# Locally compute the tree and the labels
tic = time.time()
M = {} # Path multimap
for root in G.nodes:
	# This is Algorithm 2: PreprocessGraph	
	SDSP = nx.single_source_shortest_path(G, root) # from GES.computeSDSP()
	tree = SDSP_to_tree(root, SDSP)
	path_names = compute_path_names(tree)
	for dest, path_sig in path_names.items():
		shortest_path = SDSP[int(dest)][::-1]
		path = ' '.join([str(sspp) for sspp in shortest_path])
		M[path_sig] = M.get(path_sig, []) + [path]

log.success(f'Graph preprocessing done in {time.time() - tic} sec')

# Get all the queries and compute the respective labels
tic = time.time()
Q = get_responses(r)
get_menu(r)
assert len(Q) == 60, Q.keys()

Q_map = {} # Query to path name
for root in Q:
	SDSP = Q[root]
	tree = SDSP_to_tree(root, SDSP)
	path_names = compute_path_names(tree)
	for dest, path_sig in path_names.items():
		# Recover the original token
		tok = SDSP[dest]
		tok = tok[::-1]
		tok = ''.join(tok)

		# Save the mapping token -> signature
		Q_map[tok] = path_sig

log.success(f'Query processing done in {time.time() - tic} sec')
log.info(f'{len(Q) = } {len(Q_map) = }')

# Get challenge
r.sendline(b'3')
for i in range(10):
	tok = get_challenge(r)
	path_name = Q_map[tok]
	q = M[path_name]
	log.info(f'{q = }')
	r.sendline(q[0].encode())

r.interactive()
# SEKAI{Full_QR_Attack_is_not_easy_https://eprint.iacr.org/2022/838.pdf}