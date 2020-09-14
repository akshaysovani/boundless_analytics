# utility functions
# Author: Qiong Hu

from itertools import chain, combinations
import json
import math
import urllib2
import string
import os

# cartesian product: can use the product in itertools library?
# import itertools
# for element in itertools.product(*somelists):
#    print element
def cartesian_product(*X):
	if len(X) == 1: #special case, only X1
		return [ (x0,) for x0 in X[0] ]
	else:
		return [ (x0,)+t1 for x0 in X[0] for t1 in cartesian_product(*X[1:]) ]

def powerset(iterable):
	"""
	powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
	
	"""
	xs = list(iterable)
	# note we return an iterator rather than a list
	return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

def subsets(s):
	# base case
	if len(s) == 0:
		return [[]]
	# the input set is not empty, divide and conquer!
	h, t = s[0], s[1:]
	ss_excl_h = subsets(t)
	ss_incl_h = [([h] + ss) for ss in ss_excl_h]
	return ss_incl_h + ss_excl_h
	
def intersect(a, b):
	#return list(set(a) & set(b) )
        temp = set(b)
	return [val for val in a if val in temp]
	
def write_first_object(object, filepath):
	indentlen=2
	with open (filepath, mode="w") as file:
		json.dump([object], file, sort_keys=True, indent=indentlen)

def append_object(object, filepath):
	indentlen=2
	with open (filepath, mode="r+") as file:
		file.seek(0,2)
		position = file.tell() - 1
		file.seek(position)
		lines = (",\n{}\n]".format(json.dumps(object, sort_keys=True, indent=indentlen))).splitlines(True)
		padding = indentlen*' '
		for i in xrange(0, len(lines)):
			if i == 0 | i == len(lines) - 1:
				file.write(lines[len(lines)-1])	
			else:
				file.write(padding + lines[i])

def write_first_object_noindent(object, filepath):
	with open (filepath, mode="w") as file:
		json.dump([object], file, sort_keys=True)
                file.write("\n")

def append_object_noindent(object, filepath):
	with open (filepath, mode="r+") as file:
		file.seek(-2, 2)
		file.write(",\n{}]\n".format(json.dumps(object, sort_keys=True)))

def topK_score(frequenties):

	freqs = frequenties[:]
	n_bins = len(freqs)
	tau = 0.1
	
	if n_bins <= 3:
		k = 1
	elif n_bins <= 5:
		k = 2
	elif n_bins <= 10:
		k = 3
	elif n_bins <= 1000:
		k = 5
	else:
		k = int(n_bins*0.01)
		
	freqs.sort()
	minval = min(freqs)
	if minval < 0:
		freqs[:] = [x - minval for x in freqs]
	h_score = float(sum(freqs[n_bins-k:]))/sum(freqs[0:]) if sum(freqs[0:]) else 0
	
	if n_bins <= 1000:
		if h_score > float(k)/n_bins + tau:
			score = h_score
		else:
			score = 0
	elif n_bins > 1000 and h_score > 0.01: 
		score = min( 10*(h_score - 0.01), 1)
	else:
		score = h_score
		
	return score

def roundBinWidthToMostSignificantDigit(width):	
	assert width > 0
	width = float(width)
	factor = 1
	most_significant_bit = 0
	
	if width >= 1:
		while width > 10:
			width /= 10
			factor *= 10
			most_significant_bit += 1
		return [int(round(width))*factor, most_significant_bit]
	else:
		while width < 1:
			width *= 10
			factor *= 10
			most_significant_bit -= 1
		return [float(round(width))/factor, most_significant_bit]
		

def pretty_min(num, n):
	num = float(num)
	factor = math.pow(10, -n)
	num *= factor
	if n > 0:
		return int(math.floor(num))*math.pow(10, n)
	else:
		return float(math.floor(num))*math.pow(10, n)

def pretty_max(num, n):
	num = float(num)
	factor = math.pow(10, -n)
	num *= factor
	if n > 0:
		return int(math.ceil(num))*math.pow(10, n)
	else:
		return float(math.ceil(num))*math.pow(10, n)
		
def pretty_binning(data, nbins):
	x_min = min(data)
	x_max = max(data)			
	stepSize = (x_max - x_min)/nbins
	tick_begin = x_min + stepSize/2
	
	if x_min == x_max:
		return [[tick_begin], [x_min, x_max]]
	
	[stepSize, n] = roundBinWidthToMostSignificantDigit(stepSize)
	x_min = pretty_min(x_min, n)
	x_max = pretty_max(x_max, n)
	tick_begin = pretty_min(tick_begin, n)
	
	bins = []
	ticks = []
	bin = x_min
	tick = tick_begin
	if n >= 0:
		bins.append(int(bin))
		ticks.append(int(tick))
		while tick < x_max:
			bin += stepSize
			tick += stepSize
			bins.append(int(bin))
			ticks.append(int(tick))
		bin += stepSize
		bins.append(int(bin))
	else:
		nfactor = math.pow(10, -n)
		bin = int(bin*nfactor)
		tick = int(tick*nfactor)
		bins.append(float(bin)/nfactor)
		ticks.append(float(tick)/nfactor)
		xx_max = int(x_max*nfactor)
		stepSize = int(stepSize*nfactor)
		while tick < xx_max:
			bin += stepSize
			tick += stepSize
			bins.append(float(bin)/nfactor)
			ticks.append(float(tick)/nfactor)
		bin += stepSize
		bins.append(float(bin)/nfactor)
	
	return [ticks, bins]
