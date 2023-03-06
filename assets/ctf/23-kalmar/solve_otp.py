import itertools
import os 
from pwn import xor, remote, log
import base64 as b64

cset = set('1234567890abcdef'.encode())

PASS_LENGTH_BYTES = 128

r = remote('3.120.132.103', 13338)

line = r.recvrepeat(timeout=0.5)
line = line.split(b'pad:')[1].split(b'Actually')[0].strip().upper()
enc1 = b64.b16decode(line)
log.info('Received enc1')

H = PASS_LENGTH_BYTES//2
permutation = list(range(H)) + list(range(H+1, PASS_LENGTH_BYTES)) + [H]
permutation = [str(i).encode() for i in permutation]

r.sendline(b','.join(permutation))
line = r.recvrepeat(timeout=0.5)
line = line.split(b'pad:')[1].split(b'What')[0].strip().upper()
enc2 = b64.b16decode(line)
log.info('Received enc2')

enc1_even = enc1[0::2]
enc2_even = enc2[0::2]

enc1_odd = enc1[1::2]
enc2_odd = enc2[1::2]

otp_even = [-1 for i in range(PASS_LENGTH_BYTES)]
otp_odd = [-1 for i in range(PASS_LENGTH_BYTES)]

otp_even[0] = 0 # pass[0]^pass[0]
otp_even[H] = enc1_even[0]^enc1_even[H]

otp_odd[0] = 0
otp_odd[H] = enc1_odd[0]^enc1_odd[H]

for i in range(H-1):
	# print(f'Xoring [{i}]^[{permutation[H+i]}]')
	# print(f'Xoring [{i+1}]^[{H+i+1}]')
	
	ev2 = enc2_even[i]^enc2_even[H+i]
	otp_even[H+i+1] = ev2^otp_even[i]

	ev1 = enc1_even[i+1]^enc1_even[H+i+1]
	otp_even[i+1] = ev1^otp_even[H+i+1]

	od2 = enc2_odd[i]^enc2_odd[H+i]
	otp_odd[H+i+1] = od2^otp_odd[i]

	od1 = enc1_odd[i+1]^enc1_odd[H+i+1]
	otp_odd[i+1] = od1^otp_odd[H+i+1]

s_even = set(otp_even)
for c in cset:
	c_xored = set()
	for d in cset:
		c_xored.add(c^d)
	if s_even.issubset(c_xored):
		recovered_even = [chr(c^i) for i in otp_even]
		break

s_odd = set(otp_odd)
for c in cset:
	c_xored = set()
	for d in cset:
		c_xored.add(c^d)
	if s_odd.issubset(c_xored):
		recovered_odd = [chr(c^i) for i in otp_odd]
		break
		
# print(f'{recovered_even = }')
# print(f'{recovered_odd = }')
guess = ''
while recovered_even != []:
	guess += recovered_even.pop(0)
	guess += recovered_odd.pop(0)

log.info(f'{guess = }')
r.sendline(guess.encode())
r.interactive() # The flag is kalmar{guess_i_should_have_read_the_whole_article}
