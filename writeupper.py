#!/usr/bin/env python3
import os
from pwn import log
import shutil
from datetime import datetime

# Folder of all the ctf, asks for selection
ctf_folder = '/home/r98inver/pitucci-ctf/tmp'

# Destination folder in the website
content_folder = './content'

def ctf_selection():
	ls = os.listdir(ctf_folder)
	ls.sort()
	log.info('Available CTFs:\n\t' + '\n\t'.join([f'[{i}] {j}' for i,j in enumerate(ls)]))
	log.info('Your choice: ')
	a = input()
	return ls[int(a)]

def chall_selection(ctf_name):
	log.success(f'Selected CTF: {ctf_name}')
	path = f'{ctf_folder}/{ctf_name}'
	ls = os.listdir(path)
	ls.sort()
	log.info('Available challenges:\n\t' + '\n\t'.join([f'[{i}] {j}' for i,j in enumerate(ls)])+'\n\t[*] All' )
	log.info('Your choice (comma separated): ')
	a = input().strip()
	if a == '*':
		return ls
	else:
		return [ls[int(i)] for i in a.split(',')]


if __name__ == '__main__':

	# CTF Selection
	ctf_name = ctf_selection()

	# Challenge selection
	chall_names = chall_selection(ctf_name) # a list with the name of the selected challs

	# CTF folder
	ctf_path_from = f'{ctf_folder}/{ctf_name}'
	ctf_path_to = f'{content_folder}/{ctf_name}'
	
	for chall_name in chall_names:
		log.info(f'Copying challenge {chall_name}')

		chall_info = chall_name.split('-')
		category = chall_info[1]
		title = ' '.join([i.capitalize() for i in chall_info[2:]])	
		chall_new_name = '-'.join(chall_info[1:])

		if chall_name[:7] != 'solved-':
			log.warning('Not solved, skipping')
			continue


		# Copy files
		chall_path_from = f'{ctf_path_from}/{chall_name}'
		chall_path_to = f'{ctf_path_to}/{chall_new_name}'

		if os.path.isdir(chall_path_to):
			log.warning('Already existing, skipping')
			continue

		chall_pld = ''
		solve_pld = ''

		if os.path.isdir(f'{chall_path_from}/chall_files'):
			shutil.copytree(f'{chall_path_from}/chall_files', f'{chall_path_to}/chall_files')
			chall_pld = '### Challenge Files  \n\n'
			for filename in os.listdir(f'{chall_path_from}/chall_files'):
				chall_pld += '- ['+filename+']({static}chall_files/'+filename+')\n'
			chall_pld += '\n'

		if os.path.isdir(f'{chall_path_from}/sol_files'):
			shutil.copytree(f'{chall_path_from}/sol_files', f'{chall_path_to}/sol_files')
			solve_pld = '### Solve Files  \n\n'
			for filename in os.listdir(f'{chall_path_from}/sol_files'):
				solve_pld += '- ['+filename+']({static}sol_files/'+filename+')\n'
			solve_pld += '\n'
		
		if not any([chall_pld, solve_pld]):
			log.warning('File structure not found, skipping')
			continue

		# README generator
		now = datetime.now()
		date = now.strftime("%Y-%m-%d %H:%M:%S")
		ctf_slug = ctf_name.split('-')[1]
		if ctf_name.split('-')[0] != '00':
			ctf_slug += ' ' + ctf_name.split('-')[0] # Year if not permanent
		slug = '-'.join([ctf_name, chall_new_name])
		if os.path.isfile(f'{chall_path_from}/flag.txt'):
			flag = open(f'{chall_path_from}/flag.txt').read().strip()
		else:
			flag = '[FLAG HERE]'

		if os.path.isfile(f'{chall_path_from}/desc.txt'):
			desc = open(f'{chall_path_from}/desc.txt').read().strip()
		elif os.path.isfile(f'{chall_path_from}/description.txt'):
			desc = open(f'{chall_path_from}/description.txt').read().strip() 
		else:
			desc = '[DESCRIPTION HERE]'

		# Fill the markdown template
		txt = open('writeupper_template.md', 'r').read().strip()
		txt = txt.replace('{{chall_title}}', title)
		txt = txt.replace('{{chall_date}}', date)
		txt = txt.replace('{{chall_category}}', category)
		txt = txt.replace('{{chall_slug}}', slug)
		txt = txt.replace('{{chall_ctf}}', ctf_slug)
		txt = txt.replace('{{chall_flag}}', flag)
		txt = txt.replace('{{chall_desc}}', desc)
		txt = txt.replace('{{chall_files}}', chall_pld)
		txt = txt.replace('{{chall_sol_files}}', solve_pld)

		with open(f'{chall_path_to}/README.md', 'w') as fh:
			fh.write(txt)

		# Todo list update
		with open('TODO.md', 'a') as fh:
			fh.write(f'- [ ] {ctf_slug}/{chall_new_name}\n')

		log.success('Challenge saved')
