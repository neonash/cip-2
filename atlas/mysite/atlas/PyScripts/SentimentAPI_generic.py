# Vivekn

import requests
import json
from functools import reduce  # forward compatibility for Python 3
import operator
import pandas as pd
import re
import traceback


cleaned_reviews = []
status_code = 500

# ####################################################################################################


# To extract reviews column from dataframe and clean it
def get_cols(df1):
    for index, row in df1.iterrows():
        line = row['rText']
        if type(line) != str:
            line = "#N/A"
        line = line.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        line = line.replace("&nbsp;", " ").replace("&gt;", " ").replace("&lt;", " ").replace("&quot;", " ")
        line = line.replace(" & ", " and ").replace("-", " ")
        line = re.sub(r'[^\w\s]*', "", line)  # 0 or more non-(alphanumeric or whitespace)
        line = line.strip()
        line = re.sub(r'\s{2,}', ' ', line)
        cleaned_reviews.append(line)

    return cleaned_reviews

# ###################################################################################################


# Override function to access dictionary
def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)

# ####################################################################################################


def senti_main(csv_file_path, separ):
    global cleaned_reviews, status_code

    senti = []
    confi = []
    #senti_dict = []  # To store count of each sentiment in corpus

    try:
        # Read input file
        df1 = pd.read_csv(csv_file_path, sep=separ)

        ## Slice dataframe to get rows only for selected product category
        #df_by_kw = df.loc[df['pCategory'] == kw_str]

        ## Store unique sites from available data
        #unique_sites = df_by_kw.siteCode.unique()

        ## To loop through rows per unique site
        #for u_s in unique_sites:
        cleaned_reviews = []

        #print u_s

        ## Slice dataframe to get rows only for one site per loop
        #curr_df = df_by_kw.loc[df_by_kw['siteCode'] == u_s]

        cleaned_reviews = get_cols(df1)

        url = "http://sentiment.vivekn.com/api/batch/"

        # payload contains list of reviews
        payload = cleaned_reviews
        headers = {
            'content-type': "application/raw",
            'cache-control': "no-cache",
            'postman-token': "4ea595e2-abf0-e55d-ccb7-07b4ce3d0052"
            }

        # Request (payload) sent as JSON
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        # Response contains list of results, corresponding to same order as reviews sent in request
        response1 = json.loads(response.text)
        # print type(response1)
        # print(response1)

        # Loop through responses list per site in current loop
        for i in range(len(response1)):
            print "\n" + cleaned_reviews[i]
            # Response contains sentiment and confidence
            senti.append(getFromDict(response1[i], ["result"]))
            confi.append(getFromDict(response1[i], ["confidence"]))
            print "=== > " + str(senti[len(senti) - 1]) + " with a confidence of " + str(confi[len(confi) - 1]) + "%"

        # List of unique sentiments
        sentiments = ["Positive", "Negative", "Neutral"]

        # Contains count of reviews with each sentiment
        senti_counts = [0, 0, 0]

        # Contains dictionary of sentiments and corresponding count of reviews
        senti_dict = {}

        # Contains dictionary of filewise sentiment counts
        file_senti_dict = {}
        file_senti_dict_list = []

        # To count reviews with each sentiment
        for i in range(len(senti)):
            if senti[i] == sentiments[0]:
                senti_counts[0] += 1
            elif senti[i] == sentiments[1]:
                senti_counts[1] += 1
            elif senti[i] == sentiments[2]:
                senti_counts[2] += 1
            else:
                pass

        # Form the dictionaries
        for i in range(len(sentiments)):
            senti_dict[sentiments[i]] = senti_counts[i]

        # print senti_dict

        # Obtain file_name for storing
        if "\\" in csv_file_path:
            split_file_name = str(csv_file_path).split("\\")
            split_last_value = split_file_name[len(split_file_name) - 1]
        else:
            split_last_value = csv_file_path
        # name_value = split_last_value.split(".")[0]
        file_senti_dict["name"] = split_last_value

        #if u_s == "AM":
        #    site_senti_dict["name"] = "Amazon"
        #elif u_s == "HD":
        #    site_senti_dict["name"] = "HomeDepot"
        #else:
        #    site_senti_dict["name"] = "Other"

        file_senti_dict["data"] = senti_dict.copy()

        file_senti_dict_list.append(file_senti_dict.copy())
        #print "---------------"

        # 'for' loop thru unique sites ends here ^
        status_code = 200
        return [file_senti_dict_list, status_code]
    except:
        print "Unexpected error during analysis!"
        print traceback.print_exc()
        status_code = 500
        return [None, status_code]
