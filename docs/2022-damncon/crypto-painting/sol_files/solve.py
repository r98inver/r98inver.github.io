import os
from PIL import Image
im = Image.open('img.jpg')

## IMAGE CROPPER
print(im.size)

wh = 51-19
he = 47-1
j_right = 2
j_bot = 2

start_left = 19
start_top = 1

for row in range(17):
	# print(f'{row = }')
	for col in range(14):
		if row == 16 and col == 6:
			break
		# print(f'{col = }')
		left = start_left + col*(wh + j_right)
		top = start_top + row*(he + j_bot)
		right = left + wh
		bottom = top + he
		new_img = im.crop((left+3, top+3, right-3, bottom-3))
		new_img.save(f'data/{str(row).zfill(2)}{str(col).zfill(2)}.jpg')


## HUE DECODER
def roundcolor(c):
	dist = [(abs(c-0), 0), (abs(c-127), 127), (abs(c-255),255)]
	dist.sort()
	return dist[0][1] # Closest color

def hexhue2code(img):
	out = ''

	colormap = {
		(127, 255, 0):'G', # Green
		(255, 255, 0):'Y', # Yellow
		(0, 0, 255): 'B', # Blue
		(0, 255, 0): 'G', # Green
		(255, 0, 0): 'R', # Red
		(0, 255, 255): 'C', # Cyan
		(255, 0, 255): 'P', # Purple
		(0,0,0): 'D', # Black
		(127,127,127): 'X', #Grey
		(255,255,255): 'W' # White
	}

	im = Image.open(img)
	w,h = im.size
	pix = im.load() # pix[i, j]: i is the distance from origin on x axis, j on y axis

	# Top Left
	col = [0,0,0]
	for i in range(4):
		for j in range(4):
			p = pix[i,j]
			for k in range(3):
				col[k] += p[k]
	col = [c//16 for c in col]
	col = tuple(roundcolor(c) for c in col)
	out += colormap[col]

	# Top Right
	col = [0,0,0]
	for i in range(w-4,w):
		for j in range(4):
			p = pix[i,j]
			for k in range(3):
				col[k] += p[k]
	col = [c//16 for c in col]
	col = tuple(roundcolor(c) for c in col)
	out += colormap[col]

	# Mid Left
	col = [0,0,0]
	for i in range(4):
		for j in range(h//2-2, h//2+2):
			p = pix[i,j]
			for k in range(3):
				col[k] += p[k]
	col = [c//16 for c in col]
	col = tuple(roundcolor(c) for c in col)
	out += colormap[col]
	
	# Mid Right
	col = [0,0,0]
	for i in range(w-4,w):
		for j in range(h//2-2, h//2+2):
			p = pix[i,j]
			for k in range(3):
				col[k] += p[k]
	col = [c//16 for c in col]
	col = tuple(roundcolor(c) for c in col)
	out += colormap[col]

	# Down Left
	col = [0,0,0]
	for i in range(4):
		for j in range(h-4,h):
			p = pix[i,j]
			for k in range(3):
				col[k] += p[k]
	col = [c//16 for c in col]
	col = tuple(roundcolor(c) for c in col)
	out += colormap[col]

	# Down Right
	col = [0,0,0]
	for i in range(w-4,w):
		for j in range(h-4,h):
			p = pix[i,j]
			for k in range(3):
				col[k] += p[k]
	col = [c//16 for c in col]
	col = tuple(roundcolor(c) for c in col)
	out += colormap[col]
	
	return out

def code2str(code):
	dic = {
		'PRGYBC':'A',
		'RPGYBC':'B',
		'RGPYBC':'C',
		'RGYPBC':'D',
		'RGYBPC':'E',
		'RGYBCP':'F',
		'GRYBCP':'G',
		'GYRBCP':'H',
		'GYBRCP':'I',
		'GYBCRP':'J',
		'GYBCPR':'K',
		'YGBCPR':'L',
		'YBGCPR':'M',
		'YBCGPR':'N',
		'YBCPGR':'O',
		'YBCPRG':'P',
		'BYCPRG':'Q',
		'BCYPRG':'R',
		'BCPYRG':'S',
		'BCPRYG':'T',
		'BCPRGY':'U',
		'CBPRGY':'V',
		'CPBRGY':'W',
		'CPRBGY':'X',
		'CPRGBY':'Y',
		'CPRGYB':'Z',
		'DWWDDW':'.',
		'WDDWWD':',',
		'WWWWWW':' ',
		'DDDDDD':' ',
		'DXWDXW':'0',
		'XDWDXW':'1',
		'XWDDXW':'2',
		'XWDXDW':'3',
		'XWDXWD':'4',
		'WXDXWD':'5',
		'WDXXWD':'6',
		'WDXWXD':'7',
		'WDXWDX':'8',
		'DWXWDX':'9',
	}
	return dic[code]
	
def hexhue2str(img):
	code = hexhue2code(img)
	return code2str(code)

out = ''
for i in sorted(os.listdir('data')):
	out += hexhue2str(f'data/{i}')
print(out) 
# IC0GLI4ULS0GLS4TLSAULI0TLI0GLS4TLSATLS0TLSAULI0GLI4ULS0GLI4TLS4TIC4TLI4GLI4TIC0ULS4GLS4TIC4ULS0ULSATLSAULS0TLSATLS4GLI4ULIATIC4ULS0ULSATLI0TIC0TLS0TIC4ULSAULI0TLI0GLS0UIC4ULI0TIC0GLI4TLS4TIC4ULIAULI0GLS4TLIATLI0UIC4ULI0TIC4ULI4UIA
