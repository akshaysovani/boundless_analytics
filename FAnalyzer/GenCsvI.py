import sys
import urllib.request
import ijson

parser = ijson.parse(urllib.request.urlopen('file:///home/ba/FAnalyzer/NBAPlayers_charts.json'))

attributes = {}

first = True
for prefix, event, value in parser:
    if (prefix, event) == ('item.slice.item.item', 'string') and first:
        if value in attributes:
            attributes[value] = attributes[value] + 1
        else:
            attributes[value] = 1
    first = not first
print('here')
idx = 1
sortedCats = sorted(attributes)
for orderedKey in sortedCats:
    attributes[orderedKey] = idx
    # print orderedKey + " = " + attributes[orderedKey]
    idx = idx + 1


id = 0
print("id,signature,plot_type,variable_1,variable_2," + ','.join(sortedCats) + ",score,support,dataset")

