""" application.py """

from flask import (
    Flask,
    jsonify,
    request,
    session,
    redirect,
    url_for,
    escape,
    make_response,
    render_template,
    copy_current_request_context,
    send_from_directory,
    Response)

import threading

from flask_session import Session

from flask_paginate import Pagination, get_page_parameter

import csv
import numpy as np
import pandas as pd
import mysql.connector
from collections import OrderedDict
import StringIO
import subprocess
import shlex
import os
from werkzeug.utils import secure_filename
import signal
# import pandas_profiling

import requests
import urllib
import math
import json
import sys
import re
from collections import Sequence
import base64
import io
import chardet
import traceback
from BAServiceExceptions import BAServiceError
import time
import copy

application = Flask(__name__, static_url_path='')

SESSION_TYPE = 'filesystem'
application.config.from_object('config.default')

# Basic setting
application.secret_key = "boundless_secret"
application.config['SESSION_TYPE'] = SESSION_TYPE
application.config['UPLOAD_FOLDER'] = '/home/ba/FAnalyzer/schemaData/origData/'

Session(application)

#with open('NBAPlayersJoin.db') as json_file:
#    database = json.load(json_file)
#json_file.close()

# Global variable
print("global variables created")
final_df = pd.DataFrame(data=None)
actual_file_name = ""
flag_value = 'False'
boxplot_numerical_attr_list = []
print("logging in becoming false now")
loggedIn = False

# def toConjunction(queryString):
#     return "+_text_:" + "* +_text_:".join(queryString.split()) + "* "
# def escapeQuery(queryText):
#     escaped = re.sub(r'([%+\-!(){}\[\]\^"~*?:/\\]|&&|\|\|)', r'\\\1', queryText)
#     return escaped

# def getDatasetList():
#     datasetList = requests.request("GET", application.config['SOLR_PLOTTYPE_URL_ROOT']
#         + "/select?q=*%3A*&rows=0&facet=true&facet.field=dataset&facet.limit=-1" + application.config['SOLR_URL_SUFFIX']).json()['facet_counts']['facet_fields']['dataset']
#     return [str(x) for ind, x in enumerate(datasetList) if ind % 2 == 0]


@application.errorhandler(BAServiceError)
def handle_baservice_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/')
def index():
    loggedIn = False
    print("called login")
    return render_template('login.html')
    # return render_template('startpage.html', datasetList=getDatasetList())

@application.route('/ba/homepage/', methods=['POST'])
def homepage():
    try:
        username_password_object = request.get_json()
        username = username_password_object['username']
        password = username_password_object['password']
        print(username)
        print(password)
        if username == 'root' and password == 'rootpass':
            loggedIn = True
            print("val of looged in :",loggedIn)
            print("logged in success")
            #return render_template('ba.html')
        #else:
            #return render_template('login.html')
        objToSendBack = {}
        if loggedIn:
            objToSendBack['indicator'] = 'success'
        else:
            objToSendBack['indicator'] = 'failure'
        resp = json.dumps(objToSendBack);
        return Response(response=resp, status=200, mimetype="application/json")
    except:
        traceback.print_exc()
        raise BAServiceError("Exception occurred while logging in", 500)
# @application.route('/searchPT/', defaults={'page':1})

# @application.route('/searchPT/<int:page>')
# def searchPlottypes(page):
#     start = (page - 1) * 10
#
#     param = {}
#     param['dataset']  = request.args.get('dataset', 'any')
#     param['optradio'] = request.args.get('optradio', 'any')
#
#     searchformToURL = "?"
#     searchformToURL += "dataset="
#     searchformToURL += request.args.get('dataset', '')
#     searchformToURL += "&optradio="
#     searchformToURL += request.args.get('optradio', '')
#
#     fqStr = ''
#     if param['dataset'] != 'any':
#         fqStr += 'dataset:' + param['dataset']
#     f = {
#          'fq': fqStr
#     }
#     encodedQuery = urllib.urlencode(f)
#
#     if param['optradio'] != 'any':
#         encodedQuery += '&sort=' + param['optradio'] + '+desc'
#     #print encodedQuery
#
#     # Solr Pagination
#     encodedQuery += '&start=' + str(start)
#
#     solrStr = application.config['SOLR_PLOTTYPE_URL_ROOT'] + "/select?q=*%3A*&" + encodedQuery + application.config['SOLR_URL_SUFFIX']
#     # print solrStr
#
#     response = requests.request('GET', solrStr).json()['response']
#
#     nrecords = response['numFound']
#     # npages = math.ceil(float(nrecords)/10)
#     # npages = int(npages)
#     # pages = range(1, min(npages, 10)+1)
#     # pages = range(1, npages+1)
#
#     pagination = Pagination(page=page, per_page=application.config['POSTS_PER_PAGE'], total=nrecords, record_name='plottypes')
#
#     response['start'] = start
#     # response['page'] = page
#     # response['pages'] = pages
#     response['dataset']  = request.args.get('dataset', '')
#     response['optradio'] = request.args.get('optradio', '')
#     response['searchformToURL'] = searchformToURL
#
#     return render_template('plottypes.html', results=response, pagination=pagination)

# @application.route('/form/', methods=['GET'])
# def chartSearchForm():
#     database = request.args.get('dataset')
#     plottype = request.args.get('plottype')
#     optradio = request.args.get('optradio')
#     return render_template('searchform.html', db=database, pt=plottype, op=optradio)

@application.route('/summary/', methods=['POST'])
def summary():
    schema_and_data = request.form

    data = []
    header = []
    schema = {}
    attributes_to_include = {}
    count = 1
    # For header
    data_from_line = schema_and_data["data[0]"]
    header = data_from_line.split(",")

    # For filename
    table_name = schema_and_data["file_name"]

    data_in_a_row = []

    for attribute in header:
        data_in_a_row.append(attribute)

    header = data_in_a_row
    new_header = []

    # Remove any whitespaces and store in header
    for head in header:
        head = head.strip()
        head = str(head)
        new_header.append(head)

    header = new_header

    # For all data points
    for var in schema_and_data:

        if("data" == var[0:4] and var[5] != "0"):
            data_from_line = schema_and_data[var]
            data_from_line = data_from_line.encode('ascii', 'ignore')
            # split_data = data_from_line.split(",")
            s = StringIO.StringIO(data_from_line)
            split_data = list(csv.reader(s, skipinitialspace=True))
            split_data = split_data[0]

            data_in_a_row = []

            for attribute in split_data:
                data_in_a_row.append(attribute)

            if(data_from_line != ""):
                data.append(data_in_a_row)
            count += 1
        else:
            # If attributes
            if(var[0] == "a"):
                attribute_val = var[11:-1]
                attribute_val = attribute_val.strip()
                attributes_to_include[attribute_val] = schema_and_data[var]
            # If schema
            elif(var[5] != "0" and var != "file_name"):
                attribute_val = var[7:-1]
                attribute_val = attribute_val.strip()
                schema[attribute_val] = schema_and_data[var]

    # Create a dataframe
    df = pd.DataFrame(data)
    df.columns = header

    # Remove columns that were excluded by the user
    if (attributes_to_include):
        for attr in attributes_to_include:
            if (attributes_to_include[attr] == "true"):
                df = df.drop(attr, 1)

    # Reset the header if columns were removed
    header = list(df.columns)

    # Count of number of numerical variables
    num_count = 0

    # Change the datatype of the columns
    for col_name in schema:
        col_name = str(col_name)
        if (schema[col_name] == "true"):
            # Add a try catch here in case the user inputs a wrong datatype
            try:
                df[col_name] = df[col_name].astype(float)
                num_count += 1
            except:
                schema[col_name] = "false"
                df[col_name] = df[col_name].astype(str)
        else:
            df[col_name] = df[col_name].astype(str)


    # Store the unique values for each categorical variable
    schema_unique_values = {}
    for var in schema:
        var = var.strip()
        if(schema[var] == "false"):
            var = str(var)
            unique_values = df[var].unique().tolist()
            unique_values_per_attr = {}
            count = 0
            for un_val in unique_values:
                value = str(count)
                un_val = un_val.replace("'", '"')
                unique_values_per_attr[value] = un_val
                count += 1
            unique_values_per_attr = json.dumps(unique_values_per_attr)
            schema_unique_values[var] = str(unique_values_per_attr)


    # Use pandas to get summary
    summary = df.describe(include='all')
    summary = dict(summary)

    #  If numerical variables are present
    if (num_count > 0):
        summary_attributes = ['count', 'unique', 'top', 'freq', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
    else:
        summary_attributes = ['count', 'unique', 'top', 'freq']
    # Very good summary but pandas_profiling is not installing
    # pandas_profiling.ProfileReport(data)

    # Store the summary data in the format of a dictionary
    full_summary = OrderedDict()
    # col_names = summary.columns
    col_names = summary.keys()

    for col in col_names:
        summary_per_column = {}
        for sum_attr in summary_attributes:
            if(pd.isna(summary[col][sum_attr])):
                summary_per_column[sum_attr] = "NA"
            else:
                summary_per_column[sum_attr] = summary[col][sum_attr]
        full_summary[col] = str(summary_per_column)


    # Store the schema in session
    session['my_schema'] = schema
    session['file_name'] = table_name
    session['schema_attributes'] = schema_unique_values

    # Store the data needed to create the JSON (cache) dataset
    cache_json = {}
    cache_json["summary"] = full_summary
    cache_json["schema_attributes"] = schema_unique_values
    cache_json["file_name"] = table_name + "_info.json"
    cache_json["my_schema"] = schema

    # Set the global variable
    global actual_file_name
    actual_file_name = table_name

    # -------------------------------------- #
    # Create a JSON file for the dataset
    # -------------------------------------- #
    # Create a JSON file
    json_file = {}

    json_file["db"] = table_name
    json_file["entityTables"] = [table_name]
    json_file["nTables"] = 1
    json_file["relationTable"] = []
    json_file["tablenames"] = [str(table_name)]
    json_file["tables"] = {}

    json_file["tables"][table_name] = {}

    # Create the attribute types and attributes
    json_file["tables"][table_name]["attrTypes"] = OrderedDict()
    json_file["tables"][table_name]["attributes"] = []
    for col_name in header:
        # For attribute types
        # For numerical
        if (schema[col_name] == "true"):
            json_file["tables"][table_name]["attrTypes"][col_name] = "num"
        # For categorical
        else:
            json_file["tables"][table_name]["attrTypes"][col_name] = "cat"
    # For attributes
    json_file["tables"][table_name]["attributes"] = header

    json_file["tables"][table_name]["pk"] = []
    json_file["tables"][table_name]["exceptions"] = []
    json_file["tables"][table_name]["comparable"] = []

    # # Writing into a file
    # with open(table_name + '.json', 'w') as content:
    #     json.dump(json_file, content)

    # NOTE : We write the file here too as it needs to be accessed from Database.py
    # NOTE : Uncomment the below two lines below before loading into the server
    with open('/home/ba/FAnalyzer/schemaData/json/' + table_name + '.json', 'w') as content:
        json.dump(json_file, content)

    # NOTE : Uncomment line below before loading into the server
    path = '/home/ba/FAnalyzer/schemaData/data/' + table_name + '.csv'
    # path = table_name + '.csv'
    # Write the data into a csv file
    df.to_csv(path, sep=',', index=False, encoding='utf-8')

    # -------------------------------------- #
    # Create a JSON file future use (cache)
    # -------------------------------------- #
    with open('/home/ba/FAnalyzer/schemaData/info/' + table_name + '_info.json', 'w') as content:
        json.dump(cache_json, content)

    return jsonify(full_summary)

@application.route('/query_attr/', methods=['POST'])
def query_attr():
    # Set the filename
    file_name = request.form

    # Open the file
    try:
        with io.open('/home/ba/FAnalyzer/schemaData/info/' + file_name['table'] + '_info.json') as json_file:
            all_data = json.load(json_file)

        my_data = all_data['schema_attributes']
        return jsonify(my_data)
    except IOError as io_error:
        print("IO Error while getting schema attributes - ", file_name['table'], io_error)
        traceback.print_exc()
        raise BAServiceError("Error while getting schema attributes - " + file_name['table'] + ".Please check system logs for more details", 400)
    except:
        print("Unexpected Error occurred while getting schema attributes -", file_name['table'])
        traceback.print_exc()
        raise BAServiceError("Unexpected Error occurred while getting schema attributes - " + file_name['table'] + ".Please check system logs for more details.")

@application.route('/page2/', methods=['POST'])
def page2():
    try:
        file_name = session.get('file_name')
        # Open the file
        with io.open('/home/ba/FAnalyzer/schemaData/info/' + file_name + '_info.json') as json_file:
            all_data = json.load(json_file)

        my_data = all_data['schema_attributes']
        return jsonify(my_data)
    except IOError as io_error:
        print("IO Error while getting schema attributes - ", file_name['table'], io_error)
        traceback.print_exc()
        raise BAServiceError("Error while getting schema attributes - " + file_name['table'] + ".Please check system logs for more details.", 400)
    except:
        print("Unexpected Error occurred while getting schema attributes - ", file_name['table'])
        traceback.print_exc()
        raise BAServiceError("Unexpected Error while getting schema attributes - " + file_name['table'] + ".Please check system logs for more details.")

#@application.route('/ba/loadHomePage/', methods=['POST'])
@application.route('/ba/loadHomePage/')
def loadHomePage():
    return render_template('ba.html')
    #try:
    #    Indicator_object = request.get_json()
    #    indicator = Indicator_object['ind']
    #    if indicator == 'success':
    #        print("in success last")
    #        return render_template('ba.html')
    #    else:
    #        return render_template('login.html')
    #except:
    #    return render_template('login.html')

@application.route('/ba/', methods=['POST','GET'])
def ba():
    #print("looged in val is: ", loggedIn)
    #if loggedIn:
        #print('in if')
    print("called ba")
    try:
        Indicator_object = request.get_json()
        indicator = Indicator_object['indicator']
        objToSendBack = {}
        if indicator == 'success':
            print("In if of /ba/")
            objToSendBack['ind'] = 'success'
            print("rendered")
        else:
            print("In else of /ba/")
            objToSendBack['ind'] = 'failure'
        resp = json.dumps(objToSendBack);
        return Response(response=resp, status=200, mimetype="application/json")
    except:
        return render_template('login.html')
        #traceback.print_exc()
        #raise BAServiceError("This is not a valid page..", 500)
    #else:
    #    print('in else')
    #    return render_template('login.html')

# def encodeQuery(queryText):
#     return

@application.route('/tablecheck/', methods=['POST'])
def tablecheck():
    try:
        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Query
        query = "Select actual_filename, status  from dataset_information;"

        # Running the whole query
        mycursor.execute(query)
        results = mycursor.fetchall()

        my_table_list = {}
        my_table_list['tables'] = []
        my_table_list['status'] = []
        my_table_list['space'] = []

        # Get all the tables present
        for table in results:
            my_table_list['tables'].append(table[0])
            my_table_list['status'].append(table[1])

            # Get the space occupied by the table
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="query"
            )

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Query
            query = "SELECT TABLE_NAME AS 'Table', ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024),2) AS 'Size' FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'query' AND TABLE_NAME = " + "\'" + table[0] + "_charts" + "\'" + " ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;"

            # Running the whole query
            mycursor.execute(query)
            size_tab = mycursor.fetchall()
            if (size_tab):
                for tb in size_tab:
                    if(tb[1]):
                        table_space_taken = str(tb[1]) + " MB"
            else:
                table_space_taken = "- MB"
            my_table_list['space'].append(table_space_taken)

        # Set the filename
        file_name = request.form
        global actual_file_name
        actual_file_name = file_name['table']

        session['file_name'] = file_name['table']

        return jsonify(my_table_list)
    except:
        print("Unexpected error occurred while table check")
        traceback.print_exc()
        raise BAServiceError("Unexpected error occurred while checking table. Please check system logs for more details.", 500)

