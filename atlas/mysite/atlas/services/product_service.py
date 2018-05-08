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

    # table_data_df = pd.DataFrame({'dimensions': [' '], 'levels': [' ']}, index=None)

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
                        #print(target)

                        full_data_dict['tag_dict'] = target
                        with file(target, 'w') as outfile:
                            outfile.write(filecontents)
                            responseObject["message"] = "Success: File Uploaded successfully"
                            responseObject["status"] = 200
                            responseObject["body"] = filedata._name
                        print("tag dict uploaded")
                        tagdict_flag = True
                        # ###################### readdims() start
                        #final_list = read_dims(request)
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

    #if tagdict_flag:
    return responseObject
    # else:
    #    return responseObject
    # return [responseObject, table_data_df['dimensions'].tolist(),table_data_df['levels'].tolist()]


def start_analysis():
    global full_data_dict

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

    table_data_df = pd.DataFrame({'dimensions': [' '],
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

        last_dim_idx = 0  # last idx of headers_list traversed
        # h2 = last_dim_idx + 1
        last_idx_checked = False
        while last_dim_idx < len(headers_list) and h2 <= len(headers_list) and not last_idx_checked:
            # list entry = [curr dimension, < levels within it >]
            list_entry = [headers_list[last_dim_idx]]
            # > using extend instead of append

            is_next_dim = False
            # if last_dim_idx == len(headers_list) - 1:
            #     # last item in headerlist is a dimension by itself
            #     while len(list_entry) < 6:
            #         list_entry.append("#N/A")
            #     #print(list_entry)
            #     table_data_df.loc[len(table_data_df)] = list_entry
            #     break
            # else:
            h2 = last_dim_idx + 1  # loop till (len(headers_list) - 1) (equiv to inner for loop), starting from idx 2 to compare with idx 1
            if h2 == len(headers_list):
                last_idx_checked = True

            while h2 < len(headers_list) and not is_next_dim and not last_idx_checked:

                # if next header has _, then it is a level of the prev dim, otherwise new (next) dimension
                if "_" in headers_list[h2]:
                    is_next_dim = False
                    list_entry.append(str(headers_list[h2]).split("_")[1])  # [t1, t2]

                elif h2 == last_dim_idx:
                    break

                else:
                    last_dim_idx = h2
                    is_next_dim = True

                h2 += 1

            # temp_var = ','.join(list_entry[1])
            # del list_entry[1]
            # list_entry.append(temp_var)
            while len(list_entry) < 6:
                list_entry.append("#N/A")
            print(list_entry)
            table_data_df.loc[len(table_data_df)] = list_entry
        print(table_data_df)

    except:
        print "Exception caught while extracting dimensions"
        print traceback.print_exc()

    final_list = [table_data_df['dimensions'].tolist(), table_data_df['level1'].tolist(),
                  table_data_df['level2'].tolist(), table_data_df['level3'].tolist(),
                  table_data_df['level4'].tolist(), table_data_df['level5'].tolist()]

    return final_list
    # return [responseObject, table_data_df['dimensions'].tolist(),table_data_df['levels'].tolist()]