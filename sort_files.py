#!/usr/bin/python

import os
import json
import sys
import shutil

DATA_PATH = '../data/'
FILE_SUFFIX = '.sff'
MissingFiles = []


def FindFile(name, path):
        if os.path.isfile(os.path.join(path, name)):
                return os.path.join(path, name)
        else:  
                for root, dirs, _ in os.walk(path):
                        for dirname in dirs:
                                if name.startswith(dirname):
                                        trytofind = FindFile(name, os.path.join(root, dirname))
                                        if trytofind:
                                                return trytofind
                        for dirname in dirs:
                        	trytofind = FindFile(name, os.path.join(root, dirname))
                                if trytofind:
					return trytofind

        return None

def AddSingleFileToSampleDir(filename, region, sample):
	if filename in MissingFiles:
		print "Skipping %s" % filename
		return
	print "Searching for %s..." % filename
        full_fn = FindFile(filename + FILE_SUFFIX, DATA_PATH)
        if not full_fn:
                print "File %s%s not found" % (filename, FILE_SUFFIX)
		MissingFiles.append(filename)
                return
        directory = DATA_PATH + sample + "_" + region + "_files"
        if not os.path.exists(directory):
                print "Creating dir %s..." % directory
                os.makedirs(directory)
	print "Linking %s to %s..." % (full_fn, directory)
	try:
		os.symlink(full_fn, directory + '/' + filename + FILE_SUFFIX)
	except:
		print "Cant create symlink"

if __name__ == "__main__":
        index = 0
        try:
                index = sys.argv.index('-j')
                if index >= len(sys.argv):
                        raise
        except:
                print "Usage: %s -j <json file>" % os.path.basename(__file__)
                exit(1)
	print "Parsing json..."
        json_data=open(sys.argv[index + 1])
        samples = json.load(json_data)
        json_data.close()
	print "Done parsing."
        for samp in samples:
                files = samp[3]
                for fn in files:
                        AddSingleFileToSampleDir(fn[0], fn[1], samp[0])
