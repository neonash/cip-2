import pandas as pd
import re
from time import time
import traceback
from atlas.config import dbConfig
import django
django.setup()
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses


status_code = 500
# ##############################################################################


def td_main(kw_str):
    global status_code

    try:
        keywords_dict_file = dbConfig.dict['keywordsDict']

        triggers = ['Upgrade', 'Replace', 'FirstTimeBuyer', 'Gift', 'Marketing-Sale']
        subtriggers = ['Upgrade_Upgrade',
                       'Replace_Replace',
                       'FirstTimeBuyer_FirstTimeBuyer',
                       'Gift_Birthday',
                       'Gift_Wedding',
                       'Gift_Christmas',
                       'Gift_Other',
                       'Marketing-Sale_Marketing-Sale']
        drivers = ['Brand', 'Cost', 'Recommendation', 'Innovation', 'Marketing-Ads']
        subdrivers = ['Brand_Brand',
                      'Cost_Cost',
                      'Recommendation_Recommendation',
                      'Innovation_Innovation',
                      'Marketing-Ads_TV',
                      'Marketing-Ads_Radio',
                      'Marketing-Ads_Outdoor',
                      'Marketing-Ads_Other']

        start_time = time()

        pid_by_kw = Product.objects.filter(pCategory=kw_str).values_list('pid', flat=True)

        ##print("product table filtered by category")
        # for p in pid_by_kw.iterator():
        ##print(pid_by_kw)

        revs_by_pid = Review.objects.filter(pid_id__in=list(pid_by_kw)).values()
        #print("Reviews by pid_id")

        # for u_s in unique_sites:
        for r in revs_by_pid:
            #print(r['rText'].encode('utf-8'))
            curr_rev = r['rText'].encode('utf-8')
            #print(r['rid'])
            try:
                analysis_obj = Analysis.objects.get(rid_id=r['rid'])
            except:
                analysis_obj = Analysis.objects.create(rid_id=r['rid'])

            kw = pd.read_csv(keywords_dict_file)

            for each_kw in range(len(kw)):
                # #print("each_kw:" + str(each_kw))

                if re.findall(kw.ix[each_kw, 'Keywords'], curr_rev, re.I):

                    # if kw.ix[each_kw, 'Types'] in triggers:
                    if str(kw.ix[each_kw, 'Subtypes']).split("_")[0] in triggers:  # main trig of this subtype
                        old_trig_obj = analysis_obj.trigger

                        if old_trig_obj:
                            old_trig_str = old_trig_obj
                        else:
                            old_trig_str = " "

                        #print("old trig str: " + old_trig_str)

                        if not old_trig_str == " ":
                            analysis_obj.trigger = old_trig_str + "," + str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.trigger)
                        else:
                            analysis_obj.trigger = str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.trigger)

                    elif kw.ix[each_kw, 'Subtypes'].split("_")[0] in drivers:
                        # elif kw.ix[each_kw, 'Types'] in drivers:
                        old_driv_obj = analysis_obj.driver

                        if old_driv_obj:
                            old_driv_str = old_driv_obj
                        else:
                            old_driv_str = " "

                        #print("old driv str: " + old_driv_str)

                        if not old_driv_str == " ":
                            analysis_obj.driver = old_driv_str + "," + str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.driver)
                        else:
                            analysis_obj.driver = str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.driver)

                    try:
                        analysis_obj.save()
                    except:
                        pass
                        #print("Error while updating analysis table!")
                        #print(traceback.#print_exc())

        end_time = time()

        #print "Running Time : " + str(end_time - start_time) + " secs"

        status_code = 200
        return status_code

    except:
        #print("Error in TrigDriv_2!")
        #print traceback.#print_exc()
        status_code = 500
        return status_code

# #############################################################################


