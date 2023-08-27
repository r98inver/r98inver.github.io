from pwn import *

def get_chall(r):
	r.recvline() # [+] Challenge 1/10. Generating random graph...
	r.recvline() # [+] Encrypting graph...
	line = r.recvline().decode() # [*] Destination: 25
	return line.split(':')[-1].strip()

def get_res(r):
	line = r.recvline().decode() # token
	assert 'Token:' in line, line
	token = line.split('Token:')[-1].strip()

	line = r.recvline().decode()
	assert 'Response:' in line, line 
	res = line.split('Response:')[-1].strip()
	l = len(res)//2
	tok, res = res[:l], res[l:]
	return token, tok, res

# SEKAI{3ff1c13nt_GES_4_Shortest-Path-Queries-_-}
r = remote('chals.sekai.team', 3062)

r.sendline(b'SEKAI{GES_15_34sy_2_br34k_kn@w1ng_th3_k3y}')
r.recvline()

for jjj in range(10):
	nodes = {}
	paths = []

	dest_token = None

	dest = int(get_chall(r))
	# Leak all nodes
	for i in range(130):
		if i % 10 == 0:
			log.info(f'{i = }')
		if dest == i:
			continue

		r.sendline(f'{i},{dest}'.encode())
		token, tok, res = get_res(r)
		nodes[token] = i

		path = [token]
		while tok != '':
			path.append(tok[:64])
			tok = tok[64:]


		if dest_token:
			assert path[-1] == dest_token
		else:
			nodes[path[-1]] = dest 
			dest_token = path[-1]

		paths.append(path)

	# Decode graph
	edges = set()
	for path in paths:
		for i in range(1, len(path)):
			start = nodes[path[i-1]]
			end = nodes[path[i]]
			ed = (start, end)
			edges.add(ed) # Shouldn't get duplicates

	counts = [0 for _ in range(130)]
	for start, end in edges:
		counts[start] += 1
		counts[end] += 1

	assert min(counts) == 1 and max(counts) < 130, counts
	counts.sort()

	log.success('Decode success')
	
	# Send answer
	pld = ' '.join([str(i) for i in counts])

	r.sendline(b'1,2')
	get_res(r)
	r.sendline(pld.encode())
	

r.interactive()
	

