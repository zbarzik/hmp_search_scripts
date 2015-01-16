#!/usr/bin/python
#set(['V1-V3', 'V5-V3', 'V6-V9', 'V3-V5', 'V3-V1'])
#set(['Buccal mucosa', 'L_Retroauricular crease', 'Palatine Tonsils', 'Anterior nares', 'water blank', 'Vaginal introitus', 'R_Antecubital fossa', 'Hard palate', 'Stool', 'Throat', 'Mid vagina', 'Supragingival plaque', 'Attached/Keratinized gingiva', 'Subgingival plaque', 'L_Antecubital fossa', 'positive control', 'Posterior fornix', 'Saliva', 'Tongue dorsum', 'R_Retroauricular crease'])

import csv
import sys
import os
import re
import json

METADATA_PATH = './metadata'
METADATA_TAR = 'metadata.tar'
Region = set([])
SampleType = set([])
Sequence = set([])
Sample = set([])
SampleRegions = {}
SamplesWithMultipleRegions = {}

def AreRegionsTheSame(region1, region2):
	digits1 = map(int, re.findall(r'\d+', region1))
	digits2 = map(int, re.findall(r'\d+', region2))
	digSet1 = set(digits1)
	digSet2 = set(digits2)
	assert len(digSet1) == 2
	assert len(digSet2) == 2
	return len(digSet1 & digSet2) == 2

def CreateValueSets(sequence, region, sample_type, sample):
	if sample_type == "water blank" or sample_type == "positive control":
		return
	Region.add(region)
	SampleType.add(sample_type)
	Sequence.add(sequence)
	Sample.add(sample)

def ShowProgress():
        sys.stderr.write('.')
	
def IterateFiles(func):
	for path, _, filenames in os.walk(METADATA_PATH):
		for fn in filenames:
			if not fn.endswith('.lmd'):
				continue
			ShowProgress()
			with open(os.path.join(path, fn),'r') as f:
	    			reader=csv.reader(f,delimiter='\t')
				fn_nosuffix = fn[:-4]
				for (filename, experiment, arg2, arg3, sequence, arg4, arg5, region, arg6, sequenced_sample, arg8, sample_type, id_of_sort) in reader:
					func(sequence, region, sample_type, sequenced_sample, filename)

def BuildSampleDictionaries(sequence, region, sample_type, sample, filename):
	region = GetRegionString(region)
	if filename == "NULL" or sample_type == "water blank" or sample_type == "positive control":
		return
	fileRegionTupple = (filename, GetRegionString(region))
	if SampleRegions.has_key(sample):
		if SampleRegions[sample][0] != sample_type:
			raise Exception("%s has %s instead of %s" %(sample, SampleRegions[sample][0], sample_type))
		regions = set([ SampleRegions[sample][1], region ])
		files = set([ (SampleRegions[sample][3], SampleRegions[sample][1]), fileRegionTupple ])
		if SamplesWithMultipleRegions.has_key(sample):
			regions = regions | SamplesWithMultipleRegions[sample][1]
			files = files | SamplesWithMultipleRegions[sample][3]
		SamplesWithMultipleRegions.update({sample:(sample_type, regions, sequence, files)})
	else:
		SampleRegions.update({sample:(sample_type, region, sequence, filename)})

def GetRegionString(region):
	if region.upper()=="V5-V3":
		return "V3-V5"
	elif region.upper()=="V3-V1":
		return "V1-V3"
	else:
		return region
	
def PrintRegions(regionSet):
	output = ""
	for reg in regionSet:
		output = output + GetRegionString(reg) + ", "
	return output[:-2]
	
def PrintFiles(filesSet):
	output = ""
	for fn_tup in filesSet:
		output = output + fn_tup[0] + "(" + fn_tup[1] + ")" + ', '
	return output[:-2]

def PrintResults(numberFilter = None):
	for samp in SamplesWithMultipleRegions:
        	(sample_type, regions, sequence, files) = SamplesWithMultipleRegions[samp]
		if not numberFilter:
			if len(regions) == 1:
				continue
		elif len(regions) != numberFilter:
			continue
                print "%s\t%s\t%s\t%s" %(samp, PrintRegions(regions), sample_type, PrintFiles(files))
	sys.stderr.write('\n')

def ProduceJsonResults(numberFilter = None):
	tmpList = []
	for samp in SamplesWithMultipleRegions:
		(sample_type, regions, sequence, files) = SamplesWithMultipleRegions[samp]
		if not numberFilter:
			if len(regions) == 1:
				continue
		elif len(regions) != numberFilter:
			continue
		tmpList.append((samp, list(regions), sample_type, list(files)))
	print json.dumps(tmpList)
	sys.stderr.write('\n')

def SearchMetadata(json = False):
	if not os.path.exists(METADATA_PATH):
		os.makedirs(METADATA_PATH)
		ret = os.system("tar -xf %s -C %s" % (METADATA_TAR, METADATA_PATH))
		if ret != 0:
			print "Error untaring files"
			exit(1)
	IterateFiles(BuildSampleDictionaries)
	if json:
		ProduceJsonResults()
	else:
		print "Sample\tRegions\tType\tIn Files"
		PrintResults(3)
		PrintResults(2)

if __name__ == "__main__":
	SearchMetadata(json='--json' in sys.argv)