# To run analysis on uploaded file
def td_main2(kw_str, tddict):
    global status_code

    if ".csv" in kw_str:
        kw_str = kw_str[:-4]
    print("product category :>", kw_str)

    try:
        # keywords_dict_file = dbConfig.dict['keywordsDict']
        keywords_dict_file = tddict
        kw_file = pd.read_csv(keywords_dict_file)
        triggers = []
        drivers = []
        for i, r in kw_file.iterrows():
            if 'trigger' in str(r['ToD']).lower() and r['Types'] not in triggers:
                triggers.append(r['Types'])
            elif 'driver' in str(r['ToD']).lower() and r['Types'] not in drivers:
                drivers.append(r['Types'])

        #print(triggers)
        #print(drivers)

        # NOT USED -
        #triggers = ['Upgrade', 'Replace', 'FirstTimeBuyer', 'Gift', 'Marketing-Sale']
        # subtriggers = ['Upgrade_Upgrade',
        #                'Replace_Replace',
        #                'FirstTimeBuyer_FirstTimeBuyer',
        #                'Gift_Birthday',
        #                'Gift_Wedding',
        #                'Gift_Christmas',
        #                'Gift_Other',
        #                'Marketing-Sale_Marketing-Sale']
        #drivers = ['Brand', 'Cost', 'Recommendation', 'Innovation', 'Marketing-Ads']
        # subdrivers = ['Brand_Brand',
        #               'Cost_Cost',
        #               'Recommendation_Recommendation',
        #               'Innovation_Innovation',
        #               'Marketing-Ads_TV',
        #               'Marketing-Ads_Radio',
        #               'Marketing-Ads_Outdoor',
        #               'Marketing-Ads_Other']

        start_time = time()

        revs_df = Uploads.objects.filter(pCategory=kw_str).only('rid', 'rText').values()

        for r in revs_df:

            curr_rev = r['rText'].encode('utf-8')

            try:
                analysis_obj = UploadAnalyses.objects.get(rid_id=r['rid'])
            except:
                analysis_obj = UploadAnalyses.objects.create(rid_id=r['rid'])

            kw = pd.read_csv(keywords_dict_file)

            for each_kw in range(len(kw)):
                # #print("each_kw:" + str(each_kw))

                if re.findall(kw.ix[each_kw, 'Keywords'], curr_rev, re.I):

                    # if kw.ix[each_kw, 'Types'] in triggers:
                    if str(kw.ix[each_kw, 'Subtypes']).split("_")[0] in triggers:  # main trig of this subtype
                        old_trig_obj = analysis_obj.trigger

                        if old_trig_obj:
                            old_trig_str = old_trig_obj
                        else:
                            old_trig_str = " "

                        #print("old trig str: " + old_trig_str)

                        if not old_trig_str == " ":
                            analysis_obj.trigger = old_trig_str + "," + str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.trigger)
                        else:
                            analysis_obj.trigger = str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.trigger)

                    elif kw.ix[each_kw, 'Subtypes'].split("_")[0] in drivers:
                        # elif kw.ix[each_kw, 'Types'] in drivers:
                        old_driv_obj = analysis_obj.driver

                        if old_driv_obj:
                            old_driv_str = old_driv_obj
                        else:
                            old_driv_str = " "

                        #print("old driv str: " + old_driv_str)

                        if not old_driv_str == " ":
                            analysis_obj.driver = old_driv_str + "," + str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.driver)
                        else:
                            analysis_obj.driver = str(kw.ix[each_kw, 'Subtypes'])
                            #print("Updated value: ")
                            #print(analysis_obj.driver)

                    try:
                        #print(analysis_obj.trigger, analysis_obj.driver)
                        analysis_obj.save()
                    except:
                        pass
                        #print("Error while updating uploadanalyses table!")
                        #print(traceback.print_exc())

        end_time = time()

        #print "Running Time : " + str(end_time - start_time) + " secs"

        status_code = 200
        return status_code

    except:
        #print("Error in TrigDriv_2!")
        #print traceback.#print_exc()
        status_code = 500
        return status_code
