import sys
import json

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)

attributes = {}

for datum in data:
    for att in datum['slice']:
        key = att[0]
        if key in attributes:
            attributes[key] = attributes[key] + 1
        else:
            attributes[key] = 1

idx = 1
sortedCats = sorted(attributes)
for orderedKey in sortedCats:
    attributes[orderedKey] = idx
    # print orderedKey + " = " + attributes[orderedKey]
    idx = idx + 1


id = 0
print "id,signature,plot_type,variable_1,variable_2," + ','.join(sortedCats) + ",score,support,dataset"

for datum in data:

    signature = ""
    sliceInfo = datum['slice']
    for att in sliceInfo:
        signature = signature + str(attributes[att[0]])

    sliceCols = [''] * len(sortedCats)
    for att in sliceInfo:
        sliceCols[attributes[att[0]]-1] = att[1]

    print str(id) + "," + signature + "," + datum['type'] + "," + datum['x'] + "," + (datum['y'] if 'y' in datum else "") + "," \
    + ','.join(sliceCols) + "," + str(datum['mark']) + "," + str(datum['support']) + "," + datum['dataset']
    
    id = id + 1
