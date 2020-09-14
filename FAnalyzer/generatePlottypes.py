# calculate the meta gini for plottypes and save the plottypes

import requests
import math
import numpy as np
import utilities as util
import json
import base64 # for base64 encode

chartCore = 'tcharts'

solrRoot = 'http://foreveranalytics.com:8983/solr'
solrSuffix = '&wt=json'
url_prefix = "http://foreveranalytics.com/Render-Chart/"

def getPlotTypes(dataset, corename):
	queryStr = ''.join([solrRoot, '/', corename, '/select?q=*%3A*&fq=dataset%3A', dataset, '&rows=0&facet=true&facet.field=plottype&facet.limit=-1', solrSuffix])
	queryResults = requests.get(queryStr).json()['facet_counts']['facet_fields']['plottype']
	types = queryResults[0:][::2]
	numofCharts = queryResults[1:][::2]
	plotTypes = []
	for type, num in zip(types, numofCharts):
		if num >= 1:
			#print str(type), num
			plotTypes.append([str(type), num])
	return plotTypes

def getPlotTypeObj(plottype, dataset, corename):
	# print plottype, dataset, corename

	typename = plottype[0]

	# special processing for %
	typenameinstr = typename.replace('%', '%25')
	queryStr = ''.join([solrRoot, '/', corename, '/select?q=*%3A*&fq=%2Bdataset%3A', dataset, '+%2Bplottype%3A', typenameinstr])

	print queryStr

	nplots = plottype[1]
	npages = math.ceil(float(nplots)/10)
	npages = int(npages)

	# create a plot type object
	plottype_object = {}
	plottype_object['type'] = None

	scores = []
	for page in range(0, npages):
		start = page*10
		query = ''.join([queryStr, '&start=', str(start), solrSuffix])
		plots = requests.get(query).json()['response']['docs']
		for plot in plots:
			if plottype_object['type'] is None:
				plottype_object['type'] = plot['type']
			scores.append(plot['mark'])

	var = np.var(scores)

	n_pts = len(scores)
	n_bins = math.ceil(math.sqrt(n_pts))
	[ticks, bins] = util.pretty_binning(scores, n_bins)
	[freqs, bins] = np.histogram(scores, bins)
	freqs = list(freqs)
	metagini = util.topK_score(freqs)

	plottype_object['dataset'] = dataset
	plottype_object['plottype'] = typename
	pos = typename.find('-')
	if pos == -1:
		plottype_object['x'] = typename
	else:
		plottype_object['x'] = typename[0 : pos]
		plottype_object['y'] = typename[pos + 1 : len(typename)]
	plottype_object['nplots'] = nplots
	plottype_object['variance'] = round(var, 3)
	plottype_object['metagini'] = round(metagini, 3)

	minval = np.min(scores)
	lowerquar = np.percentile(scores, 25)
	medianval = np.median(scores)
	upperquar = np.percentile(scores, 75)
	maxval = np.max(scores)
	plottype_object['stats'] = [round(minval, 2), round(lowerquar, 2), round(medianval, 2), round(upperquar, 2), round(maxval, 2)]

	plot_object = {}
	plot_object['workspace'] = False
	plot_object['hidden'] = False
	plot_object['favorite'] = False
	plot_object['dataset'] = dataset
	plot_object['type'] = 'histogram'
	plot_object['score'] = plottype_object['metagini']
	plot_object['data'] = map(lambda x,y:[x,y], ticks, freqs)
	plot_object['x'] = 'mark'
	plot_object['dimensions'] = 1
	plot_object['tags'] = {}
	json_plot_data = json.dumps(plot_object)
	base64_chart =  base64.b64encode(json_plot_data)
	url = url_prefix + base64_chart

	plottype_object['url'] = url

	return plottype_object

#datasets = ['NBAPlayers']
#datasets = ['wine']
datasets = ['moody']
for dataset in datasets:
	firstwrite = True
	outputfile = ''.join([dataset, '_plottypes.json'])

	# generate the plot type objects
	plottypes = getPlotTypes(dataset, chartCore)
	print(plottypes)
        print len(plottypes)
	for plottype in plottypes:
		# print plottype
		plottype_object = getPlotTypeObj(plottype, dataset, chartCore)
		if firstwrite:
			firstwrite=False
			util.write_first_object_noindent(plottype_object, outputfile)
		else:
			util.append_object_noindent(plottype_object, outputfile)
