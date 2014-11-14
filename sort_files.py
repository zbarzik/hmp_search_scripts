#!/usr/bin/python

import os
import json
import sys

DATA_PATH = '../data'

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    raise Exception("Not found!")

if __name__ == "__main__":
	index = 0
	try:
		index = sys.argv.index('-j')
		print index
		if index == len(sys.argv):
			print "index == len"
			raise	
	except:
		print "Usage: %s -j <json file>" % os.path.basename(__file__)
		exit(1) 
	json_data=open(sys.argv[index + 1])
	samples = json.load(json_data)
	json_data.close()
	for samp in samples:
		files = samp[3]
		for fn in files:
			full_fn = fn + '.sff'
			print full_fn
			print find(full_fn, DATA_PATH)	