@application.route('/progress_check/', methods=['POST'])
def progress_check():
    try:
        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        data = request.form

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Query
        query = "Select status, progress  from dataset_information where actual_filename = " + "\'" + data['actual_filename'] + "\'" + ";"

        # Running the whole query
        mycursor.execute(query)
        results = mycursor.fetchall()

        actual_status = {}
        actual_status['status'] = ""
        actual_status['progress'] = ""

        # Get all the tables present
        for stat in results:
            actual_status['status'] = stat[0]
            actual_status['progress'] = stat[1]

        return jsonify(actual_status)
    except:
        print("Unexpected error while progress check")
        traceback.print_exc()
        raise BAServiceError("Unexpected error occurred while checking progress status. Please check system logs for more details.", 500)

@application.route('/tableadd/', methods=['POST'])
def tableadd():

    try:
        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        data = request.form

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Delete the row if it has the same filename
        query = "DELETE FROM dataset_information WHERE actual_filename = " + "\'" + data['actual_filename'] + "\'" + ";"
        # Running the whole query
        mycursor.execute(query)
        mydb.commit()

        # Query
        query = "INSERT INTO dataset_information (filename,actual_filename,status, progress, curr_timestamp,session_id) VALUES "
        query += "(" + "\'" + data['filename'] + "\'" + "," + "\'" + data['actual_filename'] + "\'" + "," + "\'" + data['status'] + "\'" + "," + "\'" + data['progress'] + "\'" + "," + "\'" + data["timestamp"] + "\'" + "," + "\'" + session.sid + "\'" + ");"

        # Running the whole query
        mycursor.execute(query)
        mydb.commit()

        # Close connections
        mycursor.close()
        mydb.close()

        return "Done loading!!"
    except:
        print("Unexpected error while add table to database")
        traceback.print_exc()
        raise BAServiceError("Unexpected error while add table to database. Please check system logs for more details.", 500)

@application.route('/diskcheck/', methods=['POST'])
def diskcheck():

    stat = os.statvfs('/home/ba/')
    total = stat.f_bavail / float(stat.f_blocks)
    total = int(round(100 - (total*100)))

    percent_full = str(total)

    disk_value = {}
    disk_value['value'] = str(percent_full)

    return jsonify(disk_value)

@application.route('/tabledeletebecauseofdisk/', methods=['POST'])
def tabledeletebecauseofdisk():

    try:
        data = request.form
        # Get the dataset that is currently processing
        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Query
        query = "SELECT pid, progress_pid, diskfull_pid from dataset_information where actual_filename = " + "\'" + data['filename'] + "\'" + ";"

        # Running the whole query
        mycursor.execute(query)
        results = mycursor.fetchall()

        # Close connections
        mycursor.close()
        mydb.close()

        my_table_list = {}
        my_table_list['pid'] = ""
        my_table_list['progress_pid'] = ""
        my_table_list['diskfull_pid'] = ""

        # Get all the tables present
        for table in results:
            my_table_list['pid'] = table[0]
            my_table_list['progress_pid'] = table[1]
            my_table_list['diskfull_pid'] = table[2]

        # Delete the table and all its relevant information
        try:
            # os.killpg(int(my_table_list['pid']), signal.SIGTERM)
            os.killpg(os.getpgid(int(my_table_list['pid'])), signal.SIGTERM)
        except:
            pass
        try:
            # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
            os.killpg(os.getpgid(int(my_table_list['progress_pid'])), signal.SIGTERM)
        except:
            pass
        try:
            # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
            os.killpg(os.getpgid(int(my_table_list['diskfull_pid'])), signal.SIGTERM)
        except:
            pass

        # Delete origData, json, data, info and chartsJSON
        path = "/home/ba/FAnalyzer/schemaData/origData/" + data['filename'] + ".csv"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/json/" + data['filename'] + ".json"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/data/" + data['filename'] + ".csv"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/info/" + data['filename'] + "_info.json"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + data['filename'] + "_charts.json"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + data['filename'] + "_charts.csv"
        if os.path.isfile(path):
            os.unlink(path)

        theurl = {}
        theurl['url'] = "/"
        return jsonify(theurl)
    except:
        print("Unexpected error while deleting files because of disk space issue")
        traceback.print_exc()
        raise BAServiceError("Unexpected error while deleting files because of disk space issue. Please check system logs for more details.", 500)

@application.route('/tabledelete/', methods=['POST'])
def tabledelete():
    try:
        data = request.form
        # First, check if the dataset is complete or done
        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Query
        query = "Select status, pid, progress_pid, diskfull_pid  from dataset_information where actual_filename = " + "\'" + data['filename'] + "\'" + ";"

        # Running the whole query
        mycursor.execute(query)
        results = mycursor.fetchall()

        # Close connections
        mycursor.close()
        mydb.close()

        my_table_list = {}
        my_table_list['status'] = ""
        my_table_list['pid'] = ""
        my_table_list['progress_pid'] = ""
        my_table_list['diskfull_pid'] = ""

        # Get all the tables present
        for table in results:
            my_table_list['status'] = table[0]
            my_table_list['pid'] = table[1]
            my_table_list['progress_pid'] = table[2]
            my_table_list['diskfull_pid'] = table[3]

        # For Status = Processing
        if (my_table_list['status'] == "Processing"):
            # Kill the process
            try:
                # os.killpg(int(my_table_list['pid']), signal.SIGTERM)
                os.killpg(os.getpgid(int(my_table_list['pid'])), signal.SIGTERM)
            except:
                pass
            try:
                # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
                os.killpg(os.getpgid(int(my_table_list['progress_pid'])), signal.SIGTERM)
            except:
                pass
            try:
                # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
                os.killpg(os.getpgid(int(my_table_list['diskfull_pid'])), signal.SIGTERM)
            except:
                pass

        # Delete origData, json, data, info and chartsJSON
        path = "/home/ba/FAnalyzer/schemaData/origData/" + data['filename'] + ".csv"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/json/" + data['filename'] + ".json"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/data/" + data['filename'] + ".csv"
        if os.path.isfile(path):
            os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/info/" + data['filename'] + "_info.json"
        if os.path.isfile(path):
            os.unlink(path)
        #path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + data['filename'] + "_charts.json"
        #if os.path.isfile(path):
        #    os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + data['filename'] + "_charts.csv"
        if os.path.isfile(path):
            os.unlink(path)

        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Delete row in db
        query = "DELETE FROM dataset_information WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"
        # Running the whole query
        mycursor.execute(query)
        mydb.commit()

        # Close connections
        mycursor.close()
        mydb.close()

        # Drop table in query db
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="query"
        )

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Delete table
        drop_query = "DROP TABLE IF EXISTS " + "`" + data['filename'] + "_charts" + "`" + ";"
        # Running the whole query
        mycursor.execute(drop_query)
        mydb.commit()

        # Close connections
        mycursor.close()
        mydb.close()

        # #  Return based on whether request is coming from home page or dataset page
        # if (data['page'] == "Page1"):
        #     return jsonify(data)
        theurl = {}
        theurl['url'] = "/"
        return jsonify(theurl)
    except:
        print("Unexpected error while deleting the dataset and all the related data.")
        traceback.print_exc()
        raise BAServiceError("Unexpected error while deleting the dataset. Please check system logs for more details.", 500)

