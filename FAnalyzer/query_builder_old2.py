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
column_names = ['firstAttr', 'secondAttr', 'score_boundless', 'support_boundless', 'plottype_boundless']
categorical_names = []

# Get all the categorical column names
for attr in attrTypes:
    if (attrTypes[attr] == "cat"):
        column_names.append(attr)
        categorical_names.append(attr)

# Open charts.json file and read the information required
charts_filename = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + tablename + "_charts.json"

final_data = []
count = 0

# Read and load the data
with open(charts_filename, 'r') as data_file:
    json_data_all = data_file.readlines()

for json_data in json_data_all:
    # For first
    if (count == 0):
        json_data = json_data[1:-2]
    # For remaining
    else:
        json_data = json_data[:-2]
    # Changing into JSON format
    new_data = json.loads(json_data)

    count += 1

    data_points = {}
    # For first and second attribute
    data_points['firstAttr'] = new_data['x']
    try:
        data_points['secondAttr'] = new_data['y']
    except:
        data_points['secondAttr'] = 'NA'
    # For score
    data_points['score_boundless'] = new_data['mark']
    # For support
    data_points['support_boundless'] = new_data['support']
    # For plottype
    data_points['plottype_boundless'] = new_data['type']
    # For url
    try:
        data_points['url'] = new_data['url']
    except:
        data_points['url'] = ""
    # For slice
    # If there is nothing in the slice
    if (len(new_data['slice']) == 0):
        # Set every categorical variable to NA
        for var in categorical_names:
            data_points[var] = 'NA'
    else:
        # First set every categorical variable to NA
        for var in categorical_names:
            data_points[var] = 'NA'
        # Set categorical variables that are present
        for slice_attr in new_data['slice']:
            data_points[slice_attr[0]] = slice_attr[1]

    # Append the data point to the actual data
    try:
        if (new_data['url']):
            final_data.append(data_points)
            # print("Length",len(final_data))
    except:
        pass

    if (count == 100000):
        df1 = pd.DataFrame(final_data)
        final_data = []

# Store the data into a DataFrame
df = pd.DataFrame(final_data)
if (count > 100000):
    final_df = df1.append(df, ignore_index=True)
else:
    final_df = pd.DataFrame(final_data)

outputfilename = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + tablename + '_charts.csv'

# Write the dataframe to a csv
final_df.to_csv(outputfilename, index = False)

print("Done!! YAY!!!")