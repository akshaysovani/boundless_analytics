import mysql.connector
from sys import argv
import pandas as pd
import json
import io
import math
import csv

scriptname, filename = argv

mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        passwd="rootpass",
        port=3307,
        auth_plugin='mysql_native_password',
        database="query")
table_name = filename.replace('/home/ba/FAnalyzer/schemaData/schemaCSV/', '')
table_name = table_name[:-4]
print("table_name - ", table_name)
mycursor = mydb.cursor()

# select data from metadata table.
select_query = "SELECT * FROM " + "`" + table_name + "`" + " WHERE score_boundless < 1 AND plottype_boundless <> 'heatmap';"

column_query = "SHOW COLUMNS FROM " + "`" + table_name + "`" + ";"
mycursor.execute(column_query)
column_results = mycursor.fetchall()

min_max_support_query = "SELECT MIN(support_boundless), MAX(support_boundless) FROM " + "`" + table_name + "`" + ";"
mycursor.execute(min_max_support_query)
min_max_support_res = mycursor.fetchone()
min_support = min_max_support_res[0]
max_support = min_max_support_res[1]

cols = [col[0] for col in column_results]
cols = cols[:-2]

mycursor.execute(select_query)
metadata_results = mycursor.fetchall()
#print ("metadata_results: ",metadata_results)
cache_table_name = table_name[:-6] + 'cache'

#drop table to clear the cache.
drop_query = "DROP TABLE IF EXISTS " + "`" + cache_table_name + "`"
mycursor.execute(drop_query)

drop_query_2 = "DROP TABLE IF EXISTS " + "`" + cache_table_name + "_histogram" + "`"
mycursor.execute(drop_query_2)

# create table
create_table_query = "CREATE TABLE " + "`" + cache_table_name + "`"
create_table_query += " (id int AUTO_INCREMENT, first_attr TEXT, second_attr TEXT, slice LONGTEXT, data LONGTEXT, metadata LONGTEXT, plottype TEXT, slice_size TEXT, acceptable_slice_size BOOLEAN, PRIMARY KEY (id));"
mycursor.execute(create_table_query)

create_bins_table_query = "CREATE TABLE " + "`" + cache_table_name + "_histogram" + "`"
create_bins_table_query += " (id int AUTO_INCREMENT, first_attr TEXT, bins_metadata LONGTEXT, PRIMARY KEY(id));"
mycursor.execute(create_bins_table_query)

header_idx_dict = {}
header = None
csv_path = '/home/ba/FAnalyzer/schemaData/data/' + table_name[:-7] + '.csv'
with io.open(csv_path, 'r') as f:
    reader = csv.reader(f)
    header = next(reader)

for idx, head_col in enumerate(header):
    header_idx_dict[head_col] = idx

insert_query = " INSERT INTO " + "`" + table_name[:-6] + 'cache' + "`" + " (first_attr, second_attr, slice, data, metadata, plottype, slice_size, acceptable_slice_size) values (%s, %s, %s, %s, %s, %s, %s, %s);"

insert_query_histogram_bins = " INSERT INTO " + "`" + cache_table_name + "_histogram" + "`" + " (first_attr, bins_metadata) values (%s, %s);"