@application.route('/tablererun/', methods=['POST'])
def tablererun():

    try:
        data = request.form
        # First, check if the dataset is complete or done
        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Update the minimum support in the database
        # Query
        query = "UPDATE dataset_information SET minsup = " + data['minsup'] + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"

        # Running the whole query
        mycursor.execute(query)
        # Make sure the change is retained
        mydb.commit()

        # Update the status to processing
        update_query = "UPDATE dataset_information SET status = " + "\'" + "Processing" + "\'" + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"
        # Running the whole query
        mycursor.execute(update_query)
        # Make sure the change is retained
        mydb.commit()

        # Close connections
        mycursor.close()
        mydb.close()

        # Delete chartsJSON and schemaCSV
        #path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + data['filename'] + "_charts.json"
        #if os.path.isfile(path):
        #    os.unlink(path)
        path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + data['filename'] + "_charts.csv"
        if os.path.isfile(path):
            os.unlink(path)


        @copy_current_request_context
        def func():
            shell_script = './hello_world ' + data['filename'] + '.json ' + data['minsup']
            process = subprocess.Popen(shlex.split(shell_script), shell=False, preexec_fn=os.setsid, stderr=subprocess.PIPE)
            subprocess_id = process.pid

            # Store the process id and minimum support in the database
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="db"
            )

            update_query = "UPDATE dataset_information SET pid = " + "\'" + str(subprocess_id) + "\'" + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            # Close connections
            mycursor.close()
            mydb.close()

            process.wait()

            # Read the error output if any
            std_error = process.communicate()
            actual_error = std_error[1]

            with open('/home/ba/dummy4.txt', 'w') as f:
                f.write(str(actual_error))

            # Get the status of the dataset
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
            select_query = "SELECT status FROM dataset_information WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"
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

            with open('/home/ba/dummy6.txt', 'w') as f:
                f.write(str(status_value))

            # If the disk is full then avoid setting the status again
            if status_value != "Out of Space":

                # If there is some error, then set the status as Error, else set as Ready
                if (process.returncode and actual_error):
                    update_query = "UPDATE dataset_information SET status = " + "\'" + "Error" + "\'" + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"
                else:
                    update_query = "UPDATE dataset_information SET status = " + "\'" + "Done" + "\'" + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"

                # Connections credentials and other parameters
                mydb = mysql.connector.connect(
                    # host="209.97.156.178",
                    # Uncomment the two below lines before loading to server
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="db"
                )

                # Get the cursor ready
                mycursor = mydb.cursor()

                # Running the whole query
                mycursor.execute(update_query)
                # Make sure the change is retained
                mydb.commit()

                # Close connections
                mycursor.close()
                mydb.close()

                # Remove the irrelevant files - CANNOT remove data and json because of rerun
                path = "/home/ba/FAnalyzer/schemaData/origData/" + data['filename'] + ".csv"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + data['filename'] + "_charts.json"
                if os.path.isfile(path):
                    os.unlink(path)
                # path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + data['filename'] + "_charts.csv"
                # if os.path.isfile(path):
                #     os.unlink(path)

        # Using threads
        t = threading.Thread(target=func)
        t.daemon = False
        t.start()

        # Thread 2 - For progress bar status
        @copy_current_request_context
        def func2():
            shell_script = './hello_world_100 ' + data['filename']
            process_2 = subprocess.Popen(shlex.split(shell_script), shell=False, preexec_fn=os.setsid)
            subprocess_id_2 = process_2.pid

            # Store the process id in the database
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="db"
            )

            update_query = "UPDATE dataset_information SET progress_pid = " + "\'" + str(subprocess_id_2) + "\'" + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            # Close connections
            mycursor.close()
            mydb.close()

            process_2.wait()

        # Using threads
        p = threading.Thread(target=func2)
        p.daemon = False
        p.start()

        # Thread 3 - Checking the disk space for each dataset
        @copy_current_request_context
        def func3():
            shell_script = './hello_world_1000 ' + data['filename']
            process_3 = subprocess.Popen(shlex.split(shell_script), shell=False, preexec_fn=os.setsid)
            subprocess_id_3 = process_3.pid

            # Store the process id in the database
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="db"
            )

            update_query = "UPDATE dataset_information SET diskfull_pid = " + "\'" + str(subprocess_id_3) + "\'" + " WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            # Close connections
            mycursor.close()
            mydb.close()

            process_3.wait()

            # Get the status of the dataset
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
            select_query = "SELECT status FROM dataset_information WHERE actual_filename = " + "\'" + data['filename'] + "\'" + ";"
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

            if (status_value == "Out of Space"):
                # Kill the jobs that are running
                # Connections credentials and other parameters
                mydb = mysql.connector.connect(
                    # host="209.97.156.178",
                    # Uncomment the two below lines before loading to server
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="db"
                )

                # Get the cursor ready
                mycursor = mydb.cursor()

                # Query
                query = "SELECT pid, progress_pid, diskfull_pid from dataset_information where actual_filename = " + "\'" + data['filename'] + "\'" + ";"

                # Running the whole query
                mycursor.execute(query)
                results = mycursor.fetchall()

                # Close connections
                mycursor.close()
                mydb.close()

                my_table_list = {}
                my_table_list['pid'] = ""
                my_table_list['progress_pid'] = ""
                my_table_list['diskfull_pid'] = ""

                # Get all the tables present
                for table in results:
                    my_table_list['pid'] = table[0]
                    my_table_list['progress_pid'] = table[1]
                    my_table_list['diskfull_pid'] = table[2]

                # Delete the table and all its relevant information
                try:
                    # os.killpg(int(my_table_list['pid']), signal.SIGTERM)
                    os.killpg(os.getpgid(int(my_table_list['pid'])), signal.SIGTERM)
                except:
                    pass
                try:
                    # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
                    os.killpg(os.getpgid(int(my_table_list['progress_pid'])), signal.SIGTERM)
                except:
                    pass
                try:
                    # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
                    os.killpg(os.getpgid(int(my_table_list['diskfull_pid'])), signal.SIGTERM)
                except:
                    pass

                # Remove the corresponding files
                # Delete origData, json, data, info and chartsJSON
                path = "/home/ba/FAnalyzer/schemaData/origData/" + data['filename'] + ".csv"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/json/" + data['filename'] + ".json"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/data/" + data['filename'] + ".csv"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/info/" + data['filename'] + "_info.json"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + data['filename'] + "_charts.json"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + data['filename'] + "_charts.csv"
                if os.path.isfile(path):
                    os.unlink(path)

                # Drop table in query db
                mydb = mysql.connector.connect(
                    # host="209.97.156.178",
                    # Uncomment the two below lines before loading to server
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="query"
                )

                # Get the cursor ready
                mycursor = mydb.cursor()

                # Delete table
                drop_query = "DROP TABLE IF EXISTS " + data['filename'] + "_charts" + ";"
                # Running the whole query
                mycursor.execute(drop_query)
                mydb.commit()

                # Close connections
                mycursor.close()
                mydb.close()

        # Using threads
        k = threading.Thread(target=func3)
        k.daemon = False
        k.start()

        theurl = {}
        theurl['url'] = "/ba/dataset/" + data['filename']
        return jsonify(theurl)
    except:
        print("Unexpected error while running the scripts to create data ")
        traceback.print_exc()
        raise BAServiceError("Unexpected error while running the scripts to create data. Please check system logs for more details.", 500)

@application.route('/cache_data/', methods=['POST'])
def cache_data():
    try:
        file_name = request.form
        session['file_name'] = file_name['table']
        # Open the file
        with io.open('/home/ba/FAnalyzer/schemaData/info/' + file_name['table'] + '_info.json') as json_file:
            all_data = json.load(json_file)
        return jsonify(all_data)
    except:
        print("Unexpected error in loading cache data")
        traceback.print_exc()
        raise BAServiceError("Unexpected error in loading cache data. Please check system logs for more details.", 500)

@application.route('/validatecsv/', methods=['POST'])
def validatecsv():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save('/tmp/' +  filename + ".csv")
        regex = re.compile('[!\^\'";]')
        regex_exclamation = re.compile('!')
        #regex_cap = re.compile('^')
        regex_singlequote = re.compile('\'')
        regex_doublequote = re.compile('"')
        regex_semicolon = re.compile(';')

        csv_path = '/tmp/' + file.filename + ".csv"
        csv_op_path = '/tmp/temp_upload_for_validation_' + file.filename + '.csv'

        try:
            if os.path.exists(csv_op_path):
                os.remove(csv_op_path)
        except:
            raise BAServiceError("cant delete file at path ",csv_op_path)

        exclamation = False
        singlequote = False
        doublequote = False
        semicolon = False
        try:
            ipfile = open(csv_path,'r')
            opfile = open(csv_op_path,'w')
            for ipline in ipfile.readlines():
                changedline = ipline.rstrip("\n")
                changedline = changedline.rstrip("\r")
                changedline = changedline.rstrip(",")
                #print("ipline",changedline)
                #break
                opfile.write(changedline)
                opfile.write(u'\r')
                opfile.write(u'\n')

        except:
            raise BAServiceError("cant open/write file")

        try:
            with io.open(csv_op_path, 'r') as f:
                reader = csv.reader(f)
                i = 0
                number_of_attributes_counter = 0
                for row in reader:
                    #print("row length: ",len(row))
                    #column_counter = 0
                    #for head in row:
                    #    column_counter += 1
                    #print("column counter:",column_counter)
                    #if column_counter != len(row):
                    #    raise BAServiceError("There exists data in the data set without column name to it!! Please add column name for that data", 400)
                    if (i == 0):
                        print("row is: ",row)
                        print("row length: ",len(row))
                        #column_counter = 0
                        #for head in row:
                        #    column_counter += 1
                        #print("column counter:",column_counter)
                        #if column_counter != len(row):
                        #    raise BAServiceError("There exists data in the data set without column name to it!! Please add column name for that data", 400)
                        for head in row:
                        #    print(head)
                        #    if head == None:
                        #        raise BAServiceError("There exists data in the data set without column name to it!! Please add column name for that data", 400)
                            number_of_attributes_counter += 1
                            if (regex.search(head) != None):
                                exclamation = False
                                singlequote = False
                                doublequote = False
                                semicolon = False
                                error_msg = ("Attribute names  contains invalid characters. The following character was/were found on line 0.    \n")
                                if (regex_exclamation.search(head) != None):
                                    exclamation = True
                                    #error_msg = ("Invalid characters found in the attribute names.\n"
                                    #        "The following character was found. [!] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                if (regex_singlequote.search(head) != None):
                                    singlequote = True
                                    #error_msg = ("Invalid characters found in the attribute names.\n"
                                    #        "The following character was found. ['] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                if (regex_doublequote.search(head) != None):
                                    doublequote = True
                                    #error_msg = ("Invalid characters found in the attribute names.\n"
                                    #        "The following character was found. [\"] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                if (regex_semicolon.search(head) != None):
                                    semicolon = True
                                    #error_msg = ("Invalid characters found in the attribute names.\n"
                                    #        "The following character was found. [;] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                error_msg += "  [ "
                                if exclamation:
                                    error_msg += " ! \n"
                                if singlequote:
                                     error_msg += " ' \n"
                                if doublequote:
                                    error_msg += " \" \n"
                                if semicolon:
                                    error_msg += " ; \n"
                                error_msg += " ]  "
                                error_msg += "Also check for the characters \ and ^ and remove them from the data before progressing."
                                raise BAServiceError(error_msg, 400)
                    else:
                        number_of_columns_in_a_row_counter = 0
                        for value in row:
                            number_of_columns_in_a_row_counter += 1
                            if(regex.search(value) != None):
                                print("value: ",value)
                                error_msg = 'Data contains invalid characters. The following character was/were found in the data on line number: {0}'.format(i+1)
                                exclamation = False
                                singlequote = False
                                doublequote = False
                                semicolon = False
                                if (regex_exclamation.search(value) != None):
                                    exclamation = True
                                    #error_msg = ("Data contains invalid characters.\n"
                                    #        "The following character was found in the data. [!] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                if (regex_singlequote.search(value) != None):
                                    singlequote = True
                                    #error_msg = ("Data contains invalid characters.\n"
                                    #        "The following character was found in the data. ['] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                if (regex_doublequote.search(value) != None):
                                    doublequote = True
                                    #error_msg = ("Data contains invalid characters.\n"
                                    #        "The following character was found in the data. [\"] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                if (regex_semicolon.search(value) != None):
                                    semicolon = True
                                    #error_msg = ("Data contains invalid characters.\n"
                                    #        "The following character was found in the data. [;] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                                error_msg += "\t   [ "
                                if exclamation:
                                    error_msg += " ! \n"
                                if singlequote:
                                    error_msg += " ' \n"
                                if doublequote:
                                    error_msg += " \" \n"
                                if semicolon:
                                    error_msg += " ; \n"
                                error_msg += " ] \t"
                                error_msg += ("\n"
                                        "Please delete these 6 characters [ \ ^ ! ; ' \" ] from the whole dataset before progressing.")
                                raise BAServiceError(error_msg, 400)
                                    #error_msg = ("Data contains invalid characters.\n"
                                    #        "The following character was found in the data. [\,^] Please remove this character and try again.")
                                    #raise BAServiceError(error_msg, 400)
                        if number_of_columns_in_a_row_counter != number_of_attributes_counter:
                            print(number_of_columns_in_a_row_counter)
                            print(number_of_attributes_counter)
                            error_message = "Number of Columns on line number {0} Should have been {1} but found to be {2}".format(i+1,number_of_attributes_counter,number_of_columns_in_a_row_counter)
                            raise BAServiceError(error_message,400)

                    i+= 1
            return ('', 204)
        except IOError as e:
            print("IO Error while reading the file for validation - ", csv_path, e)
            traceback.print_exc()
            raise BAServiceError("Error while reading the file - " + csv_path, 400)
        except BAServiceError as service_error:
            traceback.print_exc()
            raise service_error
        except:
            traceback.print_exc()
            raise BAServiceError("Unexpected Error while reading the file - " + csv_path + ". Please contact system administrator.", 500)
        finally:
            try:
                if os.path.exists(csv_path):
                    os.remove(csv_path)
                else:
                    print("validated CSV file cannot be deleted as it is not available.")
            except:
                # just log the exception
                print("validated CSV file cannot be deleted as it is not available.")
                traceback.print_exc()


@application.route('/checknecessarycheckbox/', methods=['POST'])
def checknecessarycheckbox():
    file = request.files['file']
    filename = secure_filename(file.filename)
    #file.save('/tmp/' +  filename + ".csv")
    csv_path = '/tmp/temp_upload_for_validation_' + file.filename + ".csv"
    #csv_path = '/tmp/' + file.filename + ".csv"
    #path = '/home/ba/FAnalyzer/schemaData/origData/' + file.filename + '.csv'
    print("CSV_Path : ",csv_path)
    try:
        encoded_lines = []
        print("before open file")
        with io.open(csv_path, "rb") as f:
            chardet_detect = chardet.detect(f.read())
            encoding = chardet_detect['encoding']
        print("reach 1")
        with io.open(csv_path, "rb") as f:
            for line in f:
                try:
                    line = unicode(line, encoding).encode("utf-8", "replace")
                except UnicodeDecodeError as e:
                    print("line - ", line)
                encoded_lines.append(line)
        print("reach 2")
        #with io.open(csv_path, 'rb') as f:
            #reader = csv.reader(f)
            #i = 0
            #for row in reader:

        with io.open("/tmp/temp_upload_for_checkbox.csv", "w") as out:
            i = 0
            for line in encoded_lines:
                line = unicode(line, "utf-8").rstrip('\r\n')
                if (i == 0):
                    header = line.rstrip().split(",")
                i+=1
                out.write(line)
                out.write(u'\n')
    except:
        print("cannot open file")
        raise BAServiceError("Error occurred while checkbox decision!!")

    try:
        if os.path.exists(csv_path):
            os.remove(csv_path)
        if os.path.exists("/tmp/temp_upload_for_checkbox.csv"):
            df = pd.read_csv("/tmp/temp_upload_for_checkbox.csv")
            os.remove("/tmp/temp_upload_for_checkbox.csv")
        new_header = []
        for head in header:
            head = head.strip()
            head = head.replace(" ", "")
            head = str(head)
            new_header.append(head)
        print("reach 3")
        header = new_header
        #print(header.length)

        #df.columns = header
        print("reach 4")
        print(df)
        #print(header.length)

        resp = {}
        attribute_names = "a"
        resp['attribute_names'] = attribute_names
        return jsonify(resp)
    except:
        raise BAServiceError("Error occurred while checkbox decision second try block!!")


