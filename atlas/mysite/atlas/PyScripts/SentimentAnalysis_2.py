# Row-wise Analysis

import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import pandas as pd
import re
import csv
from decimal import Decimal
import traceback
from atlas.config import dbConfig
import django
django.setup()
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses


status_code = 500

# ##############################################################


def clean_rev(curr_rev):
    curr_rev = curr_rev.replace("\n", " ").replace("\t", " ").replace("\r", " ")
    curr_rev = curr_rev.replace("&nbsp;", " ").replace("&gt;", " ").replace("&lt;", " ").replace("&quot;", " ")
    curr_rev = curr_rev.replace(" & ", " and ").replace("-", " ")
    curr_rev = re.sub(r'[^\w\s]*', "", curr_rev)  # 0 or more non-(alphanumeric or whitespace)
    curr_rev = curr_rev.strip()
    curr_rev = re.sub(r'\s{2,}', ' ', curr_rev)

    return curr_rev

# ###############################################################


# Main function
def senti_main(kw_str):
    global status_code

    try:
        pid_by_kw = Product.objects.filter(pCategory=kw_str).values_list('pid', flat=True)

        print("product table filtered by category")
        #for p in pid_by_kw.iterator():
        print(pid_by_kw)

        revs_by_pid = Review.objects.filter(pid_id__in=list(pid_by_kw)).values()
        print("Reviews by pid_id")
        for r in revs_by_pid:
            print(r['rText'].encode('utf-8'))
            curr_rev = r['rText'].encode('utf-8')
            curr_rev1 = clean_rev(curr_rev)
            curr_rating = r['rRating']
            analysis_obj = Analysis.objects.get(rid_id=r['rid'])
            # add code to analyse
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Trigram score
            score = 0
            trigrams = []
            unigrams = str(curr_rev1).split(" ")  # for unigrams
            for i in range(0, len(unigrams) - 2):  # form trigrams
                trigrams.append(unigrams[i] + " " + unigrams[i + 1] + " " + unigrams[i + 2])
            for i in trigrams:
                with open(dbConfig.dict['sentDict']) as tsv:
                    for line in csv.reader(tsv, dialect="excel-tab"):
                        if str(i).lower() == str(line[0]).lower():
                            curr_rev1 = str(curr_rev1).replace(i, "", 1)  # self-negates matched phrase
                            score += int(line[1])
                            break
            trigram_score = score

            # Bigram score
            score = 0
            bigrams = []
            curr_rev2 = curr_rev
            curr_rev2 = curr_rev2.replace("  ", " ")
            # print "FINDING BIGRAM MATCHES IN: "
            # print(curr_rev2)
            unigrams = str(curr_rev2).split(" ")  # for unigrams
            for i in range(0, len(unigrams) - 1):  # form bigrams
                bigrams.append(unigrams[i] + " " + unigrams[i + 1])
            for i in bigrams:
                with open(dbConfig.dict['sentDict']) as tsv:
                    for line in csv.reader(tsv, dialect="excel-tab"):
                        # line_words = str(line[0]).split(" ")
                        # if len(line_words) == 2:
                        if str(i).lower() == str(line[0]).lower():
                            curr_rev2 = str(curr_rev2).replace(i, "", 1)
                            score += int(line[1])
                            break
            bigram_score = score

            # Unigram score
            score = 0
            curr_rev3 = curr_rev2
            curr_rev3 = curr_rev3.replace("  ", " ")
            # print "FINDING UNIGRAM MATCHES IN: "
            # print curr_rev3
            unigrams = str(curr_rev3).split(" ")  # for unigrams
            for rw in unigrams:
                with open(dbConfig.dict['sentDict']) as tsv:
                    for line in csv.reader(tsv,
                                           dialect="excel-tab"):  # You can also use delimiter="\t" rather than giving a dialect.
                        # line_words = str(line[0]).split(" ")
                        # if len(line_words) == 1:
                        if str(rw).lower() == str(line[0]).lower():
                            # not creating self-negating str (like in prev loops) as its not needed for later use anywhere
                            score += int(line[1])
                            break
            unigram_score = score

            # print "Trigram Score: " + str(trigram_score)
            # print "Bigram Score: " + str(bigram_score)
            # print "Unigram Score: " + str(unigram_score)
            final_score = trigram_score + bigram_score + unigram_score

            print "Final Score: " + str(final_score)
            print "Rating: " + str(curr_rating)

            analysis_obj.sentiScore = score

            if final_score < 0 and Decimal(curr_rating) > 2:
                # print "MISMATCH!!! SCORE LESS RATING MORE!!!"
                analysis_obj.sentiment = "Positive"  # rating takes precedence

            elif final_score > 20 and Decimal(curr_rating) <= 3:
                # print "MISMATCH!!! SCORE MORE RATING LESS!!!"
                analysis_obj.sentiment = "Negative"  # rating takes precedence
            else:
                if final_score < 0:
                    analysis_obj.sentiment = "Negative"
                elif final_score > 0:
                    analysis_obj.sentiment = "Positive"
                elif final_score == 0:
                    analysis_obj.sentiment = "Neutral"
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            try:
                analysis_obj.save()
            except:
                print("Error while updating analysis table!")
                print(traceback.print_exc())
        status_code = 200

    except:
        print("Error while analysing sentiment...")
        status_code = 500
        print(traceback.print_exc())

    return status_code

