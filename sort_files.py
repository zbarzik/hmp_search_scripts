#!/usr/bin/python

import os
import json
import sys
import shutil

DATA_PATH = '../data/'

def FindFile(name, path):
        for root, dirs, files in os.walk(path):
                if name in files:
                        return os.path.join(root, name)
        raise Exception("Not found!")

def AddSingleFileToSampleDir(filename, region, sample):
        full_fn = filename + '.sff'
        directory = DATA_PATH + sample + "_" + region + "_files"
        print directory
        if not os.path.exists(directory):
                print "creating dir"
                os.makedirs(directory)
        shutil.copy(FindFile(full_fn, DATA_PATH), directory)

if __name__ == "__main__":
        index = 0
        try:
                index = sys.argv.index('-j')
                if index >= len(sys.argv):
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
                        print(fn)
                        AddSingleFileToSampleDir(fn[0], fn[1], samp[0])
