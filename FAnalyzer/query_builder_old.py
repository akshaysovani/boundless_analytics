from sys import argv
import pandas as pd
import json

scriptname, filename = argv

# Read the categorical names from the file
with open(filename) as json_file:
    data = json.load(json_file)

# Extract the table name
tablename = filename.replace('/home/ba/FAnalyzer/schemaData/json/','')
tablename = tablename[:-5]

# Get the column name and its attrTypes
attrTypes = data['tables'][tablename]['attrTypes']
column_names = ['firstAttr', 'secondAttr', 'score', 'support', 'plottype']
categorical_names = []

# Get all the categorical column names
for attr in attrTypes:
    if (attrTypes[attr] == "cat"):
        column_names.append(attr)
        categorical_names.append(attr)

# Open charts.json file and read the information required
charts_filename = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + tablename + "_charts.json"

# Read and load the data
with open(charts_filename, 'r') as data_file:
    json_data_all = data_file.readlines()

for json_data in json_data_all:
    if (count == 0):
        json_data = json_data[1:-2]
    else:
        json_data = json_data[:-2]

    something = json.loads(json_data)


# with open(charts_filename) as json_file:
#     new_data = json.load(json_file)

final_data = []

# Get the information
for i in range(0, len(new_data)):
    data_points = {}
    # For first and second attribute
    data_points['firstAttr'] = new_data[i]['x']
    try:
        data_points['secondAttr'] = new_data[i]['y']
    except:
        data_points['secondAttr'] = 'NA'
    # For score
    data_points['score_boundless'] = new_data[i]['mark']
    # For support
    data_points['support_boundless'] = new_data[i]['support']
    # For plottype
    data_points['plottype_boundless'] = new_data[i]['type']
    # For url
    try:
        data_points['url'] = new_data[i]['url']
    except:
        data_points['url'] = ""
    # For slice
    # If there is nothing in the slice
    if(len(new_data[i]['slice']) == 0):
        # Set every categorical variable to NA
        for var in categorical_names:
            data_points[var] = 'NA'
    else:
        # First set every categorical variable to NA
        for var in categorical_names:
            data_points[var] = 'NA'
        # Set categorical variables that are present
        for slice_attr in new_data[i]['slice']:
            data_points[slice_attr[0]] = slice_attr[1]

    # Append the data point to the actual data
    try:
        if(new_data[i]['url']):
            final_data.append(data_points)
    except:
        pass

# Store the data into a DataFrame
df = pd.DataFrame(final_data)
outputfilename = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + tablename + '_charts.csv'

# Write the dataframe to a csv
df.to_csv(outputfilename, index = False)
