from pwn import *

from lib import GES, utils, DES

# SEKAI{GES_15_34sy_2_br34k_kn@w1ng_th3_k3y}

def get_query(r):
	line = r.recvline().decode()
	assert 'Query' in line, line
	q = line.split(':')[-1].strip().split(' ')

	line = r.recvline().decode()
	assert 'Response:' in line, line
	res = line.split(':')[1].strip()

	return q, res

r = remote('chals.sekai.team', 3001)
while True:
	line = r.recvline().decode()
	if 'Key' in line:
		key = line.split(':')[1].strip()
		log.info(f'{key = }')
	if 'Answer' in line:
		break

key = bytes.fromhex(key)
key_SKE = key[:16]
key_DES = key[16:]


for i in range(50):
	q, res = get_query(r)
	log.info(f'{q = }')
	out = q[0]
	while res != '':
		target = bytes.fromhex(res[:64])
		res = res[64:]
		pt = utils.SymmetricDecrypt(key_SKE,target).decode()

		out += ' ' + pt.split(',')[0]
	log.info(f'{out = }')
	r.sendline(out.encode())

r.interactive()