@application.route('/upload/', methods=['POST'])
def upload():
    # Read the file that has been uploaded
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
        formData = request.form
    table_name = file.filename[:-4]

    # Minimum Support
    minsup = str(float(formData['minsupvalue']))
    #path = '/home/ba/FAnalyzer/schemaData/origData/' + file.filename
    path = '/tmp/temp_upload_for_validation_' + file.filename
    #try:
    #    with io.open(path, 'rb') as f:
    #        line = f.readline()
    #        header = line.rstrip().split(",")
    #
    #except IOError as e:
    #    print("IO Error while reading the header for file - ", path, e)
    #    traceback.print_exc()
    #    raise BAServiceError("Error while reading the header for file - " + path + ". Please check that the file is in correct format and/or UTF-8 encoded and try again.", 400)
    #except:
    #    traceback.print_exc()
    #    raise BAServiceError("Error while reading the header for file - " + path + ". Please check that the file is in correct format and/or UTF-8 encoded and try again.", 500)

    # Create a dataframe
    try:
        encoded_lines = []
        print("before all..")
        with io.open(path, "rb") as f:
            chardet_detect = chardet.detect(f.read())
            encoding = chardet_detect['encoding']
            print("Detected encoding - ", encoding)
        with io.open(path, "rb") as f:
            for line in f:
                try:
                    line = unicode(line, encoding).encode("utf-8", "replace")
                except UnicodeDecodeError as e:
                    print("line - ", line)
                encoded_lines.append(line)
        with io.open("/tmp/temp_upload.csv", "w") as out:
            i = 0
            for line in encoded_lines:
                line = unicode(line, "utf-8").rstrip('\r\n')
                if (i == 0):
                    header = line.rstrip().split(",")
                i+=1
                out.write(line)
                out.write(u'\n')
        print("just before 1st catch")
    except IOError as io_error:
        print("IOError occurred while converting the file encoding to UTF-8: ", path, io_error)
        traceback.print_exc()
        raise BAServiceError("Error occurred while converting the file encoding to UTF-8: " + path + ". Please check that the file is UTF-8 encoded and try again.", 400)
    except UnicodeDecodeError as decode_error:
        print("Error occurred while decoding the file using the detected encoding: ", path, decode_error)
        traceback.print_exc()
        raise BAServiceError("Error occurred while decoding the file using the detected encoding: " + path + ". Please make sure the file is UTF-8 encoded and try again.", 400)
    except UnicodeEncodeError as encode_error:
        print("Error occurred while encoding the file to UTF-8: ", path, encode_error)
        traceback.print_exc()
        raise BAServiceError("Error occurred while encoding the file to UTF-8: " + path + ". Please check that the file is UTF-8 encoded and try again.", 400)
    except BAServiceError as service_error:
        traceback.print_exc()
        raise service_error
    except:
        print("Error occurred while reading/converting the file - ", path)
        traceback.print_exc()
        raise BAServiceError("Error occurred while reading/converting the file - " + path + ". Please upload a valid  UTF-8 encoded file.", 500)
    try:
        if os.path.exists("/tmp/temp_upload.csv"):
            df = pd.read_csv("/tmp/temp_upload.csv")
            os.remove("/tmp/temp_upload.csv")

        new_header = []
        # Remove any whitespaces and store in header
        for head in header:
            head = head.strip()
            # If there is a space in the attribute name, then remove it
            head = head.replace(" ", "")
            head = str(head)
            new_header.append(head)
        header = new_header
        df.columns = header

        # Remove columns that were excluded by the user
        attributes_to_include = formData['selectedornot']
        attributes_to_include = attributes_to_include.replace("'", "\"")
        attributes_to_include = json.loads(attributes_to_include)

        if (attributes_to_include):
            for attr in attributes_to_include:
                if (attributes_to_include[attr] == "true"):
                    attr = attr.strip()
                    attr = str(attr)
                    # Remove any space in the attribute name
                    attr = attr.replace(" ", "")
                    df = df.drop(attr, 1)

        # Reset the header if columns were removed
        header = list(df.columns)
        # Count of number of numerical variables
        num_count = 0

        # Change the datatype of the columns
        schema = formData['cat_num']
        schema = schema.replace("'", "\"")
        schema = json.loads(schema)

        new_schema = {}
        # Remove any whitespaces and store in header
        for attr in schema:
            new_attr = attr.strip()
            # Remove any space in the attribute name
            new_attr = new_attr.replace(" ", "")
            new_attr = str(new_attr)
            new_schema[new_attr] = schema[attr]

        schema = new_schema
        for col_name in schema:
            col_name = str(col_name)
            if (schema[col_name] == "true"):
                # Add a try catch here in case the user inputs a wrong datatype
                try:
                    df[col_name] = df[col_name].astype(float)
                    num_count += 1
                except:
                    schema[col_name] = "false"
                    df[col_name] = df[col_name].astype(str)
            else:
                schema[col_name] = "false"
                print(col_name)
                df[col_name] = df[col_name].astype(str)

        # Store the unique values for each categorical variable
        schema_unique_values = {}
        for var in schema:
            var = var.strip()
            if (schema[var] == "false"):
                var = str(var)
                unique_values = df[var].unique().tolist()
                unique_values_per_attr = {}
                count = 0
                for un_val in unique_values:
                    value = str(count)
                    un_val = un_val.replace("'", '"')
                    unique_values_per_attr[value] = un_val
                    count += 1
                unique_values_per_attr = json.dumps(unique_values_per_attr, ensure_ascii=False)
                schema_unique_values[var] = str(unique_values_per_attr)

        # Use pandas to get summary
        summary = df.describe(include='all')
        summary = dict(summary)

        #  If numerical variables are present
        if (num_count > 0):
            summary_attributes = ['count', 'unique', 'top', 'freq', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        else:
            summary_attributes = ['count', 'unique', 'top', 'freq']
        # Very good summary but pandas_profiling is not installing
        # pandas_profiling.ProfileReport(data)

        # Store the summary data in the format of a dictionary
        full_summary = OrderedDict()
        col_names = summary.keys()

        for col in col_names:
            summary_per_column = {}
            for sum_attr in summary_attributes:
                if (pd.isna(summary[col][sum_attr])):
                    summary_per_column[sum_attr] = "NA"
                else:
                    summary_per_column[sum_attr] = summary[col][sum_attr]
            full_summary[col] = str(summary_per_column)
            #full_summary[col] = summary_per_column

        # Store the schema in session
        session['my_schema'] = schema
        session['file_name'] = table_name
        session['schema_attributes'] = schema_unique_values

        # Store the data needed to create the JSON (cache) dataset
        cache_json = {}
        cache_json["summary"] = full_summary
        cache_json["schema_attributes"] = schema_unique_values
        cache_json["file_name"] = table_name + "_info.json"
        cache_json["my_schema"] = schema
        # Set the global variable
        global actual_file_name
        actual_file_name = table_name

        # -------------------------------------- #
        # Create a JSON file for the dataset
        # -------------------------------------- #
        # Create a JSON file
        json_file = {}

        json_file["db"] = table_name
        json_file["entityTables"] = [table_name]
        json_file["nTables"] = 1
        json_file["relationTable"] = []
        json_file["tablenames"] = [str(table_name)]
        json_file["tables"] = {}

        json_file["tables"][table_name] = {}

        # Create the attribute types and attributes
        json_file["tables"][table_name]["attrTypes"] = OrderedDict()
        json_file["tables"][table_name]["attributes"] = []
        for col_name in header:
            # For attribute types
            # For numerical
            if (schema[col_name] == "true"):
                json_file["tables"][table_name]["attrTypes"][col_name] = "num"
            # For categorical
            else:
                json_file["tables"][table_name]["attrTypes"][col_name] = "cat"
        # For attributes
        json_file["tables"][table_name]["attributes"] = header

        json_file["tables"][table_name]["pk"] = []
        json_file["tables"][table_name]["exceptions"] = []
        json_file["tables"][table_name]["comparable"] = []

        # # Writing into a file
        # with open(table_name + '.json', 'w') as content:
        #     json.dump(json_file, content)

        # NOTE : We write the file here too as it needs to be accessed from Database.py
        # NOTE : Uncomment the below two lines below before loading into the server
        with open('/home/ba/FAnalyzer/schemaData/json/' + table_name + '.json', 'w') as content:
            json.dump(json_file, content)

        # NOTE : Uncomment line below before loading into the server
        path = '/home/ba/FAnalyzer/schemaData/data/' + table_name + '.csv'
        # path = table_name + '.csv'
        # Write the data into a csv file
        df.to_csv(path, sep=',', index=False, encoding='utf-8')

        # -------------------------------------- #
        # Create a JSON file future use (cache)
        # -------------------------------------- #
        with open('/home/ba/FAnalyzer/schemaData/info/' + table_name + '_info.json', 'w') as content:
        #with open(table_name + '_info.json', 'w') as content:
            json.dump(cache_json, content)

        # -------------------------------------- #
        # Set the status to processing and then run shell script
        # -------------------------------------- #

        # Connections credentials and other parameters
        mydb = mysql.connector.connect(
            # host="209.97.156.178",
            # Uncomment the two below lines before loading to server
            host="127.0.0.1",
            user="root",
            passwd="rootpass",
            port=3307,
            auth_plugin='mysql_native_password',
            database="db"
        )

        update_query = "UPDATE dataset_information SET status = " + "\'" + "Processing" + "\'" + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"

        # Get the cursor ready
        mycursor = mydb.cursor()

        # Running the whole query
        mycursor.execute(update_query)
        # Make sure the change is retained
        mydb.commit()

        # Close connections
        mycursor.close()
        mydb.close()

        @copy_current_request_context
        def func():
            shell_script = './hello_world ' + table_name + '.json ' + str(minsup)
            process = subprocess.Popen(shlex.split(shell_script), shell=False, preexec_fn=os.setsid, stderr=subprocess.PIPE)
            subprocess_id = process.pid

            # Store the process id and minimum support in the database
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="db"
            )

            update_query = "UPDATE dataset_information SET pid = " + "\'" + str(subprocess_id) + "\'" + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            update_query = "UPDATE dataset_information SET minsup = " + str(minsup) + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            # Close connections
            mycursor.close()
            mydb.close()

            process.wait()

            # Read the error output if any
            std_error = process.communicate()
            actual_error = std_error[1]

            with open('/home/ba/dummy4.txt', 'w') as f:
                f.write(str(actual_error))

            # Get the status of the dataset
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
            select_query = "SELECT status FROM dataset_information WHERE actual_filename = " + "\'" + table_name + "\'" + ";"
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

            with open('/home/ba/dummy6.txt', 'w') as f:
                f.write(str(status_value))

            # If the disk is full then avoid setting the status again
            if status_value != "Out of Space":

                # If there is some error, then set the status as Error, else set as Ready
                if (process.returncode and actual_error):
                    update_query = "UPDATE dataset_information SET status = " + "\'" + "Error" + "\'" + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"
                else:
                    update_query = "UPDATE dataset_information SET status = " + "\'" + "Done" + "\'" + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"

                # Connections credentials and other parameters
                mydb = mysql.connector.connect(
                    # host="209.97.156.178",
                    # Uncomment the two below lines before loading to server
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="db"
                )

                # Get the cursor ready
                mycursor = mydb.cursor()

                # Running the whole query
                mycursor.execute(update_query)
                # Make sure the change is retained
                mydb.commit()

                # Close connections
                mycursor.close()
                mydb.close()

                # Remove the irrelevant files - CANNOT remove data and json because of rerun
                path = "/home/ba/FAnalyzer/schemaData/origData/" + table_name + ".csv"
                if os.path.isfile(path):
                    os.unlink(path)
                #path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + table_name + "_charts.json"
                #if os.path.isfile(path):
                #    os.unlink(path)
                # path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + table_name + "_charts.csv"
                # if os.path.isfile(path):
                #     os.unlink(path)


        # Using threads
        t = threading.Thread(target=func)
        t.daemon = False
        t.start()

        # Thread 2 - For progress bar status
        @copy_current_request_context
        def func2():
            shell_script = './hello_world_100 ' + table_name
            process_2 = subprocess.Popen(shlex.split(shell_script), shell=False, preexec_fn=os.setsid)
            subprocess_id_2 = process_2.pid

            # Store the process id in the database
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="db"
            )

            update_query = "UPDATE dataset_information SET progress_pid = " + "\'" + str(subprocess_id_2) + "\'" + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            # Close connections
            mycursor.close()
            mydb.close()

            process_2.wait()

        # Using threads
        p = threading.Thread(target=func2)
        p.daemon = False
        p.start()

        # Thread 3 - Checking the disk space for each dataset
        @copy_current_request_context
        def func3():
            shell_script = './hello_world_1000 ' + table_name
            process_3 = subprocess.Popen(shlex.split(shell_script), shell=False, preexec_fn=os.setsid)
            subprocess_id_3 = process_3.pid

            # Store the process id in the database
            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="db"
            )

            update_query = "UPDATE dataset_information SET diskfull_pid = " + "\'" + str(subprocess_id_3) + "\'" + " WHERE actual_filename = " + "\'" + table_name + "\'" + ";"

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Running the whole query
            mycursor.execute(update_query)
            # Make sure the change is retained
            mydb.commit()

            # Close connections
            mycursor.close()
            mydb.close()

            process_3.wait()

            # Get the status of the dataset
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
            select_query = "SELECT status FROM dataset_information WHERE actual_filename = " + "\'" + table_name + "\'" + ";"
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

            if (status_value == "Out of Space"):
                # Kill the jobs that are running
                # Connections credentials and other parameters
                mydb = mysql.connector.connect(
                    # host="209.97.156.178",
                    # Uncomment the two below lines before loading to server
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="db"
                )

                # Get the cursor ready
                mycursor = mydb.cursor()

                # Query
                query = "SELECT pid, progress_pid, diskfull_pid from dataset_information where actual_filename = " + "\'" + table_name + "\'" + ";"

                # Running the whole query
                mycursor.execute(query)
                results = mycursor.fetchall()

                # Close connections
                mycursor.close()
                mydb.close()

                my_table_list = {}
                my_table_list['pid'] = ""
                my_table_list['progress_pid'] = ""
                my_table_list['diskfull_pid'] = ""

                # Get all the tables present
                for table in results:
                    my_table_list['pid'] = table[0]
                    my_table_list['progress_pid'] = table[1]
                    my_table_list['diskfull_pid'] = table[2]

                # Delete the table and all its relevant information
                try:
                    # os.killpg(int(my_table_list['pid']), signal.SIGTERM)
                    os.killpg(os.getpgid(int(my_table_list['pid'])), signal.SIGTERM)
                except:
                    pass
                try:
                    # os.killpg(int(my_table_list['progress_pid']), signal.SIGTERM)
                    os.killpg(os.getpgid(int(my_table_list['progress_pid'])), signal.SIGTERM)
                except:
                    pass
                try:
                    # os.killpg(int(my_table_list['diskfull_pid']), signal.SIGTERM)
                    os.killpg(os.getpgid(int(my_table_list['diskfull_pid'])), signal.SIGTERM)
                except:
                    pass

                # Remove the corresponding files
                # Delete origData, json, data, info and chartsJSON
                path = "/home/ba/FAnalyzer/schemaData/origData/" + table_name + ".csv"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/json/" + table_name + ".json"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/data/" + table_name + ".csv"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/info/" + table_name + "_info.json"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/chartsJSON/" + table_name + "_charts.json"
                if os.path.isfile(path):
                    os.unlink(path)
                path = "/home/ba/FAnalyzer/schemaData/schemaCSV/" + table_name + "_charts.csv"
                if os.path.isfile(path):
                    os.unlink(path)

                # Drop table in query db
                mydb = mysql.connector.connect(
                    # host="209.97.156.178",
                    # Uncomment the two below lines before loading to server
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="query"
                )

                # Get the cursor ready
                mycursor = mydb.cursor()

                # Delete table
                drop_query = "DROP TABLE IF EXISTS " + table_name + "_charts" + ";"
                # Running the whole query
                mycursor.execute(drop_query)
                mydb.commit()

                # Close connections
                mycursor.close()
                mydb.close()


        # Using threads
        k = threading.Thread(target=func3)
        k.daemon = False
        k.start()

        resp = {}
        resp['url'] = "/ba/dataset/" + table_name
        return jsonify(resp)
        #return redirect("/ba/dataset/" + table_name, code=302)
    except:
        print("Unexpected error in uploading the dataset")
        traceback.print_exc()
        raise BAServiceError("Unexpected error in uploading the dataset, please save the file in UTF-8 encoding and try again.\nPlease check the system logs for more details.", 500)

