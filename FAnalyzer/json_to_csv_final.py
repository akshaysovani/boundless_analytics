import csv
import json
import pandas
from sys import argv

# Get the input arguments
scriptname, filename = argv

# Create the output filename
outputfilename = filename[:-5] + '.csv'

# Read the json file
df = pandas.read_json(filename)
# Write to csv file
df.to_csv(outputfilename, index = False)

