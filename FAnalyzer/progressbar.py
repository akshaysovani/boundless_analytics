from sys import argv
import time
import mysql.connector

scriptname, filename = argv

progress_value = 0
status_value = ""

#  Update 1% every 6 seconds
while progress_value < 90 and status_value != "Done" and status_value != "Error":

    #  Increment progress value
    progress_value += 0.5

    time.sleep(3)

    # Connections credentials and other parameters
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        passwd="rootpass",
        port=3307,
        auth_plugin='mysql_native_password',
        database="db"
    )

    update_query = "UPDATE dataset_information SET progress = " + "\'" + str(progress_value) + "\'" + " WHERE actual_filename = " + "\'" + filename + "\'" + ";"
    # Get the cursor ready
    mycursor = mydb.cursor()

    # Running the whole query
    mycursor.execute(update_query)
    # Make sure the change is retained
    mydb.commit()

    # Query
    select_query = "SELECT status FROM dataset_information WHERE actual_filename = " + "\'" + filename + "\'" + ";"

    # Running the select query
    mycursor.execute(select_query)
    results = mycursor.fetchall()

    for result in results:
        status_value = result[0]

    # Close connections
    mycursor.close()
    mydb.close()
