# Init Date: 2017/12/15
# Resume Date: 2017/12/29 - 2018/1/15
# Adapt ALPINE for vitually joined table: 5/7/2018
# Add: objectToURL: 5/8/2018
# Add: genChartObjsAcrossTables: 5/9/2018
# Author: Qiong Hu

import heapq
import math
import numpy as np
import pandas as pd
import operator  # operator.itemgetter(*b)(a)
from collections import Counter
from collections import Sequence

from Database import Database   # the Database class
import utilities as util        # self defined utilities functions

import json
import random
import base64 # for base64 encode
from sys import argv

class Itemset(object):
	"""
	The Itemset Class
	Each itemset is represented as a set of items along with its support
	"""

	def __init__(self, items = [], tidlist = [], sup = 0):
		assert(len(tidlist) == sup)
		self.items = items;
		self.tidlist = tidlist;
		self.sup = sup

	# sort the itemsets in decreasing support order
	def __cmp__(self, other):
		if self.sup > other.sup:
			return -1
		elif self.sup == other.sup:
			if len(self.items) > len(other.items):
				return -1
			elif len(self.items) == len(other.items):
				return cmp(self.items[-1], other.items[-1])
			else:
				return 1
		else:
			return 1

	def __str__(self):
		# return str(tuple(self.items)) + ":" + str(self.sup)
		return str(self.items) + ":" + str(self.sup)

