import mysql.connector
from sys import argv
import pandas as pd

# Get file input from user
scriptname, filename = argv

print("Entered mysql connect query")
print("filename ",filename)


# Connections credentials and other parameters
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  passwd="rootpass",
  port=3307,
  auth_plugin='mysql_native_password',
  database="query"
)


# Extract table name from .csv file
tablename = filename.replace('/home/ba/FAnalyzer/schemaData/schemaCSV/', '')
table_name = tablename[:-4]

mycursor = mydb.cursor()

# Drop table if it already exists
drop_query = "DROP TABLE IF EXISTS " + "`" + table_name + "`"

mycursor.execute(drop_query)

# Load the data from csv and get the column names to create table
# Open csv file
csv_information = pd.read_csv(filename)
print("cols: ",list(csv_information.columns))

column_names = list(csv_information.columns)
print ("column names: ",column_names)


#additional_columns = {'is_favorite': 'bool', 'comments': 'TEXT'}
col_names = "("

# Create table query
create_table_query = """
create table """ + "`" + table_name + "`" + " ("

for col in column_names:
    col = col.replace(" ", "")
    create_table_query += " " + "`" + str(col) + "`" + " LONGTEXT,"
    col_names += "`" + col + "`, "
#for key, value in additional_columns.items():
create_table_query += " " + "`is_favorite` bool default false,"
create_table_query += " " + "`comments` TEXT,"

create_table_query = create_table_query[:-1]
create_table_query += ");"
# print(create_table_query)
col_names = col_names[:-2]
col_names += ");"
print("create table query: ",create_table_query)
mycursor.execute(create_table_query)

print("Created table ", table_name, ".....")

# File location in docker container
file_location = '/home/root/data/' + table_name + '.csv'

# Load query from csv file
load_data_query = """
load data infile \'""" + file_location + """\' into table """ + "`" + table_name + "`" + """ fields terminated BY \',\' OPTIONALLY ENCLOSED BY \'\"\' ESCAPED BY '\\\\' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES """ + col_names

print(load_data_query)

# Load the data and then commit it
mycursor.execute(load_data_query)

print("Loaded data into the table .....")

mydb.commit()

'''
# Total count cannot exceed 16
total_count = 0


to_avoid_in_index = ['score_boundless', 'support_boundless', 'url']

#  Create index query

create_index_query = """

create index """ + "`" + table_name + "_index` ON " + "`" + table_name + "`" + " ("
for col in column_names:
    if (col not in to_avoid_in_index and total_count < 15):
        col = col.replace(" ", "")
        create_index_query += "`" + str(col) + "`,"
        total_count += 1

create_index_query = create_index_query[:-1]
create_index_query += ");"
print(create_index_query)
mycursor.execute(create_index_query)
'''
#print("Created index on ", table_name, ".....")

print("Done!!")

# Close connections

mycursor.close()
mydb.close()