bins = 0
maxValue = 0
minValue = 0
bins_meta_dict = {}
fa = []
counter = 0
print_count = 0
#print ("Total metadata results: ",len(metadata_results))
for i in range(0, len(metadata_results)):
    column_val_mapping = {}
    table_key = []
    for j in range(6, len(cols)):
        if (metadata_results[i][j] != 'NA'):
            column_val_mapping[cols[j]] = metadata_results[i][j]
    first_attr = metadata_results[i][0]
    second_attr = metadata_results[i][1]
    plottype = metadata_results[i][4]
    filtered_rows = []
    with io.open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        first_attr_index = header_idx_dict[first_attr]
        second_attr_index = -1
        if second_attr != 'NA':
            second_attr_index = header_idx_dict[second_attr]
        for line in reader:
            if (len(line) != len(header)):
                continue
            if (line[first_attr_index] == 'nan' or line[first_attr_index] == ''):
                continue
            if (second_attr != 'NA' and (line[second_attr_index] == 'nan' or line[second_attr_index] == '')):
                continue
            boolean_cond = True
            for key, value in column_val_mapping.items():
                search_index = header_idx_dict[key]
                boolean_cond = boolean_cond and line[search_index] == value
            if (boolean_cond):
                filtered_rows.append(line)
    dataframe1 = pd.DataFrame(filtered_rows, columns = header)
    #if i == 1:
    #print("length of datafram1: ",len(dataframe1))
    #slice_size = len(dataframe1)
    for k in range(0, len(dataframe1.columns)):
        dataframe1.iloc[:,k] = pd.to_numeric(dataframe1.iloc[:,k], errors='ignore')
    acceptable_slice_size = True
    slice_size = len(dataframe1)
    if slice_size < 5:
        acceptable_slice_size = False
    if (second_attr != 'NA'):																#heatmap or timeseriesplot
        #print('second attribute is NA')
        dataframe1.dropna(subset=[first_attr, second_attr], inplace=True)
        #boxplot needs to calculate max, min, quantiles
        if (metadata_results[i][4] == 'timeseries'):
            #print('here',metadata_results[i][0])
            #if (len(dataframe1[second_attr]) > 5):
                #if counter == 0:
                #    fa.append(metadata_results[i][0])
                    #print('appended')
                    #print('---fa------',fa)
                #else:
                #    if metadata_results[i][0] not in fa:
                #        print('here')
                #        continue
                #counter += 1
                #dataframe1 = dataframe1.groupby('DATE', as_index=False)['POLLEN'].mean()
                #sort_attr = "'" + first_attr + "'"

                #print("sort attr: ",sort_attr)
                aggregation_attr = "'" + second_attr + "'"
                #print(aggregation_attr)
                dataframe1[first_attr] = pd.to_datetime(dataframe1[first_attr])
                dataframe1.sort_values(by=[first_attr], inplace=True)
                dataframe1 = dataframe1.groupby(first_attr, as_index=False)[second_attr].sum()
                if print_count == 0:
                    print("before: ",dataframe1)
                #dataframe1.rolling(5, on=second_attr).mean()
                dataframe1 = dataframe1.set_index(first_attr).rolling(7).mean()
                dataframe1[second_attr] = dataframe1[second_attr].fillna(0)
                datelist = list(dataframe1.index.values)
                if print_count == 0:
                    print("after: ",dataframe1)
                    print("Date list",datelist)
                print_count += 1
                slice_size = len(dataframe1)
                if slice_size < 11:
                    acceptable_slice_size = False
                #dataframe1.sort_values(by=['0'], inplace=True)
                #print(dataframe1)
                #value = [list(zip(dataframe1[first_attr], dataframe1[second_attr])), 100.0]
                value = [list(zip(datelist, dataframe1[second_attr])), 100.0]
                #min_value = dataframe1[second_attr].quantile(0.05).astype('float')
                #max_value = dataframe1[second_attr].quantile(0.95).astype('float')
                #median_value = dataframe1[second_attr].quantile(0.5).astype('float')
                #low_quantile = dataframe1[second_attr].quantile(0.25).astype('float')
                #high_quantile = dataframe1[second_attr].quantile(0.75).astype('float')
                #value = [(min_value, low_quantile, median_value, high_quantile, max_value), 100.0]
                if (len(value) > 0):
                    mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value, default=str), json.dumps(metadata_results[i]), plottype, slice_size, acceptable_slice_size))
                #first_attr_unique_arr = dataframe1[first_attr].unique()
                #for attr_value in first_attr_unique_arr:
                #    min_value = dataframe1[dataframe1[first_attr] == attr_value][second_attr].quantile(0.05).astype('float')
                #    max_value = dataframe1[dataframe1[first_attr] == attr_value][second_attr].quantile(0.95).astype('float')
                #    median_value = dataframe1[dataframe1[first_attr] == attr_value][second_attr].quantile(0.5).astype('float')
                #    low_quantile = dataframe1[dataframe1[first_attr] == attr_value][second_attr].quantile(0.25).astype('float')
                #    high_quantile = dataframe1[dataframe1[first_attr] == attr_value][second_attr].quantile(0.75).astype('float')
                #    value = [(min_value, low_quantile, median_value, high_quantile, max_value), 100.0]
                #    column_val_mapping[first_attr] = attr_value
                #    if (len(value) > 0):
                #        mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value), json.dumps(metadata_results[i]) ,plottype, slice_size, acceptable_slice_size))
                #value = [list(zip(dataframe1[first_attr], dataframe1[second_attr])), 100.0]
        else:
            if (len(value[0]) > 0):
                mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value), json.dumps(metadata_results[i]) ,plottype, slice_size, acceptable_slice_size))
    elif (metadata_results[i][4] == 'percentile'):
        quantiles = [0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05]
        #if (len(column_val_mapping) == 0):
        result = []
        if (len(dataframe1[first_attr]) > 0):
            for quant in quantiles:
                result.append(dataframe1[first_attr].quantile(quant).astype('float'))
            value = [tuple(result), 100.0]
            if (len(value) > 0):
                mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value), json.dumps(metadata_results[i]), plottype, slice_size, acceptable_slice_size))
                #min_value = dataframe1[second_attr].quantile(0.05).astype('float')
                #max_value = dataframe1[second_attr].quantile(0.95).astype('float')
                #median_value = dataframe1[second_attr].quantile(0.5).astype('float')
                #low_quantile = dataframe1[second_attr].quantile(0.25).astype('float')
                #high_quantile = dataframe1[second_attr].quantile(0.75).astype('float')
                #value = [(min_value, low_quantile, median_value, high_quantile, max_value), 100.0]
                #if (len(value) > 0):
                #    mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value), json.dumps(metadata_results[i])))
    elif (metadata_results[i][4] == 'boxplot'): #boxplot
        min_value = dataframe1[first_attr].quantile(0.05).astype('float')
        max_value = dataframe1[first_attr].quantile(0.95).astype('float')
        median_value = dataframe1[first_attr].quantile(0.5).astype('float')
        low_quantile = dataframe1[first_attr].quantile(0.25).astype('float')
        high_quantile = dataframe1[first_attr].quantile(0.75).astype('float')
        value = [(min_value, low_quantile, median_value, high_quantile, max_value), 100.0]
        if (len(value) > 0):
            mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value), json.dumps(metadata_results[i]), plottype, slice_size, acceptable_slice_size))
    else:		#histogram, bargraph
         dataframe1.dropna(subset=[first_attr], inplace=True)
         # For Histogram there is no need to group the rows. Just return the list.
         # The bins are calculated using the Highcharts API on frontend.
         if (metadata_results[i][4] == 'histogram'):
             if (first_attr not in bins_meta_dict):
                inner_dict = {}
                if (metadata_results[i][3] == max_support):
                    bins = math.ceil(math.sqrt(dataframe1[first_attr].count()))
                    inner_dict['bins'] = bins
                    inner_dict['max'] = dataframe1[first_attr].max()
                    inner_dict['min'] = dataframe1[first_attr].min()
                    bins_meta_dict[first_attr] = inner_dict
             value = [list(dataframe1[first_attr]), 100.0]
         else:
             if (metadata_results[i][4] == 'timeseries'):
                 print("Here in else for timeseries.. ")
             res = dataframe1.groupby(first_attr)[first_attr].count() * 100 / dataframe1[first_attr].count()
             value = [list(zip(res.index, res.values)), sum(res.values)]
         if (len(value[0]) > 0):
             mycursor.execute(insert_query, (first_attr, second_attr, json.dumps(column_val_mapping), json.dumps(value), json.dumps(metadata_results[i]), plottype, slice_size, acceptable_slice_size))
for k, v in bins_meta_dict.items():
    mycursor.execute(insert_query_histogram_bins, (k, json.dumps(v)))
mydb.commit()
mycursor.close()
mydb.close()