class Fanalyzer(object):
	"""
	The Forever Analyzer Class
	The input database can contain multiple tables
	"""

	def __init__(self, db):
		"""Init the fanalyzer with a given database"""
		self.db = db     # database
		self.pq = []     # priority queue to hold the data slices in terms of itemsets
		self.dbName = self.db.schema['db']                     # database name
		self.outfile = "".join(("/home/ba/FAnalyzer/schemaData/chartsJSON/"+self.dbName, '_charts.json'))  # output chart objects file
		# self.outfile = "".join((self.dbName, '_charts_entity.json'))  # output chart objects file
		self.firstwrite = True                                 # flag to indicate the first chart object writing
		self.max_bars = 30
		self.url_prefix = "http://foreveranalytics.com/Render-Chart/"

	# def initPQ(self, tname):
		# """Init the priority queue from the items of a given table"""
		# tableData = self.db.data[tname]
		# itemNum = len(tableData['idm'])
		# abs_minsup = tableData['abs_minsup']
		# # print itemNum

		# for code in xrange(0, itemNum):
			# sup = self.db.getCodedItemSupport(tname, code)
			# if sup >= abs_minsup:
				# self.pq.append(Itemset([code], sup))

		# heapq.heapify(self.pq)
		# # while self.pq:
			# # print heapq.heappop(self.pq)

	def initPQ(self, tname):
		"""Init the priority queue from the whole dataset, no slice """
		nRecords = self.db.data[tname]['nRecords']
		heapq.heappush(self.pq, Itemset([], xrange(0, nRecords), nRecords))

        def getExceptions(self, tname):
                table = self.db.schema['tables'].get(tname)
                if table is None:
                        return {}
                exceptions = table.get('exceptions')
                if exceptions is None:
                        return {}
                return exceptions

        def getComparables(self, tname):
                table = self.db.schema['tables'].get(tname)
                if table is None:
                        return []
                comparables = table.get('comparable')
                if comparables is None:
                        return []
                return comparables

	def runAlpine(self, tname):
		"""run the ALPINE algorithm for one table"""
		# initialize the priority queue
		self.initPQ(tname)

		tableData = self.db.data[tname]
		idm = tableData['idm']
		itemCodes = tableData['itemCodes']
		nRecords = tableData['nRecords']
		itemNum = len(tableData['idm'])
		abs_minsup = tableData['abs_minsup']

		nSlices = 0

                exceptions = self.getExceptions(tname)
		print 'running ALPINE algorithm for table: ', tname, ' with absolute minsup: ', abs_minsup

		while self.pq:
			itemset = heapq.heappop(self.pq)
			# print itemset
			items = itemset.items
			tidlist = itemset.tidlist
			sup = itemset.sup

			nSlices += 1

			slice = []
			# tidlist = xrange(0, nRecords)     # tidlist of the itemset

			if len(items) == 0:
				for code in xrange(0, itemNum):
					key, val = idm[code]
					[newTidlist, newsup] = self.db.getCodedItemSupport(tname, code)
				        if newsup >= abs_minsup or key in exceptions:
						heapq.heappush(self.pq, Itemset([code], newTidlist, newsup))
			else:
				lastItem = items[-1]
				itmList = xrange(0, lastItem)  # possible extension items of the itemset
				for itm in items:
					key, val = idm[itm]
					slice.append((key, val))
					# tidlist = util.intersect(tidlist, tableData[key]['indexes'][val])
					itmList = list(set(itmList) - set(itemCodes[key]))  # not extend with different values from the same attribute

				# candidate generation
				for code in itmList:
					key, val = idm[code]
					# newTidlist = util.intersect(tidlist, tableData[key]['indexes'][val])
					[itmTidlist, itmSup] = self.db.getCodedItemSupport(tname, code)
					newTidlist = util.intersect(tidlist, itmTidlist)
					newsup = len(newTidlist)
				        if newsup >= abs_minsup:
						items.append(code)
						heapq.heappush(self.pq, Itemset(items, newTidlist, newsup))
						items = items[:-1]

				#print itemset, len(tidlist), slice, itmList

			print nSlices, slice, sup

			if tname == 'joined':
				self.genChartObjsAcrossTables(slice, tidlist)
			else:
				self.genChartObjs(slice, tidlist, tname)

		print 'number of slices: ', nSlices
		# self.genChartObjs([], xrange(3921), 'Players')

	def objectToURL(self, chart_object):

		plot_object = {}
		plot_object['workspace'] = False
		plot_object['hidden'] = False
		plot_object['favorite'] = False
		plot_object['dataset'] = chart_object['dataset']
		plot_object['score'] = chart_object['mark']
		plot_object['dimensions'] = chart_object['dimensions']
		plot_object['tags'] = {}
		plot_object['tags']['support'] = chart_object['support']
		for tkey, tval in chart_object['slice']:
			plot_object['tags'][tkey] = tval

		tname = chart_object['table']
		if tname == 'joined':
			tableMap = self.db.data['joined']['attrToTable']
			xTable = tableMap[chart_object['x']]
			if 'y' in chart_object.keys():
				yTable = tableMap[chart_object['y']]
		else:
			xTable = tname
			if 'y' in chart_object.keys():
				yTable = tname


		if chart_object['type'] == 'grouped-bargraph':
			plot_object['type'] = 'column-freq'
			plot_object['x'] = chart_object['x']
			categories = chart_object['categories']
			plot_object['xcategories'] = categories
			plot_object['data'] = map(lambda x,y:[x,y], categories, chart_object['data'])
		elif chart_object['type'] == 'bargraph':
			plot_object['type'] = 'column-freq'
			plot_object['x'] = chart_object['x']
			categories = self.db.data[xTable][chart_object['x']]['uniques']
			plot_object['xcategories'] = categories
			plot_object['data'] = map(lambda x,y:[x,y], categories, chart_object['data'])
		elif chart_object['type'] == 'heatmap':
			plot_object['type'] = chart_object['type']
			plot_object['x'] = chart_object['x']
			plot_object['y'] = chart_object['y']
			plot_object['xcategories'] = self.db.data[xTable][chart_object['x']]['uniques']
			plot_object['ycategories'] = self.db.data[yTable][chart_object['y']]['uniques']
			rows = range(len(plot_object['xcategories']))
			cols = range(len(plot_object['ycategories']))
			df = pd.DataFrame(index=rows, columns=cols)
			df = df.fillna(0)
			for x, y, val in chart_object['data']:
				df[y][x] = val
			chartdata = []
			for xidx in rows:
				for yidx in cols:
					chartdata.append([xidx, yidx, df[yidx][xidx]])
			plot_object['data'] = chartdata
			#print plot_object['data']
		elif chart_object['type'] == 'histogram':
			plot_object['type'] = chart_object['type']
			plot_object['x'] = chart_object['x']
			plot_object['data'] = chart_object['data']
		elif chart_object['type'] == 'scatter':
			plot_object['type'] = chart_object['type']
			plot_object['x'] = chart_object['x']
			plot_object['y'] = chart_object['y']
			plot_object['data'] = chart_object['data']
		elif chart_object['type'] == 'boxplot':
			plot_object['type'] = 'multi-cat-whisker'
			plot_object['x'] = chart_object['x']
			plot_object['y'] = chart_object['y']
			plot_object['xcategories'] = self.db.data[xTable][chart_object['x']]['uniques']
			datamap = {}
			for idx, minval, lowerquar, medianval, upperquar, maxval, meanval in chart_object['data']:
				datamap[idx] = [minval, lowerquar, medianval, upperquar, maxval]
			idxset = set(datamap.keys())
			plot_object['data'] = []
			for idx in range(len(plot_object['xcategories'])):
				if idx in idxset:
					plot_object['data'].append(datamap[idx])
				else:
					plot_object['data'].append([None]*5)

			# print plot_object['data']

		json_plot_data = json.dumps(plot_object)
		#print json_plot_data
		#base64_chart = json_plot_data.encode('base64')
		base64_chart =  base64.b64encode(json_plot_data)
		url = self.url_prefix + base64_chart

		# print url
		return url

	def genChartObjs(self, slice, tidlist, tname):
		"""generate all possible chart objects for a data slice"""
		# print 'generate chart objects for slice: ', slice

		dbSchema = self.db.schema
		dbName = dbSchema['db']

		tableData = self.db.data[tname]
		cat_fields_res = set(tableData['cat_fields'])
		num_fields = tableData['num_fields']
		nrecords = tableData['nRecords']
		primaryKey = tableData['pk']
                comparables = self.getComparables(tname)

		for key,val in slice:
			cat_fields_res.remove(key)

		if len(primaryKey) == 1 and primaryKey[0] in cat_fields_res:
			cat_fields_res.remove(primaryKey[0])

		cat_fields_res = list(cat_fields_res)
		supp = len(tidlist)
		supp = round(float(supp)/nrecords, 3)

		# 1-D bargraph of categorical features (or table if containing a lot of categories)
		for key in cat_fields_res:
                        vals = tableData[key]['values']
                        if not isinstance(vals, Sequence) or len(vals) == 0:
                                continue
			x_data = operator.itemgetter(*tidlist)(vals)
                        if not isinstance(x_data, Sequence):
                                x_data = [x_data]
                        # if len(x_data) == 0:
                        #         continue
			categories = tableData[key]['uniques']
			letter_counts = Counter(x_data)
			counts = []
			cnt = 0
			for val in categories:
				freq = letter_counts[val]
				counts.append(freq)
				if freq > 0:
					cnt += 1
			        if cnt == 0:
				        continue

			chart_object = {}
			chart_object['dataset'] = dbName
			chart_object['table'] = tname
			chart_object['x'] = key
			chart_object['plottype'] = key
			chart_object['type'] = 'bargraph'
			chart_object['slice'] = slice
			# chart_object['categories'] = categories
			chart_object['data'] = counts     # vector representation
			score = util.topK_score(counts)
			chart_object['mark'] = round(score, 3)
			chart_object['dimensions'] = 1
			chart_object['support'] = supp
			# print chart_object

			if len(categories) <= self.max_bars:
				chart_object['url'] = self.objectToURL(chart_object)

			# self.pretty_write(chart_object, self.outfile)
			self.oridinary_write(chart_object, self.outfile)

		# 1-D group-by bargraphs of categorical features (or table if containing a lot of categories)
        #         print "Comp: ", comparables
		for key in cat_fields_res:
			categories = tableData[key]['uniques']
                        # print "Cats: ", categories
                        if not isinstance(categories, Sequence) or len(categories) == 0:
                                continue
                        avgs = []
                        labels = []
                        maxAvg = 0.0
                        for compareSet in comparables:
                                for compare in compareSet:
			                for val in categories:
                                                [newList, newSupport] = self.db.getUncodedItemSupport(tname, key, val)
                                                subResult = util.intersect(tidlist, newList)
			                        theData = operator.itemgetter(*subResult)(tableData[compare]['values'])
                                                if not isinstance(theData, Sequence):
                                                        theData = [theData]
                                                labels.append(compare + "-" + val)
				                avg = np.mean(theData)
				                avgs.append(avg)
                                        maxAvg = max(maxAvg, util.topK_score(avgs[-2:]))
                        if len(avgs) > 0  and len(labels) > 0:
			        chart_object = {}
			        chart_object['dataset'] = dbName
			        chart_object['table'] = tname
			        chart_object['x'] = key
			        chart_object['plottype'] = key
			        chart_object['type'] = 'grouped-bargraph'
			        chart_object['slice'] = slice
			        chart_object['categories'] = labels
			        chart_object['data'] = avgs     # vector representation
			        score = maxAvg
			        chart_object['mark'] = round(score, 3)
			        chart_object['dimensions'] = 1
			        chart_object['support'] = supp

			        if len(categories) <= self.max_bars:
				        chart_object['url'] = self.objectToURL(chart_object)

			        # print chart_object
			        # self.pretty_write(chart_object, self.outfile)
			        self.oridinary_write(chart_object, self.outfile)

		# 2-D heatmap of two categorical features
		ncat = len(cat_fields_res)
		for iidx in xrange(0, ncat - 1):
                        vals = tableData[cat_fields_res[iidx]]['values']
                        if not isinstance(vals, Sequence) or len(vals) == 0:
                                continue
			x_data = operator.itemgetter(*tidlist)(vals)
                        if not isinstance(x_data, Sequence) or len(x_data) == 0:
                                continue
			for jidx in xrange(iidx+1, ncat):
                                vals = tableData[cat_fields_res[jidx]]['values']
                                if not isinstance(vals, Sequence) or len(vals) == 0:
                                        continue
				y_data = operator.itemgetter(*tidlist)(vals)
                                if not isinstance(y_data, Sequence) or len(y_data) == 0:
                                        continue
				pairs = zip(x_data, y_data)
				letter_counts = Counter(pairs)
				xcategories = tableData[cat_fields_res[iidx]]['uniques']
				ycategories = tableData[cat_fields_res[jidx]]['uniques']
				counts = []
				chartdata = []
				for xidx in xrange(0, len(xcategories)):
					for yidx in xrange(0, len(ycategories)):
						cnt = letter_counts[(xcategories[xidx], ycategories[yidx])]
						counts.append(cnt)
						if cnt != 0:
							chartdata.append([xidx, yidx, cnt])
				if len(chartdata) == 0:
					continue
				chart_object = {}
				chart_object['dataset'] = dbName
				chart_object['table'] = tname
				chart_object['x'] = cat_fields_res[iidx]
				chart_object['y'] = cat_fields_res[jidx]
				chart_object['plottype'] = ''.join([cat_fields_res[iidx], '-', cat_fields_res[jidx]])
				chart_object['type'] = 'heatmap'
				chart_object['slice'] = slice
				# chart_object['xcategories'] = xcategories
				# chart_object['ycategories'] = ycategories
				chart_object['data'] = chartdata  # sparse representation: [xidx, yidx, cnt]
				score = util.topK_score(counts)
				chart_object['mark'] = round(score, 3)
				chart_object['dimensions'] = 2
				chart_object['support'] = supp
				# print chart_object

				if len(xcategories) <= self.max_bars and len(ycategories) <= self.max_bars:
					chart_object['url'] = self.objectToURL(chart_object)

				# self.pretty_write(chart_object, self.outfile)
				self.oridinary_write(chart_object, self.outfile)

		# 1-D histogram of numerical features with pretty binning
		for key in num_fields:
                        vals = tableData[key]['values']
                        if not isinstance(vals, Sequence) or len(vals) == 0:
                                continue
			x_data = operator.itemgetter(*tidlist)(vals)
                        if not isinstance(x_data, Sequence) or len(x_data) == 0:
                                continue
			# x_data = [value for value in x_data if not np.isnan(value)]        # remove "nan" elements
			# works both for lists and numpy arrays since v != v only for NaN (an array of objects with mixed types, like strings and nans, also works)
			x_data = filter(lambda v: v==v, x_data)

                        # check how many unique values.
                        x_data_unique = set(x_data)
                        n_data = len(x_data_unique)
			# n_data = len(x_data)
			if n_data == 0:
				continue

			n_bins = math.ceil(math.sqrt(n_data))

			[ticks, bins] = util.pretty_binning(x_data, n_bins)
			[freqs, bins] = np.histogram(x_data, bins)
			freqs = list(freqs)

			chart_object = {}
			chart_object['dataset'] = dbName
			chart_object['table'] = tname
			chart_object['x'] = key
			chart_object['plottype'] = key
			chart_object['type'] = 'histogram'
			chart_object['slice'] = slice
			# chart_object['ticks'] = ticks
			# chart_object['data'] = freqs       # vector representation
			chart_object['data'] = map(lambda x,y:[x,y], ticks, freqs)
                        if n_bins == 1:
                            # made 0.99 instead of 1, because we are only displaying charts with score < 1 at the moment.
                            score = 0.999
                        else:
                            score = util.topK_score(freqs)
			chart_object['mark'] = round(score, 3)
			chart_object['dimensions'] = 1
			chart_object['support'] = supp
			chart_object['url'] = self.objectToURL(chart_object)
			# self.pretty_write(chart_object, self.outfile)
			self.oridinary_write(chart_object, self.outfile)

		# 2-D scatter plot of two numerical features
		nnum = len(num_fields)
		for iidx in xrange(0, nnum - 1):
                        vals = tableData[num_fields[iidx]]['values']
                        if not isinstance(vals, Sequence) or len(vals) == 0:
                                continue
			x_data = operator.itemgetter(*tidlist)(vals)
                        if not isinstance(x_data, Sequence) or len(x_data) == 0:
                                continue
			for jidx in xrange(iidx+1, nnum):
                                vals = tableData[num_fields[jidx]]['values']
                                if len(vals) == 0:
                                        continue
				y_data = operator.itemgetter(*tidlist)(vals)
                                if not isinstance(y_data, Sequence) or len(y_data) == 0:
                                        continue
				df = pd.DataFrame({'x': x_data, 'y': y_data})
				coeff = df['x'].corr(df['y'])
				if coeff != coeff:  # nan
					continue
				chart_object = {}
				chart_object['dataset'] = dbName
				chart_object['table'] = tname
				chart_object['x'] = num_fields[iidx]
				chart_object['y'] = num_fields[jidx]
				chart_object['plottype'] = ''.join([num_fields[iidx], '-', num_fields[jidx]])
				chart_object['type'] = 'scatter'
				chart_object['slice'] = slice
				sample_size = 100
				if len(x_data) > sample_size:
					rand_smpl = random.sample(xrange(len(x_data)), sample_size)
				else:
					rand_smpl = xrange(len(x_data))
				chart_object['data'] = [(x_data[i], y_data[i]) for i in rand_smpl if x_data[i] == x_data[i] and y_data[i] == y_data[i]]   # list of points in (xcoordinate, yxcoordinate)
				chart_object['mark'] = round(abs(coeff), 3)
				chart_object['dimensions'] = 2
				chart_object['support'] = supp
				chart_object['url'] = self.objectToURL(chart_object)
				# self.pretty_write(chart_object, self.outfile)
				self.oridinary_write(chart_object, self.outfile)

		# side-by-side boxplots of numerical features over categorical features
		for xkey in cat_fields_res:
			for ykey in num_fields:
				boxdata = []
				cnt = 0
				nCategories = len(tableData[xkey]['uniques'])
				for idx in xrange(0, nCategories):
					val = tableData[xkey]['uniques'][idx]
					if len(tidlist) == nrecords:
						tidlistforval = tableData[xkey]['indexes'][val]
					else:
						tidlistforval = util.intersect(tidlist, tableData[xkey]['indexes'][val])
					if len(tidlistforval) > 0:
						y_data = operator.itemgetter(*tidlistforval)(tableData[ykey]['values'])
						if not isinstance(y_data, Sequence):
							y_data = [y_data]
						y_data = filter(lambda v: v==v, y_data)  # filter out NaN values
						if len(y_data) > 0:
							cnt += 1
							minval = np.min(y_data)
							lowerquar = np.percentile(y_data, 25)
							medianval = np.median(y_data)
							upperquar = np.percentile(y_data, 75)
							maxval = np.max(y_data)
							meanval = np.mean(y_data)
							# boxdata.append([minval, lowerquar, medianval, upperquar, maxval])
							# boxdata.append(["{0:.2f}".format(minval), "{0:.2f}".format(lowerquar), "{0:.2f}".format(medianval), "{0:.2f}".format(upperquar), "{0:.2f}".format(maxval)])
							boxdata.append([idx, round(minval, 2), round(lowerquar, 2), round(medianval, 2), round(upperquar, 2), round(maxval, 2), round(meanval, 2)])   # sparse reprentaton: [idx, minval, lowerquar, medianval, upperquar, maxval, meanval]

				if cnt > 0:
					chart_object = {}
					chart_object['dataset'] = dbName
					chart_object['table'] = tname
					chart_object['x'] = xkey
					chart_object['y'] = ykey
					chart_object['plottype'] = ''.join([xkey, '-', ykey])
					chart_object['type'] = 'boxplot'
					chart_object['slice'] = slice
					# chart_object['categories'] = data[xkey]['uniques']
					chart_object['data'] = boxdata

					# calculate the mark
					if cnt > 1:
						meds = []
						for stats in boxdata:
							med = stats[3]
							meds.append(med)
						chart_object['mark'] = round(util.topK_score(meds), 3)
					elif cnt == 1:
						idx = boxdata[0][0]
						val = tableData[xkey]['uniques'][idx]
						if len(tidlist) == nrecords:
							tidlistforval = tableData[xkey]['indexes'][val]
						else:
							tidlistforval = util.intersect(tidlist, tableData[xkey]['indexes'][val])
						y_data = operator.itemgetter(*tidlistforval)(tableData[ykey]['values'])
						if not isinstance(y_data, Sequence):
							y_data = [y_data]
						y_data = filter(lambda v: v==v, y_data)
						n_data = len(y_data)
						n_bins = math.ceil(math.sqrt(n_data))
						[ticks, bins] = util.pretty_binning(y_data, n_bins)
						[freqs, bins] = np.histogram(y_data, bins)
						freqs = list(freqs)
						chart_object['mark'] = round(util.topK_score(freqs), 3)
					else:
						chart_object['mark'] = 0.000

					chart_object['dimensions'] = 2
					chart_object['support'] = supp

					if nCategories <= self.max_bars:
						chart_object['url'] = self.objectToURL(chart_object)

					# self.pretty_write(chart_object, self.outfile)
					self.oridinary_write(chart_object, self.outfile)

	def chartObject(self, slice, tidlist, firstAttr, secondAttr, support):
		""" generate the chart objects for two attributes: firstAttr, secondAttr across tables """
		# print firstAttr, secondAttr

		dbSchema = self.db.schema
		data = self.db.data
		dbName = dbSchema['db']
		tableMap = self.db.data['joined']['attrToTable']
		tableOne = tableMap[firstAttr]
		firstAttrType = dbSchema['tables'][tableOne]['attrTypes'][firstAttr]
		tableTwo = tableMap[secondAttr]
		secondAttrType = dbSchema['tables'][tableTwo]['attrTypes'][secondAttr]
		nrecords = data['joined']['nRecords']

		chart_object = {}
		chart_object['dataset'] = dbName
		chart_object['table'] = 'joined'
		chart_object['x'] = firstAttr
		chart_object['y'] = secondAttr
		chart_object['plottype'] = ''.join([firstAttr, '-', secondAttr])
		chart_object['slice'] = slice
		chart_object['dimensions'] = 2
		chart_object['support'] = support

		if firstAttrType == 'cat' and secondAttrType == 'cat':
			chart_object['type'] = 'heatmap'
			x_data = operator.itemgetter(*tidlist)(data[tableOne][firstAttr]['values'])
			y_data = operator.itemgetter(*tidlist)(data[tableTwo][secondAttr]['values'])
			pairs = zip(x_data, y_data)
			letter_counts = Counter(pairs)
			xcategories = data[tableOne][firstAttr]['uniques']
			ycategories = data[tableTwo][secondAttr]['uniques']
			counts = []
			chartdata = []
			for xidx in xrange(0, len(xcategories)):
				for yidx in xrange(0, len(ycategories)):
					cnt = letter_counts[(xcategories[xidx], ycategories[yidx])]
					counts.append(cnt)
					if cnt != 0:
						chartdata.append([xidx, yidx, cnt])
			if len(chartdata) == 0:
				return
			chart_object['data'] = chartdata
			score = util.topK_score(counts)
			chart_object['mark'] = round(score, 3)
			if len(xcategories) <= self.max_bars and len(ycategories) <= self.max_bars:
				chart_object['url'] = self.objectToURL(chart_object)
			self.oridinary_write(chart_object, self.outfile)
		elif firstAttrType == 'num' and secondAttrType == 'num':
			chart_object['type'] = 'scatter'
			x_data = operator.itemgetter(*tidlist)(data[tableOne][firstAttr]['values'])
			y_data = operator.itemgetter(*tidlist)(data[tableTwo][secondAttr]['values'])
			df = pd.DataFrame({'x': x_data, 'y': y_data})
			coeff = df['x'].corr(df['y'])
			if coeff != coeff:  # nan
				return
			sample_size = 100
			if len(x_data) > sample_size:
				rand_smpl = random.sample(xrange(len(x_data)), sample_size)
			else:
				rand_smpl = xrange(len(x_data))
			# list of points in (xcoordinate, yxcoordinate)
			chart_object['data'] = [(x_data[i], y_data[i]) for i in rand_smpl if x_data[i] == x_data[i] and y_data[i] == y_data[i]]
			# df = pd.DataFrame({'x': x_data, 'y': y_data})
			# coeff = df['x'].corr(df['y'])
			chart_object['mark'] = round(coeff*coeff, 3)
			chart_object['url'] = self.objectToURL(chart_object)
			self.oridinary_write(chart_object, self.outfile)
		else:
			if secondAttrType == 'cat':
				# switch when the second attr is categorical (the first attr is not)
				tmpAttr = firstAttr
				firstAttr = secondAttr
				secondAttr = tmpAttr
				tmpTable = tableOne
				tableOne = tableTwo
				tableTwo = tmpTable
				chart_object['x'] = firstAttr
				chart_object['y'] = secondAttr
				chart_object['plottype'] = ''.join([firstAttr, '-', secondAttr])

			chart_object['type'] = 'boxplot'
			boxdata = []
			cnt = 0
			nCategories = len(data[tableOne][firstAttr]['uniques'])
			for idx in xrange(0, nCategories):
				val = data[tableOne][firstAttr]['uniques'][idx]
				if len(tidlist) == nrecords:
					tidlistforval = data[tableOne][firstAttr]['indexes'][val]
				else:
					tidlistforval = util.intersect(tidlist, data[tableOne][firstAttr]['indexes'][val])
				if len(tidlistforval) > 0:
					y_data = operator.itemgetter(*tidlistforval)(data[tableTwo][secondAttr]['values'])
					if not isinstance(y_data, Sequence):
						y_data = [y_data]
					y_data = filter(lambda v: v==v, y_data)  # filter out NaN values
					if len(y_data) > 0:
						cnt += 1
						minval = np.min(y_data)
						lowerquar = np.percentile(y_data, 25)
						medianval = np.median(y_data)
						upperquar = np.percentile(y_data, 75)
						maxval = np.max(y_data)
						meanval = np.mean(y_data)
						# boxdata.append([minval, lowerquar, medianval, upperquar, maxval])
						# boxdata.append(["{0:.2f}".format(minval), "{0:.2f}".format(lowerquar), "{0:.2f}".format(medianval), "{0:.2f}".format(upperquar), "{0:.2f}".format(maxval)])
						boxdata.append([idx, round(minval, 2), round(lowerquar, 2), round(medianval, 2), round(upperquar, 2), round(maxval, 2), round(meanval, 2)])   # sparse reprentaton: [idx, minval, lowerquar, medianval, upperquar, maxval, meanval]

			if cnt > 0:
				chart_object['data'] = boxdata

				# calculate the mark
				if cnt > 1:
					meds = []
					for stats in boxdata:
						med = stats[3]
						meds.append(med)
					chart_object['mark'] = round(util.topK_score(meds), 3)
				elif cnt == 1:
					idx = boxdata[0][0]
					val = data[tableOne][firstAttr]['uniques'][idx]
					if len(tidlist) == nrecords:
						tidlistforval = data[tableOne][firstAttr]['indexes'][val]
					else:
						tidlistforval = util.intersect(tidlist, data[tableOne][firstAttr]['indexes'][val])
					y_data = operator.itemgetter(*tidlistforval)(data[tableTwo][secondAttr]['values'])
					if not isinstance(y_data, Sequence):
						y_data = [y_data]
					y_data = filter(lambda v: v==v, y_data)
					n_data = len(y_data)
					n_bins = math.ceil(math.sqrt(n_data))
					[ticks, bins] = util.pretty_binning(y_data, n_bins)
					[freqs, bins] = np.histogram(y_data, bins)
					freqs = list(freqs)
					chart_object['mark'] = round(util.topK_score(freqs), 3)
				else:
					chart_object['mark'] = 0.000

				if nCategories <= self.max_bars:
					chart_object['url'] = self.objectToURL(chart_object)
				self.oridinary_write(chart_object, self.outfile)

		# print chart_object
		# self.pretty_write(chart_object, self.outfile)
		# self.oridinary_write(chart_object, self.outfile)

	def genChartObjsAcrossTables(self, slice, tidlist):
		""" Generate chart objects across multiple tables """

		dbSchema = self.db.schema
		relationTable = dbSchema['relationTable'][0]
		attrInRelation = dbSchema['tables'][relationTable]['attributes']
		entityTables = dbSchema['entityTables']
		nrecords = self.db.data[relationTable]['nRecords']

		supp = len(tidlist)
		supp = round(float(supp)/nrecords, 3)

		dimensions = set()
		for key,val in slice:
			dimensions.add(key)

		# relation table with entity tables
		for eTable in entityTables:
			# print relationTable, eTable
			attrSetOne = set(attrInRelation)
			attrSetOne -= dimensions
			attrSetOne -= set(dbSchema['tables'][eTable]['pk'])
			attrSetOne = list(attrSetOne)

			attrSetTwo = set(dbSchema['tables'][eTable]['attributes'])
			attrSetTwo -= dimensions
			attrSetTwo -= set(dbSchema['tables'][eTable]['pk'])
			attrSetTwo = list(attrSetTwo)

			# print "attrSetOne: ", attrSetOne
			# print "attrSetTwo: ", attrSetTwo

			for first in attrSetOne:
				for second in attrSetTwo:
					# print first, second
					self.chartObject(slice, tidlist, first, second, supp)

		# among the entity tables
		tnum = len(entityTables)
		for iidx in xrange(0, tnum - 1):
			TableOne = entityTables[iidx]
			for jidx in xrange(iidx+1, tnum):
				TableTwo = entityTables[jidx]

				# print TableOne, TableTwo
				attrSetOne = set(dbSchema['tables'][TableOne]['attributes'])
				attrSetOne -= dimensions
				attrSetOne -= set(dbSchema['tables'][TableOne]['pk'])
				attrSetOne = list(attrSetOne)

				attrSetTwo = set(dbSchema['tables'][TableTwo]['attributes'])
				attrSetOne -= dimensions
				attrSetTwo -= set(dbSchema['tables'][TableTwo]['pk'])
				attrSetTwo = list(attrSetTwo)

				# print "attrSetOne: ", attrSetOne
				# print "attrSetTwo: ", attrSetTwo

				for first in attrSetOne:
					for second in attrSetTwo:
						# print first, second
						self.chartObject(slice, tidlist, first, second, supp)

	def pretty_write(self, object, filepath):
		if self.firstwrite:
			self.firstwrite=False
			util.write_first_object(object, filepath)
		else:
			util.append_object(object, filepath)

	def oridinary_write(self, object, filepath):
		if self.firstwrite:
			self.firstwrite=False
			util.write_first_object_noindent(object, filepath)
		else:
			util.append_object_noindent(object, filepath)

def main():
	# minsup = 1

	scriptname, filename, minsup = argv
	db = Database(filename)
	db.loadDBforALPINE(minsup)

	fa = Fanalyzer(db)

	tables = db.schema['tablenames']

	for tname in tables:
		fa.runAlpine(tname)

main()
