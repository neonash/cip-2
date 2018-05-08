from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
# import pymongo
#import datetime
#import binascii
#from time import sleep
import ATLAS1
from atlas.config import dbConfig
import pandas as pd
import NgramMapping
#import SentimentAPI
#import SentimentAPI_2
import SentimentAnalysis_2
#import SentimentAnalysis_2_CSV
#import SentimentAPI_generic
#import TrigDriv_2_CSV
import TrigDriv_2
import TopicModeling
import logging
import traceback


def caller_file(full_data_dict):
    # print(full_data_dict)
    request = full_data_dict['filename_obj']
    #print("Entering File analysis", request)
    filecontents = full_data_dict['file_data']
    #print("filecontents:", filecontents)

    #db = pymongo.MongoClient().atlas
    #s = request.encode('utf-8')

    df = pd.read_csv(dbConfig.dict["requestUrl"])
    status_dict = {'status': None, "senti_list": None, 'td_list': None}

    print("Calling Atlas1.main2()")
    status = ATLAS1.main2(request, filecontents)
    df.ix[(df.reqKw == request), 'reqStatus'] = "Scraping complete"

    # file_dict = {
    #     '_id': binascii.hexlify(s),
    #     'Product': request,
    #
    #     'metadata': {
    #         '_id': binascii.hexlify(s),
    #         'lastUpdated': datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"),
    #         'name': request
    #     },
    #     'analyticData': {
    #         'sentimentData': [
    #
    #         ],
    #         'trigdrivData': {
    #
    #         }
    #     }
    # }
    # result = db.data.insert_one(file_dict)
    # sent_list = SentimentAPI_generic.senti_main(dbConfig.dict['uploadsUrl'] + request, ',')
    # print sent_list
    #
    # target_string = "analyticData.sentimentData"
    #
    # db.data.update({"_id": binascii.hexlify(s)}, {"$set": {target_string: sent_list[0]}})
    # print result.inserted_id

    # Calling analyses files - sentiment, trigger/driver and topic modelling
    try:
        print("Tagging the dataset with the dictionary provided")
        # tagop_list = NgramMapping.main(full_data_dict['file_data'], full_data_dict['tag_dict'])
        print("tagging done")
        # df.ix[(df.reqKw == request), 'reqStatus'] = "Sentiment analysis done"
    except:
        print("Error while tagging dataset with dictionary")
        print(traceback.print_exc())

    try:
        print("Calling sentiment analyses to run on uploaded file...")
        sent_list = SentimentAnalysis_2.senti_main2(request, filecontents, full_data_dict['senti_dict'])
        #print sent_list
        print("Sentiment data inserted into DB")
        df.ix[(df.reqKw == request), 'reqStatus'] = "Sentiment analysis done"

    except:
        print("Error while analysing sentiment")
        print(traceback.print_exc())

    try:
        td_list = TrigDriv_2.td_main2(request, full_data_dict['td_dict'])
        #print td_list
        print("TriggerDriver data inserted into DB")
        df.ix[(df.reqKw == request), 'reqStatus'] = "Trigger/driver analysis complete"
    except:
        print("Error while analysing triggers/drivers")
        print(traceback.print_exc())

    print "Going to topic model"
    #logging.info("going to topicmodeling.main")

    # Performing Topic Modeling Analysis
    num_topics = 5
    topic_status = TopicModeling.main(request, num_topics)
    df.ix[(df.reqKw == request), 'reqStatus'] = "Analysis complete"

    # if status == 200 and sent_list == 200 and td_list == 200 and topic_status == 200:
    #     # Update request csv status to completed
    #     df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Completed"
    # elif status == 200 and sent_list == 200 and td_list == 200:
    #     df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Topic Modelling Failed"
    # elif status == 200 and sent_list == 200:
    #         df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Trigger/Driver Failed"
    # elif status == 200:
    #     df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Sentiment Failed"
    # else:
    #     df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Scraping incomplete"

    with open(dbConfig.dict["requestUrl"], 'w') as f:
        df.to_csv(f, index=False)

    print("Exiting return")
    return request


def caller(request, site):
    print("Entering", request, site)

    # db = pymongo.MongoClient().atlas
    # s = request.encode('utf-8')
    status = ATLAS1.main(request, site)
    # prod_dict = {
    #     '_id': binascii.hexlify(s),
    #     'Product': request,
    #     'metadata': {
    #         '_id': binascii.hexlify(s),
    #         'lastUpdated': datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"),
    #         'name': request
    #     },
    #     'analyticData': {
    #         'sentimentData': [
    #
    #         ],
    #         'trigdrivData': {
    #
    #         },
    #     }
    # }
    # result = db.data.insert_one(prod_dict)
    print("Atlas main finish")
    #
    try:
        # sent_list = SentimentAPI_2.senti_main(dbConfig.dict['outputUrl'], request)

        #sent_list = SentimentAnalysis_2_CSV.senti_main(dbConfig.dict['outputUrl'], request)
        #print sent_list

        #target_string = "analyticData.sentimentData"
        #db.data.update({"_id": binascii.hexlify(s)}, {"$set": {target_string: sent_list[0]}})
        #print result.inserted_id

        #print("Sentiment data inserted into MongoDB")

        sent_list = SentimentAnalysis_2.senti_main(request)
        print sent_list
        print("Sentiment data inserted into DB")

    except:
        print("Error while analysing sentiment")
        print(traceback.print_exc())
        # try:
        #     #sent_list = SentimentAnalysis_2.senti_main(dbConfig.dict['outputUrl'], request)
        #     sent_list = SentimentAnalysis_2.senti_main(request)
        #     print sent_list
        #     '''
        #     target_string = "analyticData.sentimentData"
        #     db.data.update({"_id": binascii.hexlify(s)}, {"$set": {target_string: sent_list[0]}})
        #     print result.inserted_id
        #     '''
        #     print("Sentiment data inserted into DB")
        #
        # except:
        #     print("Error while analysing custom sentiment code.")
        #     print(traceback.print_exc())

    try:
        #td_list = TrigDriv_2_CSV.td_main(dbConfig.dict['outputUrl'], request)
        #target_string = "analyticData.trigdrivData"
        #db.data.update({"_id": binascii.hexlify(s)}, {"$set": {target_string: td_list[0]}})
        #print result.inserted_id
        #print("TriggerDriver data record inserted into MongoDB")

        td_list = TrigDriv_2.td_main(request)
        print td_list
        print("TriggerDriver data inserted into DB")
    except:
        print("Error while analysing triggers/drivers")
        print(traceback.print_exc())

    print "Going to topic model"
    #logging.info("going to topicmodeling.main")

    #Performing Topic Modeling Analysis
    num_topics = 5
    topic_status = TopicModeling.main(request, num_topics)

    df = pd.read_csv(dbConfig.dict["requestUrl"])
    if status == 200 & sent_list[1] == 200 & topic_status == 200:
        # Update request csv status to completed
        df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Completed"
    else:
        df.ix[(df.reqKw == request) & (df.reqStatus == 'Pending'), 'reqStatus'] = "Failed"
    with open(dbConfig.dict["requestUrl"], 'w') as f:
        df.to_csv(f, index=False)

    print("Exiting Return")
    return request


pool = ProcessPoolExecutor()


def pool_exe(request, site):
    future = pool.submit(caller, request, site)
    print ("Exit pool exe\n")


#def pool_exe_file(request,filecontents):
#    future = pool.submit(caller_file, request, filecontents)
#    print("Exit file pool exe\n")


def pool_exe_file(full_data_dict):
    future = pool.submit(caller_file, full_data_dict)
    print("Exit file pool exe\n")