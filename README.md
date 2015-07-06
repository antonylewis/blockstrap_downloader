# Blockstrap Downloader
Blockstrap downloader is a Python wrapper for the Blockstrap blockchain API

## Description
Blockstrap downloader downloads data about Bitcoin blocks and stores them in a SQLite database on your computer.  You can then do what you want with it, like make charts etc.

Blockstrap's API is here: http://blockstrap.com/en/api/
There are quite a few endpoints provided, which are listed here: http://blockstrap.com/en/api/#start
This wrapper uses the "block height" endpoint: https://api.blockstrap.com/v0/BTC/block/height/<INT_HEIGHT> 
It asks for data, block by block, in order from the first "genesis" block through to the latest block, parses the JSON response, and stores relevant data down into a small database, which by default is 'database.db'.
Currently I'm interested in the data from the blocks, rather than specific transaction data, so I'm only storing block level data (main chain blocks only, though if there are orphans, this notes the number of orphans at each block height)

# Warning!
It takes quite a while!  It uses the anonymous API, which limits to one request per second.  Currently there are over 360,000 blocks in the Bitcoin Blockchain, so expect this to take over 100 hours.

## Dependencies
Here are the dependencies:
dataset # https://dataset.readthedocs.org/en/latest/api.html
requests # http://docs.python-requests.org/en/latest/

You can get them by doing:
    sudo pip install dataset, requests

## Usage
Just go to the directory containing blockstrap.py and type
    python blockstrap.py [number of blocks you want to download]
eg
    python blockstrap.py 500
If you don't use a number, it will just download 1 block.

## Notes
Please offer improvements!
This is my first piece of code I have put "out there".  Be gentle.  Thanks :)
