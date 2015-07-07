# Tested on Python 2.7.6 on Max OS X 10 (Yosemite)

# Inbuilt
import sys
import datetime
import time
import sqlalchemy
import json
from pprint import pprint

# External
import dataset # https://dataset.readthedocs.org/en/latest/api.html
import requests # http://docs.python-requests.org/en/latest/

# API we're going to hit: http://docs.blockstrap.com/en/api/v0/blocks/block-height/
# Here's more about it: http://blockstrap.com/en/api/#start
# For reference: 3 blocks (2 orphans) at height 317930

DATABASE_NAME = 'blockchain.db' # name of the database to use
TABLE_NAME = 'blocks' # name of the table to store the data
WAIT_TIME = 1 # wait 1 second between API calls (per anonymous usage T&Cs)


def main():
	db = connect_to_db(DATABASE_NAME)
	blocks_table = create_blocks_table(db, TABLE_NAME)
	num_of_blocks = how_many_blocks_to_add()
	start_height = get_next_block_height(db, TABLE_NAME)
	store_block_data(blocks_table, start_height, num_of_blocks)
	print_last_row(db, TABLE_NAME)

def connect_to_db(filename):
	# Connect to the database, or create it if it doesn't already exist
	db = dataset.connect('sqlite:///' + filename)
	print 'Using database:', filename
	return db

def create_blocks_table(db, table_name):
	# Create the blocks table if it doesn't exist
	if table_name not in db.tables:
		t = db.create_table(table_name)

		t.create_column('height', sqlalchemy.Integer)
		t.create_column('time', sqlalchemy.Integer)
		t.create_column('tx_count', sqlalchemy.Integer)
		t.create_column('size', sqlalchemy.Integer)
		t.create_column('input_value', sqlalchemy.Integer)
		t.create_column('output_value', sqlalchemy.Integer)
		t.create_column('fees', sqlalchemy.Integer)
		t.create_column('coinbase_value', sqlalchemy.Integer)
		t.create_column('orphans', sqlalchemy.Integer)
		t.create_column('destroyed_satoshi_seconds', sqlalchemy.Integer)
		t.create_column('version', sqlalchemy.Integer)

	else:
		t = db[table_name]
	return t

def how_many_blocks_to_add():
	# Specify how many blocks we want to add
	if len(sys.argv) > 1:
		n = int(sys.argv[1])
	else:
		print '-----'
		print 'Usage: To add more than 1 block, pass the number of blocks as a command line argument.'
		print 'eg, for 500 blocks, type python', sys.argv[0], '500'
		print '-----'
		n = 1
		raw_input('Press enter to continue...')
	return n

def get_next_block_height(db, table_name):
	# Find where we got to last, plus 1
	res = db.query('SELECT MAX(height) FROM ' + table_name)
	for r in res:
		max_height = r['MAX(height)']
	print 'Max block height found in database:', max_height

	if max_height is None:
		start_height = 0
	else:
		start_height = max_height + 1
	return start_height

def block_json_to_dict(block_json):
	main_chain_block = block_json['data']['blocks'][0]

	d = {}
	
	d['height'] = main_chain_block['height']
	d['time'] = main_chain_block['time']
	d['tx_count'] = main_chain_block['tx_count']
	d['size'] = main_chain_block['size']
	d['input_value'] = main_chain_block['input_value']
	d['output_value'] = main_chain_block['output_value']
	d['fees'] = main_chain_block['fees']
	d['coinbase_value'] = main_chain_block['coinbase_value']
	d['orphans'] = len(block_json['data']['blocks']) - 1
	d['destroyed_satoshi_seconds'] = main_chain_block['destroyed_satoshi_seconds']
	d['version'] = main_chain_block['version']
	return d

def print_to_log(block_dict):
	print '\nInserting block', block_dict['height']
	pprint(block_dict, width = 1)

	print '\tDerived (local) time:\t', datetime.datetime.fromtimestamp(int(block_dict['time'])).strftime('%Y-%m-%d %H:%M:%S')
	print '\tDerived coinbase (btc):\t', '{0:,.4f}'.format(block_dict['coinbase_value'] / 100000000)
	print '\tDerived size (b):\t', '{0:,}'.format(block_dict['size'])
	print '\tDerived size (kb):\t', '{0:,.1f}'.format(block_dict['size'] / 1024)
	print '\tDerived inputs (btc):\t', '{0:,.4f}'.format(block_dict['input_value'] / 100000000.0)
	print '\tDerived fees (btc):\t', '{0:,.4f}'.format(block_dict['fees'] / 100000000.0)

def store_block_data(blocks_table, start_height, num_of_blocks):
	# loop for the number of blocks you want to add (num_of_blocks)
	print 'Adding %s block(s)...' % (num_of_blocks)
	raw_input('Press enter to continue...')

	i = 0
	while i < num_of_blocks:
		url = 'http://api.blockstrap.com/v0/BTC/block/height/' + str(start_height + i)
		r = requests.get(url)

		if r.status_code == 200:
			block_dict = block_json_to_dict(r.json())
			print_to_log (block_dict)
			blocks_table.insert(block_dict)
			print 'Block', block_dict['height'], 'inserted successfully'
			i = i + 1

		else:
			print time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'Failed with status code:', r.status_code, url
			print 'Waiting 1 minute'
			time.sleep(59) # for when you get to the top block.  Beware, you may not be getting the main chain.

		time.sleep(WAIT_TIME)

def print_last_row(db, table_name):
	# print the last row of the table
	res = db.query('SELECT * FROM ' + table_name + ' WHERE height = (SELECT MAX(height) FROM ' + table_name + ')')
	for r in res:
		print '\n-----'
		print 'This is the last row added:'
		print(json.dumps(r, indent=2)) # need to dump the OrderedDict as a Json or it won't print well
		print 'Last block\'s time:', datetime.datetime.fromtimestamp(int(r['time'])).strftime('%Y-%m-%d %H:%M:%S')
		print 'Current time:', time.strftime('%Y-%m-%d %H:%M:%S %Z'), '\n'

main()

