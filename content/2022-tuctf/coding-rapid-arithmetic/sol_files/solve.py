from pwn import *
from number_parser import parse
import roman
import string
import parser
import importlib
import time
import random

r = remote('chals.tuctf.com', 30200)

wrn = 0
verb = 0
logs = []
keep = False
magic = False

old_line = ''

while wrn < 200:

	if not keep:
		old_line = line
		line = r.recvline(timeout=0.3)
		orig_line = line.decode()
		line = line.decode().replace('Answer:','').strip()
	keep = False

	if 'Correct!' in line:
		log.success(line)
		continue

	if 'Incorrect' in line:
		log.warning('Incorrect')
		log.info(f'{logs[-1] = }')
		log.info(f'{old_line = }')
		break

	if line == '':
		wrn += 1
		if wrn%20 == 0:
			log.warning(f'Empty - {wrn = }')
		continue
	
	verb += 1 
	if verb>=20:
		log.info(f'{line = }')
		verb = 0
	
	try:
		n = parser.parse_all(line, magic)
		if n == -1:
			continue
		if n == -2:
			if not magic:
				open('out', 'a').write('\nMAGIC\n')
			#log.info(f'{orig_line = }')
			#log.info(f'{old_line = }')
			magic = True
			continue
			
		n = round(n)
		r.sendline(str(n).encode())
		open('out', 'a').write(str(n) + ' ')
		logs.append(n)
		log.info(f'{n = }')
		wrn = 0

	except Exception as e:
		log.info(f'{e = }')
		log.info(f'{line = }')
		log.info(f'{orig_line = }')
		log.info(f'{old_line = }')
		time.sleep(1)
		importlib.reload(parser)
		keep = True


print(logs)





#136, 137, 196, 140, 207, 183, 199, 207, 174, 209, 230, 164, 202, 222, 229, 151, 140, 168, 251, 246, 191, 196, 255, 228, 139, 191, 224, 244, 246, 186, 227, 226, 202, 212, 233, 169, 185, 217, 232, 199, 199, 214, 150, 250, 238, 252, 180, 140, 168, 217, 251, 202, 176, 186, 254, 229, 234, 231, 157, 244, 183, 146, 168, 173, 233, 242, 215, 199, 173, 240, 171, 234, 241, 214, 244, 252, 139, 164, 151, 216, 158, 238, 176, 197, 219, 240, 158, 174, 194, 254, 159, 142, 248, 161, 202, 188, 215, 222, 192, 210, 157, 235, 202, 228, 248, 147, 182, 217, 207, 220, 197, 150, 143, 215, 173, 215, 185, 230, 227, 228, 249, 251, 190, 197, 180, 186, 218, 241, 194, 154, 231, 170, 238, 188, 182, 200, 245, 219, 215, 233, 216, 157, 200, 254, 242, 194, 217, 138, 188, 208, 193, 203, 221, 167