@application.route('/ba/dataset/')
@application.route('/ba/dataset/<dataset_name>')
def dataset_new(dataset_name):
    #if not loggedIn:
    #    return render_template('login.html')
    try:
        # Set the current filename
        print("Dataset name - ", dataset_name)
        session['file_name'] = dataset_name

        with io.open('/home/ba/FAnalyzer/schemaData/info/' + dataset_name + '_info.json') as json_file:
        # with open(dataset_name + '_info.json') as json_file:
            all_data = json.load(json_file)

        summary = all_data["summary"]
        new_summary = {}
        summary_attributes = OrderedDict()
        count = 0
        for summ_attr in summary:
            temp = summary[summ_attr]
            temp = temp.replace("'", '"')
            temp = json.loads(temp)
            new_summary[summ_attr] = temp

            # Get the list of summary attributes
            if (count == 0):
                count += 1
                temp_count = 0
                for val in temp:
                    summary_attributes[str(temp_count)] = val
                    temp_count += 1

        summary = new_summary

        schema_attributes = all_data["schema_attributes"]
        new_schema_attributes = {}
        for schema in schema_attributes:
            temp = schema_attributes[schema]
            temp = temp.replace("'", '"')
            temp = json.loads(temp)
            new_schema_attributes[schema] = temp

        schema_attributes = new_schema_attributes

        # Get the dataset name
        path = '/home/ba/FAnalyzer/schemaData/data/' + dataset_name + '.csv'
        with io.open(path, 'r') as f:
            count = 0
            top100 = {}
            for line in f:
                row = line.rstrip().split(",")
                if (count == 0):
                    header = row
                    count += 1
                elif (count < 100):
                    row_data = row
                    count += 1
                    top100[str(count)] = row_data
        dataset_data = {}
        dataset_data['summary'] = summary
        dataset_data['summary_attributes'] = summary_attributes
        dataset_data['schema_attributes'] = schema_attributes
        dataset_data['dataset_name'] = dataset_name
        dataset_data['sample_header'] = header
        dataset_data['sample_data'] = top100
        #return jsonify(dataset_data)
        return render_template('dataset.html', summary=summary, summary_attributes=summary_attributes, schema_attributes=schema_attributes, dataset_name=dataset_name, sample_header=header, sample_data=top100)
    except:
        print("Unexpected error in displaying the dataset information.")
        traceback.print_exc()
        raise BAServiceError("Unexpected error in getting the dataset information. Please check system logs for more details.", 500)

@application.route('/render/', methods=['POST'])
def render_dataset_template():
    print("Inside render method")
    data = request.get_json()
    print(data)
    summary = data['summary']
    summary_attributes = dataset_data['summary_attributes']
    schema_attributes = dataset_data['schema_attributes']
    dataset_name = dataset_data['dataset_name']
    header = dataset_data['sample_header']
    top100 = dataset_data['sample_data']
    return render_template('dataset.html', summary=summary, summary_attributes=summary_attributes, schema_attributes=schema_attributes, dataset_name=dataset_name, sample_header=header, sample_data=top100)

@application.route('/ba/search/internal', methods=['POST'])
def search_internal():
    formData = request.form
    print(type(formData))
    originalQuery = str(formData['q'])
    #display_type = str(formData.get('display_type'))
    display_type = 'plotzero'
    response = {}
    response['q'] = originalQuery
    response['show'] = display_type
    #boxplot = 'ss'
    #response['boxname'] = boxplot
    return jsonify(response)

