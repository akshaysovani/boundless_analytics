import csv
import json
from sys import argv

# Get the input arguments
scriptname, filename = argv

# Open the input and output file
infile = open(filename)
outputfilename = filename[:-5] + '.csv'

outfile = open(outputfilename, 'w')
output = csv.writer(outfile)

# Load the json file
data = json.load(infile)
# headers = data[0].keys()
headers = ['data', 'dataset', 'dimensions', 'mark', 'plottype', 'slice', 'support', 'tablename', 'type', 'url', 'x', 'y']

# Write the headers
output.writerow(headers)

# Write each row of data
for row in data:
    output.writerow(row.values())

# Close the input and output files
infile.close()
outfile.close()

import pandas
df = pandas.read_json(filename)
print(df.to_csv())
