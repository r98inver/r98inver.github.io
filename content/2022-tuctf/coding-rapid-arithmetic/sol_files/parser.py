from pwn import *
from number_parser import parse
import string
import roman
from random import randint

def parse_all(line, magic=False):

	if 'exec' in line:
		# log.warning(f'excec -> {line}')
		return -1

	if magic:
		if not '++++++' in line and not '==' in line:
			# log.warning(f'MLine: {line}')
			return -2

		line = line.replace('00  00', '00')
		out = ''
		buff = ''
		for c in line:
			if c == ' ':
				out += buff
				buff = ''
				continue

			elif c == buff:
				continue
			
			buff = c

		out += buff
		out = out.replace('=', '-')
		# log.info(f'MLine: {line}')
		# log.info(f'Parsed: {out}')
		return eval(out)

	# Morse
	if '.' in line or '--' in line:
		morses = ['-----','.----','..---','...--','....-','.....','-....','--...','---..','----.']
		for i in range(10):
			line = line.replace(morses[i], str(i))
		line = line.replace(' ', '')

	# Natural language
	line = line.replace(',',' ')
	nl = {'plus':'+', 'minus':'-', 'times':'*', 'negative':'-'}
	line = parse(line)
	for lang in nl:
		line = line.replace(lang, nl[lang])

	# Romans
	S = string.ascii_uppercase
	out = ''
	buffer = ''
	for c in line:
		if c in S:
			buffer += c
		else:
			if buffer != '':
				out += str(roman.fromRoman(buffer))
				buffer = ''
			out += c
	
	line = out

	if not '+' in line and not '-' in line and not '/' in line and not '*' in line and not '(' in line and not ')' in line:
		# log.info(f'{line = }')
		# log.info('Magic Starts')
		return -2

	return eval(line)

if __name__ == '__main__':
	line = '333 00  00 444444   11    ====     22    77    99999 444444'
	print(parse_all(line, True))