@application.route('/ba/search/', defaults={'page': 1}, methods=['GET','POST'])
@application.route('/ba/search/<int:page>', methods=['GET','POST'])
def oneSearch(page):
    #if not loggedIn:
    #    return render_template('login.html')
    file_name = str(session.get('file_name'))
    if (file_name == 'None'):
        print("invalid access")
        return redirect('ba')
    else:
        try:
            global boxplot_numerical_attr_list
            start = (page - 1) * 10
            posts_per_page = 10
            #if (page == 1):
            #    del boxplot_numerical_attr_list[:]

            # Connections credentials and other parameters
            mydb = mysql.connector.connect(
                # host="209.97.156.178",
                # Uncomment the two below lines before loading to server
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="query"
            )

            # Get the cursor ready
            mycursor = mydb.cursor()

            # Get the query input from user
            if request.method == 'POST':
                formData = request.form
                originalQuery = str(formData["q"])
                display_type = str(formData["show"])
            else:
                originalQuery = request.args.get('q', '')
                display_type = request.args.get('show', 'plotzero').lower()
                boxname_str = request.args.get('boxname','')
            if (len(boxname_str) > 0):
                boxname_list = boxname_str.split(",")
            else:
                boxname_list = []
            if (page == 1):
                #boxname_str = ""
                del boxname_list[:]
            print("--------boxname_string------",boxname_str)
            print("-----boxname_list-----",boxname_list)
            show_plot_zero_ui = display_type == 'plotzero'
            show_favorites = display_type == 'favorites'

            with open('/home/ba/dummy4.txt', 'a+') as f:
                f.write(str(originalQuery))
                f.write("\n")
            # Build the query
            #graph_types = ['bargraph', 'groupedBargraph', 'heatmap', 'histogram', 'scatter', 'boxplot']
            graph_types = ['bargraph', 'groupedBargraph', 'histogram', 'scatter', 'boxplot']
            sorting_types = ['Score', 'Support']
            if (originalQuery == ''):
                print("Original query is empty, search all attributes.")
                query_split = ""
            else:
                query_split = originalQuery.split(";")
            conditions_attr, conditions_slice, conditions_graph, sorting_by = [[] for i in range(4)]

            # If the user has selected any query or not
            query_flag = 0

            for query_part in query_split:
                query_part = query_part.replace('|', ' ')
                if(query_part in graph_types):
                    query_flag = 1
                    if(query_part == "groupedBargraph"):
                        conditions_graph.append("grouped-bargraph")
                    else:
                        conditions_graph.append(query_part)
                elif(query_part in sorting_types):
                    query_flag = 1
                    sorting_by.append(query_part)
                elif(":" in query_part):
                    query_flag = 1
                    conditions_slice.append(query_part)
                else:
                    query_flag = 1
                    conditions_attr.append(query_part)

            # Get the filename
            # file_name = str(formData["filename"])
            #file_name = str(session.get('file_name'))
            file_name = file_name + "_charts"

            #select_query = "SELECT * FROM " +  "`" + file_name + "`" + " WHERE plottype_boundless = 'bargraph' AND "
            select_query = "SELECT * FROM " +  "`" + file_name + "`" + " WHERE plottype_boundless <> 'heatmap' AND "

            # Select statement
            # For graphs
            if (len(conditions_graph) > 0):
                select_query += "("
                for graph in conditions_graph:
                    select_query += " plottype_boundless LIKE "
                    select_query += "\'" + graph + "\'" + " OR "
                select_query = select_query[:-3]
                select_query += ") AND "
            # For attributes
            if (len(conditions_attr) > 0):
                if (len(conditions_attr) == 2):
                    plottype = "(" + "\'" + conditions_attr[0] + "\'" + ", " + "\'" + conditions_attr[1] + "\'" + ")"
                    select_query += " firstAttr IN " + plottype + " AND "
                    select_query += " secondAttr IN " + plottype + " AND "
                else:
                    select_query += " (firstAttr LIKE "
                    select_query += "\'" + conditions_attr[0] + "\'" + " OR "
                    select_query += " secondAttr LIKE "
                    select_query += "\'" + conditions_attr[0] + "\'" + ")" + " AND "
            # For slices
            if (len(conditions_slice) > 0):
                # Build strings
                all_slices = []
                for slice in conditions_slice:
                    attr_name = slice.split(':')[0]
                    attr_value = slice.split(':')[1]
                    # NOTE : The 'u' may/maynot be a problem
                    # curr_string = "[u\\\'" + attr_name + "\\\', u\\\'" + attr_value + "\\\']"
                    select_query += "`" + attr_name + "`" + " LIKE " + "\'" + attr_value + "%" + "\'" + " AND "

            # Note: Quick fix to filter the plots with score < 1.
            # TO DO: See if this is actually required or should be moved to an external script that does
            # filtering in an intelligent way.
            select_query += " score_boundless < 1 "
            if (show_plot_zero_ui):
                if (len(conditions_slice) == 0):
                    select_query += " AND support_boundless = 1"
            elif show_favorites:
                select_query += " AND is_favorite = true "

            # For sorting
            if (len(sorting_by) > 0):
                select_query += " ORDER BY "
                for orders in sorting_by:
                    if (orders == 'Score'):
                        select_query += "score_boundless ASC, "
                    else:
                        select_query += "support_boundless ASC, "

            # Remove the extra comma from the query
            if (select_query[-2] == ','):
                select_query = select_query[:-2]
            # Store the actual query
            actual_query = select_query
            # Add the final semicolon
            select_query += ";"

            # Check if any conditions have been given by the user
            if (query_flag == 1):
                # Remove extra spaces
                select_query = " ".join(select_query.split())
                # Replace * with COUNT(*)
                select_query = select_query.replace("*", "COUNT(*)")
            else:
                select_query = "SELECT * FROM " + "`" + file_name + "`" + " WHERE score_boundless < 1 "
                if show_plot_zero_ui:
                    select_query += " AND support_boundless = 1 "
                elif show_favorites:
                    select_query += " AND is_favorite = true "
                actual_query = select_query
                # TODO:FOR  DEMO, enable only bar graphs.
                #actual_query += " AND plottype_boundless = 'bargraph'"
                actual_query += " AND plottype_boundless <> 'heatmap'"
                #select_query = "SELECT COUNT(*) FROM " + "`" + file_name + "`" + " WHERE score_boundless < 1 AND plottype_boundless = 'bargraph'"
                select_query = "SELECT COUNT(*) FROM " + "`" + file_name + "`" + " WHERE score_boundless < 1 AND plottype_boundless <> 'heatmap'"
                if (show_plot_zero_ui):
                    if (len(conditions_slice) == 0):
                        select_query += " AND support_boundless = 1"
                elif show_favorites:
                    select_query += " AND is_favorite = true "
                select_query += ";"

            #check if we have slice in the query.
            if (len(conditions_slice) > 0 and show_plot_zero_ui):
                # filter the results with exactly the same slice.
                # We will get this by first finding the max support from all these results
                # and then finding the result that has other attributes = 'NA'.
                actual_query_for_max_support = actual_query
                print("Query for max support - ", actual_query_for_max_support)
                mycursor.execute(actual_query_for_max_support)
                results_max_support = mycursor.fetchall()
                if (len(results_max_support) > 0):
                    sp_list = []
                    for i in range(len(results_max_support)):
                        tup = results_max_support[i]
                        sp_list.append(tup[3])

                    max_support_for_slice = max(sp_list)
                    actual_query += " AND support_boundless = " + max_support_for_slice
                else:
                    print("Query for getting max support returned zero results.")
            else:
                actual_query += " ORDER BY score_boundless DESC, support_boundless DESC "


            column_query = "SHOW COLUMNS FROM " + "`" + file_name + "`" + ";"
            mycursor.execute(column_query)
            column_results = mycursor.fetchall()
            # Extract the column names from the result
            col_names = []
            for col in column_results:
                col_names.append(col[0])
            col_names = col_names[:-2];
            with open('/home/ba/dummy7.txt', 'w') as f:
                f.write(str(col_names))
                f.write(str("\n"))

            if (len(conditions_slice) > 0 and show_plot_zero_ui):
                col_names_trimmed = [e for e in col_names if e not in {'firstAttr', 'secondAttr', 'score_boundless', 'support_boundless', 'url', 'plottype_boundless', attr_name}]
                query_clause = ""

                for col in col_names_trimmed:
                    query_clause += '`' + col + '`' + '= "NA" AND '
                # trim the last AND from the query_clause.
                query_clause = query_clause[:-4]
                # append the query_clause to the actual_query.
                actual_query += " AND " + query_clause
                # Update select_query to get the number of results here as we now have multiple conditions added because of slice in the query and show_plot_zero_ui = True
                select_query = actual_query
                select_query += ";"
                select_query = select_query.replace("*", "COUNT(*)")

            # Execute select_query to get the total count of the results.
            print("Select query - ", select_query)
            mycursor.execute(select_query)
            results = mycursor.fetchall()

            # Add limit for pagination.
            actual_query += " LIMIT " + str(start) + ", " + str(posts_per_page) + ";"
            print("actual query - ", actual_query)

            with open('/home/ba/dummy5.txt', 'a+') as f:
                f.write(str(actual_query))
                f.write(str("\n"))

            # Execute actual_query to get results.
            mycursor.execute(actual_query)
            current_results = mycursor.fetchall()

            with open('/home/ba/dummy6.txt', 'w') as f:
                f.write(str(current_results))
                f.write(str("\n"))

            # Get data ready to send out
            final_data = {}
            # final_data['numFound'] = len(results)
            final_data['numFound'] = results[0][0]
            noOfPlotsCount = int(final_data['numFound'])
            # nrecords = len(results)
            nrecords = results[0][0]
            final_data['docs'] = []
            final_data['selected'] = originalQuery

            # Store the output received
            count = len(current_results)
            print("current_results: ",current_results)
            #for i in range(0, len(current_results)):
            #    print('plottype :', current_results[i][4])
            #print("List with page - ", boxplot_numerical_attr_list, "::", page)
            current_plottype = ""
            for i in range(0, len(current_results)):
                #if (current_results[i][4] == 'boxplot'):
                #    if current_results[i][1] in boxname_list:
                #        continue
                #    else:
                #        boxname_list.append(current_results[i][1])
                data_dict = {}
                # current_result[i] - 2 to ignore the last 2 columns (is_favorite, comments)
                for j in range(0, len(current_results[i]) - 2):
                    data_dict[col_names[j]] = current_results[i][j]
                # To display the attributes this plot object represents.
                current_plottype = current_results[i][4]
                data_dict['x_attribute'] = current_results[i][0]
                x_val_for_query = data_dict['x_attribute']
                data_dict['y_attribute'] = current_results[i][1]
                y_val_for_query = data_dict['y_attribute']
                cache_table = file_name[:-6]
                cache_table += "cache"
                #scores_query = "SELECT slice_size FROM " + "`" + cache_table  + "`" + " WHERE first_attr = '" + x_val_for_query + "'" + " AND second_attr = '" + y_val_for_query + "'"
                if current_plottype == 'boxplot':
                    data_query = "SELECT data FROM " + "`" + cache_table + "`" + " WHERE first_attr = '" + x_val_for_query + "'" + " AND second_attr = '" + y_val_for_query + "'" + " AND acceptable_slice_size = True" + " AND plottype = '" + current_plottype + "'"
                    mycursor.execute(data_query)
                    data_results_for_boxplots = mycursor.fetchall()
                    min_y_from_data = 1000000000000
                    max_y_from_data = -1000000000000
                    for count in range(0, len(data_results_for_boxplots)):
                        req_string = data_results_for_boxplots[count][0][2:]
                        req_string = req_string.split(']')
                        req_string = req_string[0]
                        req_string = req_string.split(',')
                        if int(float(req_string[0])) < min_y_from_data:
                            min_y_from_data = int(float(req_string[0]))
                        if int(float(req_string[4])) > max_y_from_data:
                            max_y_from_data = int(float(req_string[4]))
                    counter_no_of_slices_boxplot = 0
                    for count in range(0, len(data_results_for_boxplots)):
                        req_string = data_results_for_boxplots[count][0][2:]
                        req_string = req_string.split(']')
                        req_string = req_string[0]
                        req_string = req_string.split(',')
                        if int(float(req_string[3])) - int(float(req_string[1])) >= ((max_y_from_data-min_y_from_data)/6):
                            counter_no_of_slices_boxplot += 1
                    actualNoOfSlices = counter_no_of_slices_boxplot
                    if x_val_for_query == 'JobLevel':
                        print("min data for duration is ",min_y_from_data)
                        print("max data for duration is ",max_y_from_data)
                    #print(data_results_for_boxplots)
                else:
                    scores_query = "SELECT count(*) FROM " + "`" + cache_table  + "`" + " WHERE first_attr = '" + x_val_for_query + "'" + " AND second_attr = '" + y_val_for_query + "'" + " AND acceptable_slice_size = True" + " AND plottype = '" + current_plottype + "'"
                    mycursor.execute(scores_query)
                    scores_results_for_no_of_slices = mycursor.fetchall()
                    #print(len(scores_results_for_no_of_slices))
                    #scores_results_for_no_of_slices = scores_results_for_no_of_slices[:-1]
                    #scores_results_for_no_of_slices = scores_results_for_no_of_slices[1:]
                    #for x in scores_results_for_no_of_slices:
                    data_dict['noOfSlicesForChart'] = str(scores_results_for_no_of_slices)
                    charlist = ["[", "(", ")", "]", ","]
                    actualNoOfSlices = ""
                    for count in range(len(data_dict['noOfSlicesForChart'])):
                        if data_dict['noOfSlicesForChart'][count] in charlist:
                            #print("in continue")
                            continue
                        actualNoOfSlices += data_dict['noOfSlicesForChart'][count]
                    print("No of slices : ", len(data_dict['noOfSlicesForChart']))
                    print("actual slice: ",actualNoOfSlices)
                if actualNoOfSlices == 0:
                    noOfPlotsCount -= 1
                    continue
                data_dict['noOfSlicesForChart'] = actualNoOfSlices
                data_dict['id_value'] = i * count + j
                if (show_favorites and current_results[i][-1] is not None):
                    data_dict['comments'] = current_results[i][-1]
                final_data['docs'].append(data_dict)
            final_data['numFound'] = str(noOfPlotsCount)
            final_data['start'] = start
            boxname_str_op =  ','.join(boxname_list)
            #final_data['boxplot'] = boxname_str_op
            print("List with page after ", boxname_str_op, "::", page)

            # get the spread of the plot and add it to the result.
            slice_clause_spread = ""
            if (len(conditions_slice) > 0 and show_plot_zero_ui):
                for each_slice in conditions_slice:
                    attr_name = each_slice.split(":")[0]
                    attr_value = each_slice.split(":")[1]
                    slice_clause_spread += "`" + attr_name + "`" + " LIKE " + "\'" + attr_value + "%\'" + " AND "
            slice_clause_spread = slice_clause_spread[:-4]
            for i in range(len(final_data['docs'])):
                inner_dict = final_data['docs'][i]
                query = "SELECT MAX(score_boundless), MIN(score_boundless) FROM " + "`" + file_name + "`" + " WHERE "
                query += "firstAttr = " + "\'" + inner_dict['x_attribute'] + "\'" + " AND secondAttr = " + "\'" + inner_dict['y_attribute'] + "\'"
                if (slice_clause_spread != ""):
                    query += " AND " + slice_clause_spread
                query += ";"
                mycursor.execute(query)
                results_spread = mycursor.fetchone()
                max_score = float(results_spread[0])
                min_score = float(results_spread[1])
                spread = max_score - min_score
                inner_dict['rating'] = round(spread * 10) * 10
            mycursor.close()
            mydb.close()

            pagination = Pagination(page=page, per_page=posts_per_page, total=nrecords, href="http://www.foreveranalytics.com/ba/search/{0}?q=" + originalQuery + "&show=" + display_type + "&boxname=" + boxname_str_op)

            param = {}
            param['q'] = originalQuery
            param['show'] = display_type
            param['boxname'] = boxname_str_op
            print("parameters - ", param)
            return render_template('searchresults.html', results=final_data, pagination=pagination, params=param)
        except:
            print("Unexpected error in searching the dataset.")
            traceback.print_exc()
            raise BAServiceError("Unexpected error in searching the dataset for plots. Please check the system logs for more details.", 500)


@application.route('/ba/search/bounds/plotzeroshift/', methods=['POST'])
def sort_charts_per_score():
    try:
        sort_array_object = request.get_json()
        sort_array = sort_array_object['new_global_charts_per_score']
        plot_zero_data = sort_array_object['plotZeroData']
        print("Plot zero data: ",plot_zero_data)

        plot_data_type = sort_array[0][1][4]
        print("Plot data type: ",plot_data_type)

        if (plot_data_type == 'boxplot'):
            for chart_arr in sort_array:
                value = chart_arr[0]
                compare_list = value[0]
                value[1] = round(abs(compare_list[2] - plot_zero_data[2]), 2)
            sort_array = sorted(sort_array, key = lambda chart_arr: chart_arr[0][1], reverse=True)
        elif (plot_data_type == 'percentile'):
            for chart_arr in sort_array:
                value = chart_arr[0]
                compare_list = value[0]
                value[1] = round(abs(compare_list[9] - plot_zero_data[9]), 2)
            sort_array = sorted(sort_array, key = lambda chart_arr: chart_arr[0][1], reverse=True)
        elif (plot_data_type == 'histogram'):
            for chart_arr in sort_array:
                value = chart_arr[0]
                inner_dict = {}
                compare_list = value[0]
                for compare_val in compare_list:
                    if isinstance(compare_val, tuple):
                        inner_dict[compare_val[0]] = compare_val[1]
                for plot_zero_val in plot_zero_data:
                    if isinstance(plot_zero_val, tuple):
                        if plot_zero_val[0] in inner_dict:
                            inner_dict[plot_zero_val[0]] = round(abs(inner_dict[plot_zero_val[0]] - plot_zero_val[1]), 2)
                        else:
                            inner_dict[plot_zero_val[0]] = plot_zero_val[1]
                value[1] = round(sum(inner_dict.values()), 2)
            sort_array = sorted(sort_array, key = lambda chart_arr: chart_arr[0][1], reverse=True)
        elif (plot_data_type == 'bargraph'):
            for chart_arr in sort_array:
                value = chart_arr[0]
                inner_dict = {}
                compare_list = value[0]
                for compare_val in compare_list:
                    if isinstance(compare_val, list):
                        inner_dict[compare_val[0]] = compare_val[1]
                for plot_zero_val in plot_zero_data:
                    if isinstance(plot_zero_val, list):
                        if plot_zero_val[0] in inner_dict:
                            inner_dict[plot_zero_val[0]] = round(abs(inner_dict[plot_zero_val[0]] - plot_zero_val[1]), 2)
                        else:
                            inner_dict[plot_zero_val[0]] = plot_zero_val[1]
                value[1] = round(sum(inner_dict.values()), 2)
            sort_array = sorted(sort_array, key = lambda chart_arr: chart_arr[0][1], reverse=True)
        else:
            print("invalid plot type")



        objToSendBack = {}
        objToSendBack['new_global_charts_per_score'] = sort_array
        resp = json.dumps(objToSendBack);
        return Response(response=resp, status=200, mimetype="application/json")
    except:
        traceback.print_exc()
        raise BAServiceError("Exception occurred while sorting charts_per_score array", 500)

