#!/usr/bin/python
#set(['V1-V3', 'V5-V3', 'V6-V9', 'V3-V5', 'V3-V1'])
#set(['Buccal mucosa', 'L_Retroauricular crease', 'Palatine Tonsils', 'Anterior nares', 'water blank', 'Vaginal introitus', 'R_Antecubital fossa', 'Hard palate', 'Stool', 'Throat', 'Mid vagina', 'Supragingival plaque', 'Attached/Keratinized gingiva', 'Subgingival plaque', 'L_Antecubital fossa', 'positive control', 'Posterior fornix', 'Saliva', 'Tongue dorsum', 'R_Retroauricular crease'])

import csv
import sys
import os
import re

#indir = '~/Downloads/corrected-metadata-v1'
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
	for path, _, filenames in os.walk('.'):
		for fn in filenames:
			if not fn.endswith('.lmd'):
				continue
			ShowProgress()
			with open(os.path.join(path, fn),'r') as f:
	    			reader=csv.reader(f,delimiter='\t')
				fn_nosuffix = fn[:-4]
	    			for arg0, arg1, arg2, arg3, sequence, arg4, arg5, region, arg6, arg7, arg8, sample_type, sample in reader:
					func(sequence, region, sample_type, sample, fn_nosuffix)

def BuildSampleDictionaries(sequence, region, sample_type, sample, filename):
        if sample_type == "water blank" or sample_type == "positive control":
                return
	if SampleRegions.has_key(sample) and SampleRegions[sample][0] != sample_type:
		raise Exception("Probably a bug - sample %s had sample_type %s but now found sample_type %s" % (sample, SampleRegions[sample][0], sample_type))
	if SampleRegions.has_key(sample) and not AreRegionsTheSame(SampleRegions[sample][1], region):
		regions = set([ SampleRegions[sample][1], region ])
		files = set([ SampleRegions[sample][3], filename ])
		if SamplesWithMultipleRegions.has_key(sample):
			regions = regions | SamplesWithMultipleRegions[sample][1]
			files = files | SamplesWithMultipleRegions[sample][3] 	
		SamplesWithMultipleRegions.update({sample:(sample_type, regions, sequence, files)})
	SampleRegions.update({sample:(sample_type, region, sequence, filename)})
	
def PrintRegions(regionSet):
	output = ""
	for reg in regionSet:
		if reg=="V5-V3":
			output = output + "V3-V5, "
		elif reg=="V3-V1":
			output = output + "V1-V3, "
		else:
			output = output + reg + ", "
	return output[:-2]
	
def PrintFiles(filesSet):
	output = ""
	for fn in filesSet:
		output = output + fn + ', '
	return output[:-2]

def PrintResults(numberFilter = None):
	for samp in SamplesWithMultipleRegions:
        	(sample_type, regions, sequence, files) = SamplesWithMultipleRegions[samp]
        	if numberFilter and len(regions) != numberFilter:
			continue
                print "%s\t%s\t%s\t%s" %(samp, PrintRegions(regions), sample_type, PrintFiles(files))

#print "Iterating over files to find all possible values..."
#IterateFiles(CreateValueSets)
#print "Iterating over files to find samples that had more than one region sequencing..."
IterateFiles(BuildSampleDictionaries)
#print "Found %d samples with more than one region" %len(SamplesWithMultipleRegions)
print "Sample\tRegions\tType"
PrintResults(3)
PrintResults(2)

