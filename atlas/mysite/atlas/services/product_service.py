from django.http import HttpResponse
from django.http import HttpRequest
from atlas import static_data
#from atlas.PyScripts import ATLAS1
import datetime
import pandas as pd
import numpy as np
import os
from atlas.PyScripts import task1
from atlas.config import dbConfig
import StringIO
import traceback


full_data_dict = {'filename_obj': None, 'file_data': None, 'tag_dict': None,
                  'senti_dict': dbConfig.dict['sentDict'], 'td_dict': dbConfig.dict['keywordsDict'], 'boolStart': False}
# [dataset name obj, data_df, tag_dict, senti dict, trig-driv dict]


def fetchRequests():
    print(os.getcwd())
    df = pd.read_csv(dbConfig.dict["requestUrl"])
    jsonData = df.to_json(orient='records')
    return jsonData


def raiseRequest(request, site, refreshStatus):
    responseObject = {}
    keyObject = ["message", "status", "body"]
    curTime = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p")
    for i in keyObject:
        responseObject[i] = None

    columns = ['reqKw', 'reqTime', 'reqStatus']
    status = 'Pending'
    df = pd.read_csv(dbConfig.dict["requestUrl"])
    if refreshStatus:
        print refreshStatus
        if ((df['reqStatus'] == 'Pending') & (df['reqKw'] == request)).any():
            responseObject["message"] = "Conflict: A pending/processing entry for the product already exists"
            responseObject["status"] = 409
            responseObject["body"] = request
            return responseObject
        df.ix[(df.reqStatus == 'Completed') & (df.reqKw == request), 'reqTime'] = curTime
        df.ix[(df.reqStatus == 'Completed') & (df.reqKw == request), 'reqStatus'] = status
        with open(dbConfig.dict["requestUrl"], 'w') as f:
            (df).to_csv(f, index=False)
        f.close()
    else:
        # df.to_csv("C:\\Users\\akshat.gupta\\Documents\\django-atlas\\mysite\\atlas\\database\\request.csv", mode='a', index=False, sep=',', header=False)
        data = np.array([[request, curTime, status]])
        print("len(df): ", len(df))
        df1 = pd.DataFrame(data, columns=columns, index=[len(df)])
        with open(dbConfig.dict["requestUrl"], 'a') as f:
            (df1).to_csv(f, header=False)
        f.close()
    #task.work()
    task1.pool_exe(request, site)
    responseObject["message"] = "Success: Request raised successfully"
    responseObject["status"] = 200
    responseObject["body"] = request
    return responseObject


def getMetaDataFromProducts():
    ls = []
    for key, val in static_data.products.items():
        ls.append(val["metaData"])
    return ls


def reset_data_dict_map():
    global full_data_dict

    full_data_dict = {'filename_obj': None, 'file_data': None, 'tag_dict': None,
                      'senti_dict': dbConfig.dict['sentDict'], 'td_dict': dbConfig.dict['keywordsDict'], 'boolStart': False}


def uploadFile(request):
    global full_data_dict

    tagdict_flag = False

    print("INSIDE UPLOADFILE(REQUEST) FUNCTION")
    #print request
    responseObject = {}
    keyObject = ["message", "status", "body"]
    for i in keyObject:
        responseObject[i] = None
    #print "Content-Type: text/html"
    a = request.FILES

    # print("a:", a)
    # print dir(a)
    # print (type(a))
    # print dir(request)
    # print(dir(a['kartik-input-711[]']))
    #              form = cgi.FieldStorage()

    curTime = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p")
    columns = ['reqKw', 'reqTime', 'reqStatus']
    status = 'Pending'
    df = pd.read_csv(dbConfig.dict["requestUrl"])

    ids = ['input440[]', 'input441[]', 'input442[]', 'input44[]']

    # table_data_df = pd.DataFrame({'dimension': [' '], 'levels': [' ']}, index=None)

    for i in ids:
        # print(i)
        print("INSIDE FOR LOOP FOR REQUESTS IN UPLOADS")
        try:
            if request.FILES:
                # print (request.FILES)
                # print(i)

                #for filename1, file1 in request.FILES.iteritems():
                #    print(filename1, file1)
                #    name = request.FILES[filename1].name

                filedata = request.FILES[i]
                #filedata = request.FILES.getlist(i)
                #print (request.FILES[i])
                #print (filedata)
                if filedata:
                    filecontents = filedata.file.read()
                    #print(filecontents)
                    if i == 'input440[]':
                        print("inside if input440")
                        target = dbConfig.dict['tagDictPath'] + filedata._name
                        print(target)

                        full_data_dict['tag_dict'] = target
                        with file(target, 'w') as outfile:
                            outfile.write(filecontents)
                            responseObject["message"] = "Success: File Uploaded successfully"
                            responseObject["status"] = 200
                            responseObject["body"] = filedata._name
                        print("tag dict uploaded")
                        tagdict_flag = True
                        # ###################### readdims() start
                        final_list = read_dims(request)
                        print(final_list)
                        # ######################################

                        break
                    elif i == 'input441[]':
                        target = dbConfig.dict['sentDictsPath'] + filedata._name
                        #print(target)

                        full_data_dict['senti_dict'] = target
                        with file(target, 'w') as outfile:
                            outfile.write(filecontents)
                            responseObject["message"] = "Success: File Uploaded successfully"
                            responseObject["status"] = 200
                            responseObject["body"] = filedata._name
                        print("Senti dict uploaded")
                        break
                    elif i == 'input442[]':
                        target = dbConfig.dict['tdDictsPath'] + filedata._name
                        #print(target)
                        full_data_dict['td_dict'] = target
                        with file(target, 'w') as outfile:
                            outfile.write(filecontents)
                            responseObject["message"] = "Success: File Uploaded successfully"
                            responseObject["status"] = 200
                            responseObject["body"] = filedata._name
                        print("TD dict uploaded")
                        break
                    elif i == 'input44[]':
                        target = dbConfig.dict['uploadsUrl'] + filedata._name
                        #print(target)
                        full_data_dict['filename_obj'] = filedata._name
                        full_data_dict['file_data'] = filecontents
                        with file(target, 'w') as outfile:
                            outfile.write(filecontents)

                            responseObject["message"] = "Success: File Uploaded successfully"
                            responseObject["status"] = 200
                            responseObject["body"] = filedata._name
                            # open requests file and raise a request to analyse this file
                            data = np.array([[filedata._name, curTime, status]])
                            df1 = pd.DataFrame(data, columns=columns, index=[len(df)+1])
                            with open(dbConfig.dict["requestUrl"], 'a') as f:
                                df1.to_csv(f, header=False)
                            f.close()
                        #print("full_data_dict")
                        #print(full_data_dict)
                        break
        except:
            print("Error while uploading file. Displaying only for debugging:-")
            print traceback.print_exc()

    # try:
    #     if request.FILES['files[]']:
    #         filedata = request.FILES['files[]']
    #         if filedata.file:  # field really is an upload
    #             filecontents = filedata.file.read()
    #             target = dbConfig.dict['sentDictsPath'] + "\\" + filedata._name
    #             print(target)
    #             with file(target, 'w') as outfile:
    #                 outfile.write(filecontents)
    #             data_df = pd.read_csv(StringIO.StringIO(filecontents))
    #             print("sentidict saved")
    #             # full_data_dict['trigdriv_dict'] = data_df
    # except:
    #     print "Exception caught"
    #     #print traceback.print_exc()

    #print("calling task1")
    #task1.pool_exe_file(filedata._name, data_df)
    #task1.pool_exe_file(full_data_dict)

    # if tagdict_flag:
    return responseObject
    # else:
    #     return [responseObject, table_data_df['dimension'].tolist(),table_data_df['levels'].tolist()]


