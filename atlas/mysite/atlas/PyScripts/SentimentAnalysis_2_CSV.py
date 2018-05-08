# Row-wise Analysis

import pandas as pd
import re
import csv
from decimal import Decimal
import traceback
from atlas.config import dbConfig
import django
django.setup()
from atlas.models import Product, Review, Analysis


# csv_file_loc = "C:\Users\Aparna.harihara\PycharmProjects\AuScer\Outputs\ATLAS_Universal.csv"  # ATLAS_tv.csv
actual_reviews = []
cleaned_reviews = []
ratings = []
senti_dict_list = []
status_code = 500


def get_rating(str1):
    pat1 = re.compile(r'[0-9](\.?[0-9])?')
    #print pat1.match(str2).group()
    return pat1.match(str1).group()


def get_cols(curr_df):
    for index, row in curr_df.iterrows():
        line = row['rText']
        actual_reviews.append(line)
        line = line.replace("\n", " ").replace("\t", " ").replace("\r", " ")
        line = line.replace("&nbsp;", " ").replace("&gt;", " ").replace("&lt;", " ").replace("&quot;", " ")
        line = line.replace(" & ", " and ").replace("-", " ")
        line = re.sub(r'[^\w\s]*', "", line)  # 0 or more non-(alphanumeric or whitespace)
        line = line.strip()
        line = re.sub(r'\s{2,}', ' ', line)
        cleaned_reviews.append(line)

        ratings.append(row['rRating'])
    return [actual_reviews, cleaned_reviews, ratings]


def gen_rid(row1):
    l1=len(row1['rText'])
    w1 = len(str(row1['rText']).split(" "))
    tmp1 = row1['pid'] + "_" + row1['rUser'] + "_" + str(l1) + "_" + str(w1)
    return tmp1


