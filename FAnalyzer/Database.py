# Define the database class
# Date: 2017/12/11-14
# Add virtualJoin and jointItemRecode: 5/7/2018
# Author: Qiong Hu

import json
import os.path
import csv  # csv reader
import ast  # eval
import numpy as np
import math
import itertools

class Item(object):
	"""
	The Item class
	Each item is represented as a <key, value> pair, as each attribute can have multiple categories
	The support of each item is also kept to define the preorder among those items
	"""

	def __init__(self, keyval = (), sup = 0):
		self.keyval = keyval
		self.sup = sup

	# sort the items in decreasing support order
	def __cmp__(self, other):
		return -cmp(self.sup, other.sup)

	def __str__(self):
		return str(self.keyval) + ":" + str(self.sup)

class Database(object):
	"""
	The Database class
	Define all the operations and preprocessing functions of a database
	"""

	def __init__(self, schemaFile):
		"""Init a database by specify its schemaFile"""

		self.schemaFile = schemaFile  # name of the db schema file
		self.schema = None            # db schema
		self.data = {}                # data

	def loadDBSchema(self):
		"""load the database schema from the schemaFile"""

		print 'loading database schema: ', self.schemaFile
		with open(self.schemaFile) as json_file:
			self.schema = json.load(json_file)
		json_file.close()
		assert(self.schema['nTables'] == len(self.schema['tablenames']))
		# print(self.schema)

	def loadData(self, tname):
		"""load data from .csv file for a table"""

		fname = "".join(("/home/ba/FAnalyzer/schemaData/data/"+tname, '.csv'))
		print 'loading table: ', fname
		assert(os.path.isfile(fname))
		with open(fname, 'rb') as csvfile:
			datareader = csv.reader(csvfile, delimiter=',')
			headers = datareader.next()
			# print headers
                        # print self.schema['tables'][tname]['attributes']
			assert(headers == self.schema['tables'][tname]['attributes'])
			columns = list(zip(*datareader))
		csvfile.close()

		table = {}
		table['attributes'] = headers
		table['nAttributes'] = len(headers)
		table['nRecords'] = len(columns[0])
		table['pk'] = self.schema['tables'][tname]['pk']
		if 'fk' in self.schema['tables'][tname].keys():
			table['fk'] = self.schema['tables'][tname]['fk']
		table['num_fields'] = []
		table['cat_fields'] = []
		table['cat_categories'] = []
		table['timeseries_fields'] = []
                for idx in xrange(0, len(headers)):
			column = {}
			attr = headers[idx]
                        #print ("Attr is: ",attr)
			column['index'] = idx
			column['type'] = self.schema['tables'][tname]['attrTypes'][attr]
			if column['type'] == 'num':
                                print ("Numerical Attr is: ",attr)
				table['num_fields'].append(attr)
				column['values'] = [ast.literal_eval(v) if v else np.nan for v in columns[idx]]
			elif column['type'] == 'cat':
				table['cat_fields'].append(attr)
				column['values'] = [v if v else np.nan for v in columns[idx]]
				uniques = reduce(lambda l, v: l if v in l else l+[v], column['values'], [])
				uniques.sort()
				column['uniques'] = [x for x in uniques if str(x) != 'nan']
				table['cat_categories'].append(len(column['uniques']))
				indexes = {}
				for v in column['uniques']:
					indexes[v] = [i for i,x in enumerate(column['values']) if x == v]
				column['indexes'] = indexes
		        else:
                                table['timeseries_fields'].append(attr)
                                print ("Timeseries Attr is: ",attr)
                                #column['values'] = [ast.literal_eval(v) if v else np.nan for v in columns[idx]]
                        table[attr] = column

		# print table
		self.data[tname] = table

        def getExceptions(self, tname):
                table = self.schema['tables'].get(tname)
                if table is None:
                        return {}
                exceptions = table.get('exceptions')
                if exceptions is None:
                        return {}
                return exceptions

	def itemRecode(self, tname, minsup):
		"""Recode each item in a table: a (key, value) pair based on their support"""
		"""Only those items with support greater than or equal to minsup are kept"""

		print 'recoding items in table: ', tname
		tableData = self.data[tname]
		nrecords = tableData['nRecords']

		# calculate the absolute support count
		print("nrecords",nrecords)
                abs_minsup = math.ceil(float(minsup)/100*nrecords)
		self.data[tname]['abs_minsup'] = abs_minsup

                exceptions = self.getExceptions(tname)

		items = []
		for key in tableData['cat_fields']:
			for val in tableData[key]['uniques']:
				sup = len(tableData[key]['indexes'][val])
                                print ("key :",key)
                                print ("val :",val)
                                print ("sup :",sup)
                                print ("abs_minsup :",abs_minsup)
                                if sup >= abs_minsup or key in exceptions:
					items.append(Item((key, val), sup))
                                        print 'Including: ', key, ' = ', val
                                else:
                                        print 'Excluding: ', key, ' = ', val

		items.sort()

		# for item in items:
			# print item

		idm = {}          # item decode map
		itemCodes = {}    # item codes for each attribute
		for idx in xrange(0, len(items)):
			idm[idx] = items[idx].keyval
			key, value = items[idx].keyval
			if key in itemCodes.keys():
				itemCodes[key].append(idx)
			else:
				itemCodes[key] = [idx]

		# print idm
		# print itemCodes
		self.data[tname]['idm'] = idm
		self.data[tname]['itemCodes'] = itemCodes

        def getUncodedItemSupport(self, tname, key, val):
		""" Get the support of each uncoded item """
		# map to the actual table name from the vitually joined table
		if tname == 'joined':
			tname = self.data[tname]['attrToTable'][key]

		tidlist = self.data[tname][key]['indexes'][val]
		sup = len(tidlist)
		return [tidlist, sup]

	def getCodedItemSupport(self, tname, code):
		""" Get the support of each coded item """
		key, val = self.data[tname]['idm'][code]

		# map to the actual table name from the vitually joined table
		if tname == 'joined':
			tname = self.data[tname]['attrToTable'][key]

		tidlist = self.data[tname][key]['indexes'][val]
		sup = len(tidlist)
		return [tidlist, sup]

	def loadDB(self):
		""" Load the database """
		# load the db schema
		self.loadDBSchema()

		# load each table from .csv file
		for tname in self.schema['tablenames']:
		# for tname in ['Players']:
			self.loadData(tname)

	def loadDBforALPINE(self, minsup):
		""" Load the database with a specified minimum support """
		""" recode the frequent items based on their support """

		# load the database
		self.loadDBSchema()

		# load each table from .csv file and recode the items based on their support
		for tname in self.schema['tablenames']:
		# for tname in ['Players']:
			self.loadData(tname)
			self.itemRecode(tname, minsup)

	def virtualJoin(self):
		""" Virtually join the tables in the star-schema without materializing it """
		""" The connection among the tables is established through the foreign key reference """

		print 'virtually join the tables'

		relationTableName = self.schema['relationTable'][0]
		relationTable = self.data[relationTableName]
		nRecords = relationTable['nRecords']

		self.data['joined'] = {}
		self.data['joined']['nRecords'] = nRecords

		# map from attr to table
		attrToTable = {}
		for attr in relationTable['attributes']:
			attrToTable[attr] = relationTableName

		# print nRecords

		for fkref in relationTable['fk']:
			entityTable = fkref['refTable']
			entityKey = fkref['key'][0]
			columnR = relationTable[entityKey]
			# print entityTable, entityKey
			# print column

			tableSchema = self.schema['tables'][entityTable]
			tableData = self.data[entityTable]
			keyvals = tableData[entityKey]['values']
			# print keyvals

			# modify the entityTable to do the virtual join
			for attr in tableSchema['attributes']:
				# print attr, tableSchema['attrTypes'][attr]
				type = tableSchema['attrTypes'][attr]
				column = tableData[attr]
				# print attr, type

				if type == 'cat':
					for v in column['uniques']:
						old_indexes = column['indexes'][v]
						# 2018-07-09  filter: some player not occurs in stats, add a filter
						old_indexes = [x for x in old_indexes if keyvals[x] in columnR['indexes'].keys()]
						list2d = [columnR['indexes'][keyvals[i]] for i in old_indexes]
						flat = list(itertools.chain.from_iterable(list2d))
						column['indexes'][v] = flat
						# print v
						# print old_indexes
						# print flat
						# print attr, v, column['indexes'][v]
						# print attr, v, len(flat)

				old_values = column['values']
				new_values = [None for x in range(nRecords)]
				for i, val in enumerate(old_values):
					# add the test to avoid key error
					if keyvals[i] in columnR['indexes'].keys():
						for ind in columnR['indexes'][keyvals[i]]:
							new_values[ind] = val
				column['values'] = new_values
				# print attr, column['values']
				# print attr, len(new_values)

				if attr not in attrToTable.keys():
					attrToTable[attr] = entityTable

		self.data['joined']['attrToTable'] = attrToTable


	def jointItemRecode(self, minsup):
		""" Recode items in the virtually joined table """

		print 'recoding items for the virtually joint table'

		relationTableName = self.schema['relationTable'][0]
		relationTable = self.data[relationTableName]
		nRecords = relationTable['nRecords']

		# get the absolute support count
		abs_minsup = math.ceil(float(minsup)/100*nRecords)
		self.data['joined']['abs_minsup'] = abs_minsup

		# to modify: might have duplicates: like Player occurrs in both Players and SeasonsStats
		# items = []
		# for tname in self.schema['tablenames']:
			# tableData = self.data[tname]
			# for key in tableData['cat_fields']:
				# for val in tableData[key]['uniques']:
					# sup = len(tableData[key]['indexes'][val])
					# if sup >= abs_minsup:
						# items.append(Item((key, val), sup))
		# items.sort()

		items = []
		tableMap = self.data['joined']['attrToTable']
		for attr in tableMap.keys():
			tname = tableMap[attr]
			tableData = self.data[tname]
			attrType = self.schema['tables'][tname]['attrTypes'][attr]
			if attrType == 'cat':
				# print attr
				for val in tableData[attr]['uniques']:
					sup = len(tableData[attr]['indexes'][val])
					if sup >= abs_minsup:
						items.append(Item((attr, val), sup))
		items.sort()

		# for item in items:
			# print item

		idm = {}          # item decode map
		itemCodes = {}    # item codes for each attribute
		for idx in xrange(0, len(items)):
			idm[idx] = items[idx].keyval
			key, value = items[idx].keyval
			if key in itemCodes.keys():
				itemCodes[key].append(idx)
			else:
				itemCodes[key] = [idx]

		# print idm
		# print itemCodes
		self.data['joined']['idm'] = idm
		self.data['joined']['itemCodes'] = itemCodes

def main():

	# items = []
	# items.append(Item((0, 0), 100));
	# items.append(Item((1, 0), 70));
	# items.append(Item((1, 1), 100));
	# items.sort()
	# for item in items:
		# print item

	# db = Database('NBAPlayers.json')
	# print db.schemaFile

	# db.loadDBSchema()
	# print db.schema

	# db.loadData()

	# minsup: 0.5%
	# db.itemRecode(20)

	# indentlen=2
	# with open ('database.json', mode="w") as file:
		# json.dump(db.data, file, sort_keys=True, indent=indentlen)

	minsup = 1

	db = Database('NBAPlayers.json')
	# db.loadDB()

	db.loadDBforALPINE(minsup)

	db.virtualJoin()
	db.jointItemRecode(minsup)

	indentlen=2
	# with open ('database.json', mode="w") as file:
	# with open ('NBAPlayers.db', mode="w") as file:
	# with open ('NBAPlayersAlpine.db', mode="w") as file:
	with open ('NBAPlayersJoin.db', mode="w") as file:
		json.dump(db.data, file, sort_keys=True, indent=indentlen)

# main()
