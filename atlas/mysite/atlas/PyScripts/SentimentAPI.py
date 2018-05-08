import requests
import json
from functools import reduce  # forward compatibility for Python 3
import operator
import pandas as pd
import re


cleaned_reviews = []
status_code = 500

# ####################################################################################################


# To extract reviews column from dataframe and clean it
def get_cols(curr_df):
    for index, row in curr_df.iterrows():
        line = row['rText']
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


def senti_main(csv_file_path, kw_str):
    global cleaned_reviews, status_code

    senti = []
    confi = []
    senti_dict_list = []  # To store list of sentiment dictionaries for each site

    try:
        # Read input file
        df = pd.read_csv(csv_file_path)

        # Slice dataframe to get rows only for selected product category
        df_by_kw = df.loc[df['pCategory'] == kw_str]

        # Store unique sites from available data
        unique_sites = df_by_kw.siteCode.unique()

        # To loop through rows per unique site
        for u_s in unique_sites:
            cleaned_reviews = []

            print u_s

            # Slice dataframe to get rows only for one site per loop
            curr_df = df_by_kw.loc[df_by_kw['siteCode'] == u_s]

            cleaned_reviews = get_cols(curr_df)

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

            # Contains dictionary of sitewise sentiment counts
            site_senti_dict = {}

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

            if u_s == "AM":
                site_senti_dict["name"] = "Amazon"
            elif u_s == "HD":
                site_senti_dict["name"] = "HomeDepot"
            elif u_s == "WM":
                site_senti_dict["name"] = "Walmart"
            else:
                site_senti_dict["name"] = "Other"

            site_senti_dict["data"] = senti_dict.copy()

            senti_dict_list.append(site_senti_dict.copy())
            print "---------------"

        # 'for' loop thru unique sites ends here ^
        status_code = 200
        return [senti_dict_list, status_code]
    except:
        print "Unexpected error during analysis!"
        status_code = 500
        return status_code