@application.route('/ba/search/bounds/', methods=['POST'])
def search_by_bounds():
    try:
        attributes = request.get_json()
        file_name = str(session.get('file_name'))
        if (file_name == 'None'):
            #the API has been called directly, redirect to the home page.
            return redirect('ba')
        else:
            file_name = file_name + "_charts"
            print("File name - ", file_name)
            if (attributes is not None):
                first_attr = attributes['firstAttr']
                second_attr = attributes['secondAttr']
                query_slices = attributes['slices'];
                chart_type = attributes['chartType']
                # MySQL query to find the minimum and maximum score from the database.
                mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    passwd="rootpass",
                    port=3307,
                    auth_plugin='mysql_native_password',
                    database="query"
                )

                if (query_slices is not None):
                    query_slice_dict = {}
                    for i in range(len(query_slices)):
                        attr = query_slices[i].split(":")[0]
                        value = query_slices[i].split(":")[1]
                        query_slice_dict[attr] = value

                mycursor = mydb.cursor()
                # get the columns to map them to the values obtained for min, max charts. So that we can display the corresponding slices on the UI.
                columns_query = "SHOW COLUMNS FROM " + "`" + file_name + "`" + ";"
                mycursor.execute(columns_query)
                columns = mycursor.fetchall()
                col_names = [col[0] for col in columns]
                # Not include the is_favorite, comments columns
                col_names = col_names[:-2]

                #Get the plots from the cache table.
                table_name = file_name[:-6] + "cache"
                scores_query = "SELECT slice, data, metadata, slice_size FROM " + "`" + table_name + "`" + " WHERE first_attr = '" + first_attr + "'" + " AND second_attr = '" + second_attr + "'"
                if (chart_type == 'histogram'):
                    scores_query += " AND plottype = 'histogram'"
                    scores_query += ";"
                if (chart_type == 'percentile'):
                    scores_query += " AND plottype = 'percentile'"
                    scores_query += ";"
                if (chart_type == 'boxplot'):
                    scores_query += " AND plottype = 'boxplot'"
                    scores_query += ";"
                mycursor.execute(scores_query)
                scores_results = mycursor.fetchall()
                print("length of scores results", len(scores_results))
                print("actual score results: ",scores_results)
                bins_metadata_results = None
                if (chart_type == 'histogram'):
                    query = "SELECT bins_metadata FROM " + "`" + table_name + "_histogram" + "`" + " WHERE first_attr = '" + first_attr + "'" + ";"
                    mycursor.execute(query)
                    bins_metadata_results = mycursor.fetchone()

                #csv_path = "/home/ba/FAnalyzer/schemaData/data/" + file_name[:-7] + ".csv"
                #data_table = csv_path.replace('/home/ba/FAnalyzer/schemaData/data/','')
                #data_table = data_table[:-4] + '_data'
                #with io.open(csv_path, 'rb') as f:
                #    line_zero = f.readline()
                #    new_header = line_zero.rstrip().split(',')
                #print(new_header)
                #mycursor.execute('CREATE TABLE ' + data_table + '')

                #csv_data = csv.reader(file(csv_path))
                #for row in csv_data
                #    mycursor.execute('CREATE TABLE ' + data_table + '')
                # Close DB connections
                mycursor.close()
                mydb.close()

                charts_per_score_old = []
                csv_path = "/home/ba/FAnalyzer/schemaData/data/" + file_name[:-7] + ".csv"
                df_actual_data = pd.read_csv("/home/ba/FAnalyzer/schemaData/data/" + file_name[:-7] + ".csv", encoding="utf-8-sig")
                print(df_actual_data)

                plotzero_chart = None
                plotzero_metadata = None
                max_y_scale = -100000000000000
                min_y_scale = 100000000000000
                max_x_scale = 0

                header = None
                #with io.open(csv_path, 'rb') as f:
                #    line_zero = f.readline()
                #    header = line_zero.rstrip().split(',')
                st = time.time()
                printval = True
                first_plot_on_right = True
                first_plot_on_right_arr = []
                for i in range(len(scores_results)):
                    loop_back = False
                    slice_val = json.loads(scores_results[i][0])
                    for k, v in query_slice_dict.items():
                        if  (k not in slice_val or (k in slice_val and slice_val[k] != v)):
                            loop_back = True
                            break
                    if loop_back:
                        continue
                    metadata = json.loads(scores_results[i][2])
                    data = json.loads(scores_results[i][1])
                    slice_size = scores_results[i][3]
                    if int(slice_size) < 5:
                        #print("in continue")
                        continue
                    #print("slice_size",slice_size)
                    if (bins_metadata_results is not None):
                        bins_metadata_dict = json.loads(bins_metadata_results[0])
                        max_x = bins_metadata_dict['max']
                        min_x = bins_metadata_dict['min']
                        num_bins = int(bins_metadata_dict['bins'])
                        bin_width = math.ceil((max_x - min_x) / float(num_bins))
                        bins = []
                        bins.append(min_x)
                        next_start = min_x
                        for i in range(num_bins):
                            next_start = next_start + bin_width
                            bins.append(next_start)
                        # Add data to bins based on the bin width.
                        [data_binned, bins] = np.histogram(data[0], bins)
                        data[0] = dict(zip(bins, data_binned))
                        sum_values = sum(data[0].values())
                        for k, v in data[0].items():
                            data[0][k] = round(data[0][k] * 100 / float(sum_values), 2)
                        # sort the values in increasing order of the key (bin).
                        # This is required for the highcharts library to display the chart properly.
                        data[0] = sorted(data[0].items(), key=lambda k: k[0])
                        freq_values = [ele[1] for ele in data[0]]
                        max_local = max(freq_values)
                        max_x_local = max_x
                        if (max_local > max_y_scale):
                            max_y_scale = max_local
                        if (math.ceil(max_x_local) > max_x_scale):
                            max_x_scale = math.ceil(max_x_local)
                    scores_result_filtered = [res for res in metadata[6:-2] if res != 'NA']
                    if (chart_type == 'boxplot' or chart_type == 'percentile' ):
                        max_local = data[0][4]
                        min_local = data[0][0]
                        if (max_local > max_y_scale):
                            max_y_scale = max_local
                        if (min_local < min_y_scale):
                            min_y_scale = min_local
                    elif chart_type == 'bargraph':
                        local_data = data[0]
                        max_local = max([d[1] for d in local_data])
                        if max_local > max_y_scale:
                            max_y_scale = math.ceil(max_local / 10.0) * 10
                    if (len(query_slices) == 0):
                        if (chart_type == 'boxplot' or chart_type == 'percentile'):
                            if (len(slice_val) == 0):
                                plotzero_chart = data
                                plotzero_metadata = metadata
                        elif (len(scores_result_filtered) == 0):
                            plotzero_chart = data
                            plotzero_metadata = metadata
                    elif (chart_type == 'boxplot' or chart_type == 'percentile'):
                        import copy
                        copy_slices = copy.deepcopy(slice_val)
                        copy_slices.pop(first_attr)
                        if (query_slices.keys() == copy_slices.keys()):
                            plotzero_chart = data
                            plotzero_metadata = metadata
                    elif (len(scores_result_filtered) == len(query_slices)):
                        plotzero_chart = data
                        plotzero_metadata = metadata
                    #stringForDataSelection = ""
                    #print(slice_val)
                    keysarray = []
                    valuesarray = []
                    #if len(slice_val) != 0:
                    #    allRecordsFlag = 0
                    #    for dictkey, dictval in slice_val.iteritems():
                           #stringForDataSelection += '(df_actual_data['"'"+dictkey+"'"'] == '"'"+dictval+"'"') & '
                    #        keysarray.append(dictkey)
                    #        valuesarray.append(dictval)
                    #else:
                    #    allRecordsFlag = 1
                    #if len(stringForDataSelection) > 0:
                        #stringForDataSelection = stringForDataSelection[:-3]
                        #print(stringForDataSelection)
                        #df_small = df_actual_data.loc[stringForDataSelection]
                        #a_String = ""
                        #a_String += (df_actual_data['DRINK'] == 'None')
                        #df_small = df_actual_data.loc["(df_actual_data['DRINK'] == 'None')"]
                        #df_small = df_actual_data.loc[a_string]
                        #print(df_small)
                        #print(len(df_small))

                    #df_actual_data_for_this_slice = df_actual_data
                    #for val in range(len(keysarray)):
                       # keyvalue = keysarray[val]
                       # valuevalue = valuesarray[val]
                      #  print("keyvalue",keyvalue)
                     #   df_actual_data_for_this_slice = df_actual_data_for_this_slice[df_actual_data_for_this_slice.keyvalue.isin(valuesarray)]

                    #print(df_actual_data_for_this_slice)
                    #print(len(df_actual_data_for_this_slice))
                    #if (chart_type == 'boxplot'):
                    #    if ((int(data[0][3]) - int(data[0][1])) < ((int(max_y_scale) - int(min_y_scale))/6)):
                    #        continue
                    #print('max value: ',data[0][4])
                    #print('small diff: ',int(data[0][3]) - int(data[0][1]))
                    #print('big diff: ',(int(max_y_scale) - int(min_y_scale))/6)
                    if (first_plot_on_right):
                        first_plot_on_right = False;
                        first_plot_on_right_arr.append(data)
                        first_plot_on_right_arr.append(metadata)
                        first_plot_on_right_arr.append(slice_val)
                        first_plot_on_right_arr.append(slice_size)
                        continue

                    chart_obj = []
                    chart_obj.append(data)
                    chart_obj.append(metadata)
                    chart_obj.append(slice_val)
                    chart_obj.append(slice_size)
                    charts_per_score_old.append(chart_obj)

                #Add first plot on right at last position
                chart_obj = []
                for first_plot_on_right_item in first_plot_on_right_arr:
                    chart_obj.append(first_plot_on_right_item)

                charts_per_score_old.append(chart_obj)

                charts_per_score = []
                print("old length: ",len(charts_per_score_old))
                print("bounds min y: ",int(min_y_scale))
                print("bounds max y:",int(max_y_scale))
                if (chart_type == 'boxplot'):
                    for count in range(0, len(charts_per_score_old)):
                        #print(int(charts_per_score_old[count][0][0][1]))
                        #print("In bounds",int(charts_per_score_old[count][0][0][3]) - int(charts_per_score_old[count][0][0][1]))
                        #print((int(max_y_scale) - int(min_y_scale))/6)
                        #print("bounds min y: ",int(min_y_scale))
                        #print("bounds max y:",int(max_y_scale))
                        if ((int(charts_per_score_old[count][0][0][3]) - int(charts_per_score_old[count][0][0][1])) >= ((int(max_y_scale) - int(min_y_scale))/6)):
                            #print('count++')
                            charts_per_score.append(charts_per_score_old[count])
                else:
                    import copy
                    charts_per_score = copy.deepcopy(charts_per_score_old)
                print("Number of charts - ", len(charts_per_score))
                if (chart_type == 'bargraph'):
                    plot_zero_value = plotzero_chart[0]
                    for chart_obj in charts_per_score:
                        value = chart_obj[0]
                        inner_dict = {}
                        compare_list = value[0]
                        for compare_val in compare_list:
                            if isinstance(compare_val, list):
                                inner_dict[compare_val[0]] = compare_val[1]
                        for plot_zero_val in plot_zero_value:
                            if isinstance(plot_zero_val, list):
                                if plot_zero_val[0] in inner_dict:
                                    inner_dict[plot_zero_val[0]] = round(abs(inner_dict[plot_zero_val[0]] - plot_zero_val[1]), 2)
                                else:
                                    inner_dict[plot_zero_val[0]] = plot_zero_val[1]
                        value[1] = round(sum(inner_dict.values()), 2)
                    charts_per_score = sorted(charts_per_score, key = lambda chart_obj: chart_obj[0][1], reverse=True)
                elif (chart_type == 'histogram'):
                    plot_zero_value = plotzero_chart[0]
                    for chart_obj in charts_per_score:
                        value = chart_obj[0]
                        inner_dict = {}
                        compare_list = value[0]
                        for compare_val in compare_list:
                            if isinstance(compare_val, tuple):
                                inner_dict[compare_val[0]] = compare_val[1]
                        for plot_zero_val in plot_zero_value:
                            if isinstance(plot_zero_val, tuple):
                                if plot_zero_val[0] in inner_dict:
                                    inner_dict[plot_zero_val[0]] = round(abs(inner_dict[plot_zero_val[0]] - plot_zero_val[1]), 2)
                                else:
                                    inner_dict[plot_zero_val[0]] = plot_zero_val[1]
                        value[1] = round(sum(inner_dict.values()), 2)
                    charts_per_score = sorted(charts_per_score, key = lambda chart_obj: chart_obj[0][1], reverse=True)
                elif (chart_type == 'scatter'):
                    for chart_obj in charts_per_score:
                        value = chart_obj[0]
                        value[1] = abs(float(plotzero_metadata[2]) - float(chart_obj[1][2]))
                    charts_per_score = sorted(charts_per_score, key = lambda chart_obj: chart_obj[0][1])
                elif (chart_type == 'boxplot'):
                    plot_zero_value = plotzero_chart[0]
                    for chart_obj in charts_per_score:
                        value = chart_obj[0]
                        compare_list = value[0]
                        value[1] = round(abs(compare_list[2] - plot_zero_value[2]), 2)
                    print("old charts per score: ",charts_per_score)
                    charts_per_score = sorted(charts_per_score, key = lambda chart_obj: chart_obj[0][1], reverse=True)
                    print("new charts per score :",charts_per_score)
                elif (chart_type == 'percentile'):
                    plot_zero_value = plotzero_chart[0]
                    for chart_obj in charts_per_score:
                        value = chart_obj[0]
                        compare_list = value[0]
                        value[1] = round(abs(compare_list[9] - plot_zero_value[9]), 2)
                    charts_per_score = sorted(charts_per_score, key = lambda chart_obj: chart_obj[0][1], reverse=True)
                else:
                    print("Invalid plot type.")

                charts_scale = {}
                charts_scale['max'] = max_y_scale
                charts_scale['min'] = min_y_scale
                charts_scale['max_x'] = max_x_scale
                #print('charts_scale : debug = ', charts_scale)
                charts = {}
                charts['columns'] = col_names
                charts['charts_per_score'] = charts_per_score
                charts['plotzero_chart'] = plotzero_chart[0]
                charts['plotzero_metadata'] = plotzero_metadata
                charts['scale'] = charts_scale
                et = time.time()
                resp = json.dumps(charts)
                print("elapsed time = ", (et - st))
                #for count_new in range(0, len(charts['charts_per_score'])):
                    #print("charts per score",charts['charts_per_score'][count_new][2])
                #print("charts per score",charts['charts_per_score'][-1])
                return Response(response=resp, status=200, mimetype="application/json")
            else:
                print("Attributes are not available.")
                raise BAServiceError("Attributes for search not available. Please check if the dataset is loaded properly and try again.", 400)
    except:
        print("Exception occurred while searching the charts with minimum and maximum scores.")
        traceback.print_exc()
        raise BAServiceError("Exception occurred while searching the charts with minimum and maximum scores.", 500)