def senti_main(csv_file_path, kw_str):
    global actual_reviews, cleaned_reviews, ratings, status_code

    try:
        df = pd.read_csv(csv_file_path)
        df_by_kw = df.loc[df['pCategory'] == kw_str]
        unique_sites = df_by_kw.siteCode.unique()
        for u_s in unique_sites:
            actual_reviews = []
            cleaned_reviews = []
            ratings = []

            #print u_s

            curr_df = df_by_kw.loc[df_by_kw['siteCode'] == u_s]
            [actual_reviews, cleaned_reviews, ratings] = get_cols(curr_df)

            final_scores = []
            rev_sentiment = []

            for idx, item in enumerate(cleaned_reviews):
                #print "COUNT " + str(idx)
                #print "" + item
                rev_line1 = item
                #print "FINDING TRIGRAM MATCHES IN: "
                #print rev_line1

                # Trigram score
                score = 0
                trigrams = []
                unigrams = str(rev_line1).split(" ")  # for unigrams
                for i in range(0, len(unigrams) - 2):  # form trigrams
                    trigrams.append(unigrams[i] + " " + unigrams[i + 1] + " " + unigrams[i + 2])
                for i in trigrams:
                    with open(dbConfig.dict['sentDict']) as tsv:
                        for line in csv.reader(tsv, dialect="excel-tab"):
                            if str(i).lower() == str(line[0]).lower():
                                rev_line1 = str(rev_line1).replace(i, "", 1)
                                # print rev_line1
                                # print line - can uncomment
                                # print "@@@"
                                # print line[1]
                                score += int(line[1])
                                break
                trigram_score = score

                # Bigram score
                score = 0
                bigrams = []
                rev_line2 = rev_line1
                rev_line2 = rev_line2.replace("  ", " ")
                #print "FINDING BIGRAM MATCHES IN: "
                #print rev_line2
                unigrams = str(rev_line2).split(" ")  # for unigrams
                for i in range(0, len(unigrams) - 1):  # form bigrams
                    bigrams.append(unigrams[i] + " " + unigrams[i + 1])
                for i in bigrams:
                    with open(dbConfig.dict['sentDict']) as tsv:
                        for line in csv.reader(tsv, dialect="excel-tab"):
                            # line_words = str(line[0]).split(" ")
                            # if len(line_words) == 2:
                            if str(i).lower() == str(line[0]).lower():
                                rev_line2 = str(rev_line2).replace(i, "", 1)
                                # print rev_line2
                                # print line - can uncomment
                                # print "@@@"
                                # print line[1]
                                score += int(line[1])
                                break
                bigram_score = score

                # Unigram score
                score = 0
                rev_line3 = rev_line2
                rev_line3 = rev_line3.replace("  ", " ")
                #print "FINDING UNIGRAM MATCHES IN: "
                #print rev_line3
                unigrams = str(rev_line3).split(" ")  # for unigrams
                for rw in unigrams:
                    with open(dbConfig.dict['sentDict']) as tsv:
                        for line in csv.reader(tsv, dialect="excel-tab"):  # You can also use delimiter="\t" rather than giving a dialect.
                            # line_words = str(line[0]).split(" ")
                            # if len(line_words) == 1:
                            if str(rw).lower() == str(line[0]).lower():
                                #print line - can uncomment
                                # print "@@@"
                                # print line[1]
                                score += int(line[1])
                                break
                unigram_score = score

                #print "Trigram Score: " + str(trigram_score)
                #print "Bigram Score: " + str(bigram_score)
                #print "Unigram Score: " + str(unigram_score)
                final_score = trigram_score + bigram_score + unigram_score
                final_scores.append(final_score)
                #print "Final Score: " + str(final_score)

                str2 = str(ratings[idx]).strip().replace("\r\n", " ")
                curr_rating = get_rating(str2)
                #print "Rating: " + curr_rating

                if final_score < 0 and Decimal(curr_rating) > 2:
                    #print "MISMATCH!!! SCORE LESS RATING MORE!!!"
                    rev_sentiment.append("Positive")
                elif final_score > 20 and Decimal(curr_rating) <= 3:
                    #print "MISMATCH!!! SCORE MORE RATING LESS!!!"
                    rev_sentiment.append("Negative")
                else:
                    if final_score < 0:
                        #print "REVIEW SENTIMENT: NEGATIVE"
                        rev_sentiment.append("Negative")
                    elif final_score > 0:
                        #print "REVIEW SENTIMENT: POSITIVE"
                        rev_sentiment.append("Positive")
                    elif final_score == 0:
                        #print "REVIEW SENTIMENT: NEUTRAL"
                        rev_sentiment.append("Neutral")
                    else:
                        #print "REVIEW SENTIMENT: CANNOT CLASSIFY!"
                        rev_sentiment.append("#N/A")

                    df.ix[(df.siteCode == u_s) & (df.pCategory == kw_str) & (df.rText == actual_reviews[idx]), 'sentiment'] = rev_sentiment[len(rev_sentiment) - 1]

                #print "\n"

            # 'for' loop through each review ends here

            sentiments = ["Positive", "Negative", "Neutral"]
            senti_counts = [0, 0, 0]
            senti_dict = {}
            site_senti_dict = {}
            for i in range(len(rev_sentiment)):
                if rev_sentiment[i] == sentiments[0]:
                    senti_counts[0] += 1
                elif rev_sentiment[i] == sentiments[1]:
                    senti_counts[1] += 1
                elif rev_sentiment[i] == sentiments[2]:
                    senti_counts[2] += 1
                else:
                    pass
            for i in range(len(sentiments)):
                senti_dict[sentiments[i]] = senti_counts[i]

            print senti_dict

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
        # 'for' loop through unique sites ends here
        print senti_dict_list


        # Add to database:-
        for index, row in df.iterrows():
            print("adding row to analysis table")
            try:
                #tmp = str(row['pid']) + "_" + str(row['rUser'])
                rid = gen_rid(row)
                print(rid)
                fk_rid_obj = Review.objects.get(rid=rid)
                print(fk_rid_obj)
                obj1 = Analysis.objects.create(rid=fk_rid_obj, sentiment=row['sentiment'], trigger=row['trigger'],
                                               driver=row['driver'])
                print(fk_rid_obj)
                obj1.save()

            except:
                print("Error while adding row to analysis table!")
                # tmp = str(row['pid'])+"_"+str(row['rUser'])
                # print(tmp)
                print(traceback.print_exc())


        status_code = 200
        return [senti_dict_list, status_code]
    except:
        print "Unexpected error during analysis!"
        print(traceback.print_exc())
        status_code = 500
        return [None, status_code]

