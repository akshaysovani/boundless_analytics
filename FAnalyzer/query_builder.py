from sys import argv
import pandas as pd
import json
import csv

scriptname, filename = argv


# Read the categorical names from the file
with open(filename) as json_file:
    data = json.load(json_file)

# Extract the table name
tablename = filename.replace('/home/ba/FAnalyzer/schemaData/json/', '')
tablename = tablename[:-5]

# Get the column name and its attrTypes
attrTypes = data['tables'][tablename]['attrTypes']
column_names = ['firstAttr', 'secondAttr', 'score_boundless', 'support_boundless', 'plottype_boundless', 'url']
categorical_names = []

# Get all the categorical column names
for attr in attrTypes:
    if (attrTypes[attr] == "cat"):
        column_names.append(attr)
        categorical_names.append(attr)

# Open charts.json file and read the information required
charts_filename = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + tablename + "_charts.json"

count = 0

outputfilename = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + tablename + '_charts.csv'

with open(outputfilename, 'w') as f:
    data_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Write the header
    data_writer.writerow(column_names)

    # Read and load the data
    with open(charts_filename, 'r') as data_file:
        json_data = data_file.readline()

        while json_data:

            # Reset the data in row
            final_data = []
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
            final_data.append(new_data['x'])
            try:
                final_data.append(new_data['y'])
            except:
                final_data.append('NA')
            # For score
            final_data.append(new_data['mark'])
            # For support
            final_data.append(new_data['support'])
            # For plottype
            final_data.append(new_data['type'])
            # For url
            try:
                final_data.append(new_data['url'])
            except:
                final_data.append("")
            # For slice
            # If there is nothing in the slice
            if (len(new_data['slice']) == 0):
                # Set every categorical variable to NA
                for var in categorical_names:
                    final_data.append('NA')
            else:
                data_points = {}
                # First set every categorical variable to NA
                for var in categorical_names:
                    data_points[var] = 'NA'
                # Set categorical variables that are present
                for slice_attr in new_data['slice']:
                    data_points[slice_attr[0]] = slice_attr[1]

                # Append the values
                for val in categorical_names:
                    final_data.append(data_points[val])

            # Append the data point to the actual data
            try:
                if (new_data['url']):
                    data_writer.writerow(final_data)
            except:
                pass

            json_data = data_file.readline()

print("Done!! YAY!!!")
