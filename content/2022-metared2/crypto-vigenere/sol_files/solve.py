from pwn import *

def encode(text: bytes, key: bytes):
	cnt = 0
	out = []

	def add(a, b):
		return (a+b)%256

	for c in text:
		out.append(add(c, key[cnt]))
		cnt = (cnt+1)%len(key)

	return bytes(out)

def decode(text: bytes, key: bytes):
	cnt = 0
	out = []

	def add(a, b):
		return (a-b)%256
		#return a^b

	for c in text:
		out.append(add(c, key[cnt]))
		cnt = (cnt+1)%len(key)

	return bytes(out)


def attack_single_byte_xor(text: bytes) -> int:
	# key = a...z
	ascii_text_chars = list(range(32, 91)) + list(range(97, 123))
	best = (0, -1) # (number of letters, key)
	for i in range(27):
		candidate_message = decode(text, bytes([i]))
		n_letters = sum([x in ascii_text_chars for x in candidate_message])
		if n_letters > best[0]:
			best = (n_letters,i)

	return (best[0]/len(text), best[1])

def guess_keysize(enc: bytes):
	for key_len in range(2, 30):
		log.info(f'Checking {key_len = }')

		# Split text
		scores = []
		key = []
		for i in range(key_len):
			s = bytes(enc[j] for j in range(i, len(enc), key_len))
			score, k = attack_single_byte_xor(s)
			scores.append(round(score, 3))
			key.append(k)

		avg = round(sum(scores)/len(scores), 3)
		k1 = ''.join([chr(ord('a') + i) for i in key])
		k2 = ''.join([chr(ord('a') + i + 1) for i in key])
		log.info(f'{key = } {k1 = }, {k2 = }, {avg = }')
		#log.info(f'{decode(enc, key)}')

def main():
	with open('criptograma.txt', 'rb') as fh:
		enc = fh.read().strip()

	#guess_keysize(enc)
	
	key_len = 11
	key = [14, 3, 8, 0, 1, 15, 2, 18, 4, 19, 5]

	print(decode(enc, key))
	

if __name__ == '__main__':
	main()