from pwn import *
import json

def register(username, r):
	l = {'recipient':'Casino', 'command':'Register', 'username':username}
	r.sendline(json.dumps(l).encode())
	data = r.recvrepeat(timeout=0.3).decode()
	log.info(data)

def showbalance(username, r):
	l = {'recipient':'Casino', 'command':'ShowBalanceWithProof', 'username':username}
	r.sendline(json.dumps(l).encode())
	data = r.recvrepeat(timeout=0.3).decode()
	balance, proof = data.strip().split(',')
	balance = int(balance)
	proof = proof.strip()
	return balance, proof

def bet(username, amount, n, r):
	l = {'recipient':'Casino', 'command':'Bet', 'username':username, 'amount':amount, 'n':n}
	r.sendline(json.dumps(l).encode())
	data = r.recvrepeat(timeout=0.3).decode()
	if 'WIN' in data:
		log.success('WIN!!')
		return 1, n
	elif 'LOSE' in data:
		val = int(data.split('(')[1].split('!=')[0])
		return 0, val
	else:
		log.info(f'WARNING: {data = }')
		return 0, 0

def printflag(username, balance, proof, r):
	l = {'recipient':'FlagSeller', 'command':'PrintFlag', 'balance':balance, 'proof_data':proof}
	r.sendline(json.dumps(l).encode())
	data = r.recvrepeat(timeout=0.3).decode()
	log.info(data)


r = remote('192.53.115.129', 31339)

myuser = 'dotti'
register(myuser, r)

ls = []

for i in range(610):
	if i%50 == 0:
		log.info(f'{i = }')
	x, val = bet(myuser, 1, 2023, r)
	ls.append(val)


state = 0
while True:
	if state == 0:
		balance, proof = showbalance(myuser, r)
		log.info(f'{balance = }')
		printflag(myuser, balance, proof, r)
		if balance > 5000:
			cur_bet = balance // 10
		else:
			cur_bet = 10
		log.info(f'{cur_bet = }')

	# https://www.leviathansecurity.com/media/attacking-gos-lagged-fibonacci-generator
	exp = (ls[-273]+ls[-607])%2022
	res, val = bet(myuser, cur_bet, exp, r)
	log.info(f'{exp = } {val = } {res = }')
	ls.append(val)
	if res == 1:
		state = 0

	else:
		state = (state + 1) % 8