@application.route('/ba/search/markfavorite/', methods = ['POST'])
def mark_favorite():
    try:
        request_data = request.get_json()
        file_name = str(session.get('file_name'))
        file_name = file_name + "_charts"
        print("request - ", request_data)
        metadata = request_data['metadata']
        cols = request_data['cols']
        firstAttr = metadata[0]
        secondAttr = metadata[1]
        score = metadata[2]
        support = metadata[3]
        comments = request_data['comments']

        mydb = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="query"
        )
        mycursor = mydb.cursor()
        query_statement = " UPDATE " + "`" + file_name + "`" + " SET is_favorite = true, comments = '" + comments + "'" + " WHERE "
        query_statement += " firstAttr = '" + firstAttr + "'" + " AND secondAttr = '" + secondAttr + "'"
        query_statement += " AND score_boundless = " + score + " AND support_boundless = " + support + ";"
        #print("query = ", query_statement)
        mycursor.execute(query_statement)
        mydb.commit()
        # close connection
        mycursor.close()
        mydb.close()
        return jsonify(success=True)
    except:
        print("Exception occurred while marking the chart as favorite.")
        traceback.print_exc()
        raise BAServiceError("Datastore exception occurred while marking the chart as favorite.", 500)


@application.route('/ba/search/slices/compare/', methods = ['POST'])
def search_slice_attributes():
    try:
        request_data = request.get_json()
        file_name = str(session.get('file_name'))
        file_name = file_name + "_charts"
        if (request_data is not None):
            # get all the attributes.
            variable_attr = request_data['variable']
            slice_dict = request_data['slice']
            reference_chart = request_data['reference']
            first_attr = reference_chart[0]
            second_attr = reference_chart[1]
            result_dict = {}
            # get database connection.
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                passwd="rootpass",
                port=3307,
                auth_plugin='mysql_native_password',
                database="query"
            )
            csv_path = "/home/ba/FAnalyzer/schemaData/data/" + file_name[:-7] + ".csv"
            df = pd.read_csv(csv_path, encoding="utf-8")
            unique_values_for_variable = list(df[variable_attr].unique())

            mycursor = mydb.cursor()
            columns_query = "SHOW COLUMNS FROM " + "`" + file_name + "`" + ";"
            mycursor.execute(columns_query)
            columns = mycursor.fetchall()
            col_names = [col[0] for col in columns]
            #Don't include the is_favorite column.
            col_names = col_names[:-1]
            variable_cols = col_names[6:]
            for var in variable_cols:
                if var not in slice_dict:
                    slice_dict[var] = 'NA'

            query_statement = "SELECT * FROM " + "`" + file_name + "`" + " WHERE "
            query_statement += " firstAttr = '" + first_attr + "'" + " AND secondAttr = '" + second_attr + "'" + " AND "
            for key, value in slice_dict.items():
                if key != variable_attr:
                    query_statement += "`" + key + "`" + "=" + "'" + value + "'" + " AND "
            query_statement += "`" + variable_attr + "`" + "<>" + "'NA';"

            mycursor.execute(query_statement)
            results = mycursor.fetchall()

            result_list = []
            for i in range(len(results)):
                df1 = df
                result_metadata = results[i]
                for j in range(6, len(col_names)):
                    if (result_metadata[j] != 'NA'):
                        df1 = df1[df1[col_names[j]] == result_metadata[j]]
                if (second_attr != 'NA'):
                    value = list(zip(df1[first_attr], df1[second_attr]))
                result_object = {}
                result_object['metadata'] = result_metadata
                result_object['chart_data'] = value
                result_list.append(result_object)

            mycursor.close()
            mydb.close()
            result_dict['results'] = result_list
            return jsonify(result_dict)
    except:
        traceback.print_exc();
        raise BAServiceError("Exception in reading unique values for attributes in the slice.", 500)


@application.route('/ba/download/<dataset_name>')
def download_dataset(dataset_name):
    #if not loggedIn:
    #    return render_template('login.html')
    try:
        print("Downloading dataset - ", dataset_name)
        file_name = dataset_name + ".csv"
        file_path = "/home/ba/FAnalyzer/schemaData/data/" + file_name
        if (os.path.exists(file_path)):
            return send_from_directory("/home/ba/FAnalyzer/schemaData/data", file_name, mimetype="text/csv", as_attachment=True)
        else:
            raise BAServiceError("Requested dataset is not available on the server", 400)
    except IOError as io_error:
        print("Error occurred while downloading the dataset - ", dataset_name, io_error)
        traceback.print_exc()
        raise BAServiceError("Error occurred while downloading the dataset - " + dataset_name, 400)

# @application.route('/ba/plot/<string:plotdata>')
# def showPlot(plotdata):
#     decoded = base64.b64decode(plotdata)
#     return render_template('chart.html', plot_data=decoded)

# @application.route('/form/search/', defaults={'page': 1})
# @application.route('/form/search/<int:page>')
# def searchpagestemplate(page):
#     start = (page - 1) * 10
#
#     param = {}
#     param['dataset'] = request.args.get('dataset', 'any')
#     param['plottype'] = request.args.get('plottype', 'any')
#     param['support'] = request.args.get('minsup', 'any')
#     param['minmark'] = request.args.get('minmark', 'any')
#     param['maxmark'] = request.args.get('maxmark', 'any')
#     param['slice'] = request.args.get('slice', 'any')
#     param['sortAttr'] = request.args.get('sortAttr', 'any')
#
#     searchformToURL = "?"
#     searchformToURL += "dataset="
#     searchformToURL += request.args.get('dataset', '')
#     searchformToURL += "&plottype="
#     searchformToURL += request.args.get('plottype', '')
#     searchformToURL += "&minsup="
#     searchformToURL += request.args.get('minsup', '')
#     searchformToURL += "&minmark="
#     searchformToURL += request.args.get('minmark', '')
#     searchformToURL += "&maxmark="
#     searchformToURL += request.args.get('maxmark', '')
#     searchformToURL += '&slice='
#     searchformToURL += request.args.get('slice', '')
#     searchformToURL += '&sortAttr='
#     searchformToURL += request.args.get('sortAttr', '')
#     # print searchformToURL
#
#     #queryString = "+type:bargraph +dataset:541WINE +support:[0.5 TO *]"
#     queryString = ''
#     for key, val in param.iteritems():
#         #print key, val
#         if key != 'sortAttr' and key != 'minmark' and key != 'maxmark' and val != 'any' and val != '':
#             # if key == 'support' or key == 'mark':
#             if key == 'support':
#                 queryString += '+' + key + ':[' + val + ' TO *] '
#             else:
#                 queryString += '+' + key + ':' + val + ' '
#
#     if param['minmark'] != 'any' and param['minmark'] != '' and param['maxmark'] != 'any' and param['maxmark'] != '':
#         queryString += '+mark:[' + param['minmark'] + ' TO ' + param['maxmark'] +'] '
#     elif param['minmark'] != 'any' and param['minmark'] != '':
#         queryString += '+mark:[' + param['minmark'] + ' TO *] '
#     elif param['maxmark'] != 'any' and param['maxmark'] != '':
#         queryString += '+mark:[* TO ' + param['maxmark'] + '] '
#
#     queryString += '+url:[* TO *] '
#     print (queryString)
#
#     f = {
#          'q': queryString
#     }
#     encodedQuery = urllib.urlencode(f)
#     #print encodedQuery
#
#     if param['sortAttr'] != 'any' and param['sortAttr'] != '':
#         encodedQuery += '&sort=' + param['sortAttr'] + '+desc'
#     # print encodedQuery
#
#     # Solr Pagination
#     encodedQuery += '&start=' + str(start)
#
#     solrStr = application.config['SOLR_CHARTS_URL_ROOT'] + "/select?" + encodedQuery + application.config['SOLR_URL_SUFFIX']
#     #print solrStr
#
#     # response = requests.request("GET", "http://aurora.cs.rutgers.edu:8983/solr/testtiming"
#     #         + "/select?" + encodedQuery + "&wt=json&indent=true").json()['response']['docs']
#
#     #response = requests.request('GET', solrStr).json()['response']['docs']
#     response = requests.request('GET', solrStr).json()['response']
#
#     nrecords = response['numFound']
#     # print nrecords
#     # npages = math.ceil(float(nrecords)/10)
#     # npages = int(npages)
#     # pages = range(1, min(npages, 10)+1)
#
#     pagination = Pagination(page=page, per_page=application.config['POSTS_PER_PAGE'], total=nrecords, record_name='plots')
#     response['start'] = start
#     # response['page'] = page
#     # response['pages'] = pages
#     response['searchformToURL'] = searchformToURL
#     response['dataset'] = request.args.get('dataset', '')
#     response['plottype'] = request.args.get('plottype', '')
#     response['optradio'] = request.args.get('optradio', '')
#
#     return render_template('searchresults.html', results=response, pagination=pagination)

# @application.route('/form/search/table/')
# def activeTable():
#     param = {}
#     param['id'] = request.args.get('id', 'any')
#
#     searchformToURL = "?"
#     searchformToURL += "id="
#     searchformToURL += request.args.get('id', '')
#     # print searchformToURL
#
#     fqStr = ''
#     if param['id'] != 'any':
#         fqStr += 'id:' + param['id']
#     f = {
#          'fq': fqStr
#     }
#     encodedQuery = urllib.urlencode(f)
#     solrStr = application.config['SOLR_CHARTS_URL_ROOT'] + "/select?q=*%3A*&" + encodedQuery + application.config['SOLR_URL_SUFFIX']
#     # print solrStr
#     # http://aurora.cs.rutgers.edu:8983/solr/democharts/select?q=id%3A+44e961b9-f61b-4e6f-8025-3eec03103091&wt=json&indent=true
#     response = requests.request('GET', solrStr).json()['response']
#     chart = response['docs'][0]
#
#     # print chart
#     # print database['Players']['attributes']
#
#     xTable = chart['table'][0]
#     x = chart['x'][0]
#     if xTable == 'joined':
#         xTable = database['joined']['attrToTable'][x]
#     chart['xcategories'] = database[xTable][x]['uniques']
#     if chart['type'][0] == 'heatmap':
#         yTable = chart['table'][0]
#         y = chart['y'][0]
#         if yTable == 'joined':
#             yTable = database['joined']['attrToTable'][y]
#         chart['ycategories'] = database[yTable][y]['uniques']
#
#     transformed = []
#     data = chart['data']
#     if chart['type'][0] == 'bargraph':
#         if not isinstance(data, Sequence):
#             data = [data]
#         for idx, val in enumerate(data):
#             if val > 0:
#                 transformed.append([int(idx), int(val)])
#     elif chart['type'][0] == 'heatmap':
#         step = 3
#         for i in range(0, len(data), step):
#             transformed.append([int(x) for x in data[i:i+step]])
#     elif chart['type'][0] == 'boxplot':
#         step = 7
#         for i in range(0, len(data), step):
#             row = data[i:i+step]
#             row[0] = int(row[0])
#             transformed.append(row)
#     chart['data'] = transformed
#
#     # print len(chart['data'])
#     # print len(chart['data'][0])
#     # print chart['data'][0]
#     # print chart['xcategories'][1]
#     # print chart['ycategories'][80]
#
#
#     # print type(chart['data'][0][0])
#     # print chart['xcategories'][chart['data'][0][0]]
#
#     # print len(chart['data'])
#
#     # print chart.keys()
#     return render_template('table.html', chart=chart)

if __name__ == '__main__':
    application.run(port=8081, host='0.0.0.0', debug=application.config['DEBUG'])