def start_analysis():
    global full_data_dict

    # insert tagging dict, its dimension mapping and dataset into database


    responseObject = {}
    print("calling task1")
    task1.pool_exe_file(full_data_dict)
    reset_data_dict_map()

    responseObject["message"] = "Analyses initiated successfully"
    responseObject["status"] = 200

    return responseObject


def read_dims(request):
    global full_data_dict

    print("INSIDE readdims(REQUEST) FUNCTION")
    print request
    #a = request.FILES

    #print("a:", a)
    #print dir(a)
    # print (type(a))
    # print dir(request)

    table_data_df = pd.DataFrame({'dimension': [' '],
                                  'level1': [' '],
                                  'level2': [' '],
                                  'level3': [' '],
                                  'level4': [' '],
                                  'level5': [' ']}, index=None)

    try:
        # if request.FILES:
        #     the_req = request.FILES["input440[]"]._name
        #    print(str(the_req).split('.')[0])

        # print(dbConfig.dict['tagDict'])
        #tag_dict_df = pd.read_csv(dbConfig.dict['tagDict'])  # FOR DEBUGGING
        tag_dict_df = pd.read_csv(full_data_dict['tag_dict'])  # FOR PRODUCTION
        headers_list1 = tag_dict_df.columns.values.tolist()
        headers_list = headers_list1[1:]  # to avoid first column
        print(headers_list)
        # del headers_list[0]
        print('populating table_data_df')

        # to extract dimensions and levels from uploaded dict >>>
        # for loop starting from 2 to avoid first col ('n gram'), looping till last but one element

        table_data_df = pd.DataFrame({'dimension': [' '],
                                      'level1': [' '],
                                      'level2': [' '],
                                      'level3': [' '],
                                      'level4': [' '],
                                      'level5': [' ']}, index=None)
        i = 0
        j = i + 1
        list_entry = [headers_list[i]]
        while j < len(headers_list):
            if "_" in headers_list[j]:
                lvl = str(headers_list[j]).split("_")[1]
                list_entry.append(lvl)
                if j == len(headers_list) - 1:  # if last item is a level, save list entry
                    while len(list_entry) < 6:
                        list_entry.append("#N/A")
                    #print(list_entry)
                    table_data_df.loc[len(table_data_df)] = list_entry
                j += 1
            else:
                # store previous entry
                while len(list_entry) < 6:
                    list_entry.append("#N/A")
                #print(list_entry)
                table_data_df.loc[len(table_data_df)] = list_entry

                # create new entry
                dim = headers_list[j]
                i = j
                list_entry = [dim]
                j = i + 1
                if j == len(headers_list):  # if last item is a dimension, save list entry
                    while len(list_entry) < 6:
                        list_entry.append("#N/A")
                    #print(list_entry)
                    table_data_df.loc[len(table_data_df)] = list_entry

            #print(table_data_df)

    except:
        print "Exception caught while extracting dimensions"
        print traceback.print_exc()

    final_list = [table_data_df['dimension'].tolist(), table_data_df['level1'].tolist(),
                  table_data_df['level2'].tolist(), table_data_df['level3'].tolist(),
                  table_data_df['level4'].tolist(), table_data_df['level5'].tolist()]

    return final_list
    # return [responseObject, table_data_df['dimension'].tolist(),table_data_df['levels'].tolist()]