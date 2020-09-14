from sys import argv
import time
import mysql.connector
import os
# import subprocess
# import re
# import shlex

scriptname, filename = argv

# Set the values for first time
total = 0
status_value = "Processing"

#  Update 1% every 6 seconds
while total < 80 and status_value == "Processing":

    # Get the space occupied
    stat = os.statvfs('/home/ba/')
    total = stat.f_bavail / float(stat.f_blocks)
    total = int(round(100 - (total * 100)))

    # command = "df -h"
    # # df = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    # # df = subprocess.check_output(['df', '-h'])
    # df = subprocess.check_output("df -h /", shell=True)
    # df = df.decode('utf8')
    # # df = os.popen('df -h /').read()
    # # print(df)
    # for line in df.split("\n"):
    #     if re.search("/dev/disk/by-label/DOROOT.*", line):
    #         disk_space = line.split()[4]
    #         break
    #
    # total = disk_space
    # total = int(total[:-1])

    # Sleep for one second
    time.sleep(1)

    # If space is greater than 97, set status to "Disk Full"
    if (total >= 80):

        # # Check the dataset that has the lowest timestamp with status processing
        # # Get the dataset that is currently processing
        # # Connections credentials and other parameters
        # mydb = mysql.connector.connect(
        #     # host="209.97.156.178",
        #     # Uncomment the two below lines before loading to server
        #     host="127.0.0.1",
        #     user="root",
        #     passwd="rootpass",
        #     port=3307,
        #     auth_plugin='mysql_native_password',
        #     database="db"
        # )
        #
        # # Get the cursor ready
        # mycursor = mydb.cursor()
        #
        # # Query
        # query = "SELECT actual_filename, curr_timestamp from dataset_information where status = " + "\'" + "Processing" + "\'" + ";"
        #
        # # Running the whole query
        # mycursor.execute(query)
        # results = mycursor.fetchall()
        #
        # # Close connections
        # mycursor.close()
        # mydb.close()
        #
        # my_table_list = {}
        # my_table_list['actual_filename'] = []
        # my_table_list['curr_timestamp'] = []
        #
        # # Get all the tables present
        # for table in results:
        #     my_table_list['actual_filename'].append(table[0])
        #     my_table_list['curr_timestamp'].append(float(table[1]))
        #
        # # Get the index of the dataset with the minimum timestamp
        # selected_index = my_table_list['curr_timestamp'].index(max(my_table_list['curr_timestamp']))
        # selected_filename = my_table_list['actual_filename'][selected_index]

        # if (selected_filename == filename):

        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        update_query = "UPDATE dataset_information SET status = " + "\'" + "Out of Space" + "\'" + " WHERE actual_filename = " + "\'" + filename + "\'" + ";"
        # Get the cursor ready
        mycursor = mydb.cursor()

        # Running the whole query
        mycursor.execute(update_query)
        # Make sure the change is retained
        mydb.commit()

        # Close connections
        mycursor.close()
        mydb.close()

        # # Sleep for three second
        # time.sleep(3)

    # Get the current status
    # Connections credentials and other parameters
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        passwd="rootpass",
        port=3307,
        auth_plugin='mysql_native_password',
        database="db"
    )

    # Query
    select_query = "SELECT status FROM dataset_information WHERE actual_filename = " + "\'" + filename + "\'" + ";"
    # Get the cursor ready
    mycursor = mydb.cursor()

    # Running the select query
    mycursor.execute(select_query)
    results = mycursor.fetchall()

    for result in results:
        status_value = result[0]

    # Close connections
    mycursor.close()
    mydb.close()