# #################################################################################


# Main function
def senti_main2(kw_str, filecontents, sentidict):
    global status_code

    if ".csv" in kw_str:
        kw_str = kw_str[:-4]
    print("product category :>", kw_str)

    print("type of contents_df:", type(filecontents))
    filecontents = pd.read_csv(StringIO(filecontents))
    #print("contents_df: ", filecontents)

    try:
        revs_df = Uploads.objects.filter(pCategory=kw_str).only('rid','rText','rRating').values()

        for r in revs_df:
            #print(r['rText'].encode('utf-8'))
            curr_rev = r['rText'].encode('utf-8')
            curr_rev1 = clean_rev(curr_rev)
            curr_rating = r['rRating']
            try:
                analysis_obj = UploadAnalyses.objects.get(rid_id=r['rid'])
            except:
                analysis_obj = UploadAnalyses.objects.filter(rid_id=r['rid']).distinct()
            #  code to analyse
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Trigram score
            score = 0
            trigrams = []
            unigrams = str(curr_rev1).split(" ")  # for unigrams
            for i in range(0, len(unigrams) - 2):  # form trigrams
                trigrams.append(unigrams[i] + " " + unigrams[i + 1] + " " + unigrams[i + 2])
            for i in trigrams:
                #with open(dbConfig.dict['sentDict']) as tsv:
                with open(sentidict) as tsv:
                    for line in csv.reader(tsv, dialect="excel-tab"):
                        if str(i).lower() == str(line[0]).lower():
                            curr_rev1 = str(curr_rev1).replace(i, "", 1)  # self-negates matched phrase
                            score += int(line[1])
                            break
            trigram_score = score

            # Bigram score
            score = 0
            bigrams = []
            curr_rev2 = curr_rev
            curr_rev2 = curr_rev2.replace("  ", " ")
            # print "FINDING BIGRAM MATCHES IN: "
            # print(curr_rev2)
            unigrams = str(curr_rev2).split(" ")  # for unigrams
            for i in range(0, len(unigrams) - 1):  # form bigrams
                bigrams.append(unigrams[i] + " " + unigrams[i + 1])
            for i in bigrams:
                #with open(dbConfig.dict['sentDict']) as tsv:
                with open(sentidict) as tsv:
                    for line in csv.reader(tsv, dialect="excel-tab"):
                        # line_words = str(line[0]).split(" ")
                        # if len(line_words) == 2:
                        if str(i).lower() == str(line[0]).lower():
                            curr_rev2 = str(curr_rev2).replace(i, "", 1)
                            score += int(line[1])
                            break
            bigram_score = score

            # Unigram score
            score = 0
            curr_rev3 = curr_rev2
            curr_rev3 = curr_rev3.replace("  ", " ")
            # print "FINDING UNIGRAM MATCHES IN: "
            # print curr_rev3
            unigrams = str(curr_rev3).split(" ")  # for unigrams
            for rw in unigrams:
                #with open(dbConfig.dict['sentDict']) as tsv:
                with open(sentidict) as tsv:
                    for line in csv.reader(tsv,
                                           dialect="excel-tab"):  # You can also use delimiter="\t" rather than giving a dialect.
                        # line_words = str(line[0]).split(" ")
                        # if len(line_words) == 1:
                        if str(rw).lower() == str(line[0]).lower():
                            # not creating self-negating str (like in prev loops) as its not needed for later use anywhere
                            score += int(line[1])
                            break
            unigram_score = score

            # print "Trigram Score: " + str(trigram_score)
            # print "Bigram Score: " + str(bigram_score)
            # print "Unigram Score: " + str(unigram_score)
            final_score = trigram_score + bigram_score + unigram_score

            #print "Final Score: " + str(final_score)
            #print "Rating: " + str(curr_rating)

            analysis_obj.sentiScore = score

            if final_score < 0 and Decimal(curr_rating) > 2:
                # print "MISMATCH!!! SCORE LESS RATING MORE!!!"
                analysis_obj.sentiment = "Positive"  # rating takes precedence

            elif final_score > 20 and Decimal(curr_rating) <= 3:
                # print "MISMATCH!!! SCORE MORE RATING LESS!!!"
                analysis_obj.sentiment = "Negative"  # rating takes precedence
            else:
                if final_score < 0:
                    analysis_obj.sentiment = "Negative"
                elif final_score > 0:
                    analysis_obj.sentiment = "Positive"
                elif final_score == 0:
                    analysis_obj.sentiment = "Neutral"
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            try:
                analysis_obj.save()
            except:
                print("Error while updating analysis table!")
                print(traceback.print_exc())
        status_code = 200

    except:
        print("Error while analysing sentiment...")
        status_code = 500
        print(traceback.print_exc())

    return status_code