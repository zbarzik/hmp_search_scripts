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
IGNORE_SAMPLE_TYPES = [ "water blank", "positive control" ]
IGNORE_FILENAMES = [ 'SRR058115', 'SRR042815', 'SRR046214', 'SRR052699', 'SRR058087', 'SRR058086', 'SRR058085', 'SRR058084', 'SRR057663', 'SRR057609', 'SRR058120', 'SRR058089', 'SRR058088', 'SRR058107', 'SRR058108', 'SRR058109', 'SRR042796', 'SRR058098', 'SRR047551', 'SRR058090', 'SRR058091', 'SRR058092', 'SRR058093', 'SRR058094', 'SRR058095', 'SRR058096', 'SRR058097', 'SRR058114', 'SRR058111', 'SRR045646', 'SRR058113', 'SRR058112']
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
	if sample_type in IGNORE_SAMPLE_TYPES:
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
	samplesToDrop = set([])
        for samp in SamplesWithMultipleRegions:
                (sample_type, regions, sequence, files) = SamplesWithMultipleRegions[samp]
		if DoFilesHaveDuplicateRegions(files):
			samplesToDrop = samplesToDrop | set([ samp ])
	for samp in samplesToDrop:
		del SamplesWithMultipleRegions[samp]
			
	

def BuildSampleDictionaries(sequence, region, sample_type, sample, filename):
	TYPE_IDX = 0
        REGION_IDX = 1
        SEQUENCE_IDX = 2
        FILE_IDX = 3
	region = GetRegionString(region)
	if filename == "NULL" or sample_type in IGNORE_SAMPLE_TYPES or filename in IGNORE_FILENAMES:
		return
	fileRegionTupple = (filename, GetRegionString(region))
	if SampleRegions.has_key(sample):
		if SampleRegions[sample][TYPE_IDX] != sample_type:
			raise Exception("%s has %s instead of %s" %(sample, SampleRegions[sample][TYPE_IDX], sample_type))
		regions = set([ SampleRegions[sample][REGION_IDX], region ])
		files = set([ (SampleRegions[sample][FILE_IDX], SampleRegions[sample][REGION_IDX]), fileRegionTupple ])
		if SamplesWithMultipleRegions.has_key(sample):
			regions = regions | SamplesWithMultipleRegions[sample][REGION_IDX]
			files = files | SamplesWithMultipleRegions[sample][FILE_IDX]
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

def DoFilesHaveDuplicateRegions(filesSet):
	justFiles = set([ ])
	for filename, _ in filesSet:
		justFiles = justFiles | set([ filename ])
	return len(justFiles) != len(filesSet)

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

def ProduceJsonResults(printJson = True, numberFilter = None):
	tmpList = []
	for samp in SamplesWithMultipleRegions:
		(sample_type, regions, sequence, files) = SamplesWithMultipleRegions[samp]
		if not numberFilter:
			if len(regions) == 1:
				continue
		elif len(regions) != numberFilter:
			continue
		tmpList.append((samp, list(regions), sample_type, list(files)))
	jsonRes = json.dumps(tmpList)
	if (printJson):
		print jsonRes
		sys.stderr.write('\n')
        return jsonRes

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
