
import json
import re
from django.core.serializers.json import DjangoJSONEncoder
import django
django.setup()
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses
from django.db.models import Count,Avg
from django.utils.dateformat import format
import time, datetime
from operator import itemgetter


def getBrand(kw):
    brands = Product.objects.filter(pCategory=kw).distinct().values('pBrand')  # to return dictionary of values for each column
    #brands = Product.objects.filter(pCategory=request).distinct().values_list('pBrand', flat=True)  # to return only values of that column
    brands_json = json.dumps(list(brands), cls=DjangoJSONEncoder)
    return brands_json


def getSource(kw, brand):
    sources = Product.objects.filter(pCategory=kw, pBrand__in=brand).distinct().values('siteCode')  # to return dictionary of values for each column
    print(sources)
    sources_json = json.dumps(list(sources), cls=DjangoJSONEncoder)
    return sources_json


def getSku(kw, brand, source):
    sku = Product.objects.filter(pCategory=kw, pBrand__in=brand, siteCode__in=source).distinct().values('pModel')  # to return dictionary of values for each column
    sku_json = json.dumps(list(sku), cls=DjangoJSONEncoder)
    return sku_json


def neighborhood(iterable):
    iterator = iter(iterable)
    prev_item = None
    current_item = next(iterator)  # throws StopIteration if empty.
    for next_item in iterator:
        yield (prev_item, current_item, next_item)
        prev_item = current_item
        current_item = next_item
    yield (prev_item, current_item, None)


def getBrandSummaryChart(kw, brand, source, sku, fromDate, toDate):
    #print("Inside getbrandsummarychart()")
    if fromDate == "" or toDate == "":
        data2 = Review.objects.filter\
            (pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source, pid__pModel__in=sku)\
            .values_list('pid__pBrand', 'pid__pModel')\
            .annotate(average_rating=Avg('pid__pRating'))
        data1 = Review.objects.filter\
            (pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source, pid__pModel__in=sku).values_list('pid__pBrand')\
            .annotate(average_rating=Avg('pid__pRating'))
    else:
        data2 = Review.objects.filter\
            (pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source, pid__pModel__in=sku, rDate2__range=[fromDate, toDate])\
            .values_list('pid__pBrand','pid__pModel')\
            .annotate(average_rating=Avg('pid__pRating'))
        data1 = Review.objects.filter\
            (pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source, pid__pModel__in=sku, rDate2__range=[fromDate, toDate])\
            .values_list('pid__pBrand')\
            .annotate(average_rating=Avg('pid__pRating'))

    a = list(data1)
    a = sorted(a, key=itemgetter(1), reverse=True)
    print(a)
    b = list(data2)
    b = sorted(b, key=itemgetter(2), reverse=True)
    print(b)
    #print("--------------------------------------------------------------")
    #print("--------------------------------------------------------------")
    #print("Query= ", data2.query)
    dict1 = {}
    response1 = []
    #print(data_json1)
    #print("--------------------------------------------------------------")
    #a
    # [["Element", 4.0], ["Samsung", 1.0], ["Sceptre", 4.03975], ["Seiki", 3.0], ["TCL", 4.33846], ["VIZIO", 4.5]]
    #b
    # [["Element", "B01HQS8UZA", 4.0], ["Samsung", "301688015", 1.0], ["Sceptre", "27678567", 4.0],
    #  ["Sceptre", "55042148", 4.5], ["Sceptre", "55427159", 3.5], ["Sceptre", "B00W2T70IM", 4.2],
    #  ["Seiki", "55277725", 3.0], ["TCL", "B01MTGM5I9", 4.8], ["TCL", "B01MU1GBLL", 4.2], ["VIZIO", "49228250", 4.5]]
    for i in a:
        dict1["name"] = i[0]
        dict1["y"] = i[1]
        dict1["drilldown"] = i[0]
        response1.append(dict1)
        dict1 = {}

    series = []
    temp_list = []
    temp1 = []
    dict2 = {}

    for prev, item, next in neighborhood(b):
        if next is not None:
            if item[0] == next[0]:
                temp_list.append(item[1])
                temp_list.append(item[2])
                temp1.append(temp_list)
                temp_list = []
                continue
            else:
                temp_list.append(item[1])
                temp_list.append(item[2])
                temp1.append(temp_list)
        else:
            temp_list.append(item[1])
            temp_list.append(item[2])
            temp1.append(temp_list)

        dict2["name"] = item[0]
        dict2["id"] = item[0]
        dict2["data"] = temp1
        series.append(dict2)
        dict2 = {}
        temp1 = []
        temp_list = []

    dict2['series'] = series
    response = {}
    response['response1'] = response1
    response['dict2'] = dict2
    #print response
    response_json = json.dumps(response, cls=DjangoJSONEncoder)
    return response_json


def getChart1(kw, brand, source, sku, fromDate, toDate):
    print("inside analysis service - getChart1Data")

    s = ["Positive", "Negative", "Neutral"]

    if fromDate == "" or toDate == "":
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, sentiment__in=s) \
            .values_list('rid__pid__pBrand', 'sentiment') \
            .annotate(senti_count=Count('sentiment'))

        data1 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, sentiment__in=s) \
            .values_list('rid__pid__pBrand', 'rid__pid__pModel', 'sentiment') \
            .annotate(senti_count=Count('sentiment'))

    else:
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate], sentiment__in=s) \
            .values_list('rid__pid__pBrand', 'sentiment') \
            .annotate(senti_count=Count('sentiment'))

        data1 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate], sentiment__in=s) \
            .values_list('rid__pid__pBrand', 'rid__pid__pModel', 'sentiment') \
            .annotate(senti_count=Count('sentiment'))

    temp_brand_senti = []
    brand_senti = []
    brand_senti_count_dict = {"name": "", "y": 0.0, "drilldown": ""}

    temp_sku_senti = []
    sku_senti = []
    sku_senti_count_dict = {"id": "", "name": "", "data": []}

    for b in brand:
        #print(b)
        brand_senti_count_dict["name"] = b
        brand_senti_count_dict["drilldown"] = b
        brand_senti_total_count = 0
        brand_positivity = 0
        for i in data2:
            #print(i)  # i = [pBrand, sentiment, senti_count]
            if i[0] == b:
                if i[1] == "Positive":
                    brand_positivity = i[2]
                brand_senti_total_count += i[2]

        try:
            brand_senti_count_dict["y"] = float(brand_positivity)/float(brand_senti_total_count)*100
        except:
            brand_senti_count_dict["y"] = 0.0
        temp_brand_senti.append(brand_senti_count_dict.copy())

    for b in brand:
        #print(b)
        sku_senti_count_dict["name"] = b
        sku_senti_count_dict["id"] = b
        sku_senti_count_dict["data"] = []
        curr_sku = ""
        sku_senti_total_count = 0
        sku_positivity = 0

        brand_wise_sku = data1.filter(rid__pid__pBrand=b).values_list("rid__pid__pModel", flat=True).distinct()
        #print(list(brand_wise_sku))

        for s in brand_wise_sku:
            data_list = []
            for i in data1:
                # print(i)  # i = [pBrand, pModel, sentiment, senti_count]
                if i[0] == b and i[1] == s:
                    #print(i)
                    curr_sku = i[1]
                    if i[2] == "Positive":
                        sku_positivity = i[3]
                    sku_senti_total_count += i[3]
            # print("sku_positivity " + str(sku_positivity) + " sku_senti_total_count " + str(sku_senti_total_count))
            data_list.append(curr_sku)
            try:
                data_list.append(float(sku_positivity) / float(sku_senti_total_count) * 100)
            except:
                data_list.append(float(0.0))
            sku_senti_count_dict["data"].append(data_list)
            #print(sku_senti_count_dict)
            temp_sku_senti.append(sku_senti_count_dict.copy())
    # 'for b in brands' ends here

    while temp_brand_senti:
        maxYItem = max(temp_brand_senti, key=lambda x: x['y'])
        brand_senti.append(maxYItem)
        temp_brand_senti.remove(maxYItem)

    for t in temp_sku_senti:
        t["data"].sort(key=lambda x: x[1], reverse=True)

    while temp_sku_senti:
        maxDataItem = max(temp_sku_senti, key=lambda x: x['data'])
        sku_senti.append(maxDataItem)
        temp_sku_senti.remove(maxDataItem)

    data_json = json.dumps([brand_senti, sku_senti], cls=DjangoJSONEncoder)

    #print("data json")
    #print(main_trigs)
    #print(sub_trigs)

    #print("returning from analysis service")
    return data_json


def getChart2(kw, brand, source, sku, fromDate, toDate):
    print("inside analysis service - getChart2Data")
    #print(type(source))
    #print(source)

    if fromDate == "" or toDate == "":
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku) \
            .values_list('rid__pid__siteCode', 'sentiment') \
            .annotate(senti_count=Count('sentiment'))

    else:
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate]) \
            .values_list('rid__pid__siteCode', 'sentiment') \
            .annotate(senti_count=Count('sentiment'))

    #print(len(list(data2)))
    #print(list(data2))

    site_senti_dict = {}
    senti_dict_list = []

    for s in source:
        sentiment_flags = [False, False, False]  # For [positive, negative, neutral]
        senti_counts = [0, 0, 0]

        if s == "AM":
            site_senti_dict["name"] = "Amazon"
        elif s == "HD":
            site_senti_dict["name"] = "HomeDepot"
        elif s == "WM":
            site_senti_dict["name"] = "Walmart"
        else:
            site_senti_dict["name"] = "Other"

        for d in list(data2):
            # d = (siteCode, sentiment, count)
            # print(d[0])
            # print(d[1])
            if d[0] == s:

                if d[1] == "Positive":
                    senti_counts[0] = d[2]
                    sentiment_flags[0] = True
                elif d[1] == "Negative":
                    senti_counts[1] = d[2]
                    sentiment_flags[1] = True
                elif d[1] == "Neutral":
                    senti_counts[2] = d[2]
                    sentiment_flags[2] = True

        site_senti_dict["data"] = senti_counts

        senti_dict_list.append(site_senti_dict.copy())
        #print "---------------"

    # 'for' loop through unique sites ends here
    print senti_dict_list

    data_json = json.dumps(senti_dict_list, cls=DjangoJSONEncoder)
    return data_json


def getChart3(kw, brand, source, sku, fromDate, toDate):
    print("inside analysis service - getChart3Data")

    if fromDate == "" or toDate == "":
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku) \
            .values('trigger')

    else:
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate]) \
            .values('trigger')

    trigs_total_count = 0
    main_trigs = []
    main_trigs_count_dict = {"name": "", "y": 0, "drilldown": ""}
    sub_trigs = []
    sub_trigs_count_dict = {"id": "", "name": "", "data": []}

    for i in data2:  # for i in a:
        # print(i.get('trigger'))
        if i.get('trigger') and re.search(r'[a-zA-Z]+', i.get('trigger')):
            curr_trigs = str(i.get('trigger')).split(",")

            for c in curr_trigs:
                trig_drill = str(c).split("_")

                mt_flag = False
                for mt in range(len(main_trigs)):
                    if main_trigs[mt]["name"] == trig_drill[0]:  # if main trigger listed already
                        mt_flag = True
                        # print("main trigger already listed")
                        main_trigs[mt]["y"] += 1
                        if trig_drill[1] == trig_drill[0]:  # if main trigger doesnt have subtrigger
                            pass  # nothing to do as dummy entry already exists
                        else:  # if main trigger has subtrigger
                            st_flag = False  # to indicate if subtrigger value has been incremented

                            for st in range(len(sub_trigs)):  # check if it is listed and update value
                                if sub_trigs[st]["id"] == trig_drill[0]:

                                    # st_idx = 0
                                    for st_d in range(len(sub_trigs[st]["data"])):  # this loop to check if entry already exists and increment
                                        if trig_drill[1] == sub_trigs[st]["data"][st_d][0]:  # if main trigger listed and subtrigger also listed
                                            sub_trigs[st]["data"][st_d][1] += 1
                                            st_flag = True

                            if not st_flag:  # if subtrigger is not listed then append
                                dd_data_list = sub_trigs[st]["data"]
                                dd_data_list.append([trig_drill[1], 1])
                                sub_trigs[st]["data"] = dd_data_list

                if not mt_flag:  # if main trigger is not already listed
                    # print("main trig not already listed")
                    # main_trigs.append(trig_drill[0])
                    # main_trigs_count.append(i.get('trigger__count'))
                    main_trigs_count_dict["name"] = trig_drill[0]
                    main_trigs_count_dict["y"] = 1
                    if trig_drill[1] == trig_drill[0]:
                        main_trigs_count_dict["drilldown"] = None
                    else:
                        main_trigs_count_dict["drilldown"] = trig_drill[0]
                    main_trigs.append(main_trigs_count_dict.copy())

                    if trig_drill[1] == trig_drill[0]:  # if main trigger has no sub triggers, create dummy
                        pass  # nothing to do
                    else:  # if main trigger has sub triggers, append to data list
                        sub_trigs_count_dict["name"] = trig_drill[0]
                        sub_trigs_count_dict["id"] = trig_drill[0]
                        sub_trigs_count_dict["data"].append([trig_drill[1], 1])
                        sub_trigs.append(sub_trigs_count_dict.copy())

    trigs_total_count = sum([item['y'] for item in main_trigs])

    for m_t in range(len(main_trigs)):
        main_trigs[m_t]["y"] = float(main_trigs[m_t]["y"])/float(trigs_total_count)*100

    for s_t in range(len(sub_trigs)):
        sub_trigs_count = sum([d[1] for d in sub_trigs[s_t]["data"]])
        for d in range(len(sub_trigs[s_t]["data"])):
            sub_trigs[s_t]["data"][d][1] = float(sub_trigs[s_t]["data"][d][1])/float(sub_trigs_count)*100

    data_json = json.dumps([main_trigs, sub_trigs], cls=DjangoJSONEncoder)

    #print("data json")
    #print(main_trigs)
    #print(sub_trigs)

    #print("returning from analysis service")
    return data_json


def getCommonTrigChart(kw):
    print("inside analysis service - getCommonTrigChart")
    kw = str(kw)[:len(kw) - 4]

    data1 = Uploads.objects.filter(pCategory=kw).values_list('rid')
    #print("data1")
    #print(list(data1))

    data2 = UploadAnalyses.objects \
        .filter(rid_id__in=data1) \
        .values('trigger')
    print("data2")
    print(list(data2))

    trigs_total_count = 0
    main_trigs = []
    main_trigs_count_dict = {"name": "", "y": 0, "drilldown": ""}
    sub_trigs = []
    sub_trigs_count_dict = {"id": "", "name": "", "data": []}

    for i in data2:  # for i in a:
        #print("This is i")
        #print(type(i))
        if i.get('trigger') and re.search(r'[a-zA-Z]+', i.get('trigger')):
            curr_trigs = str(i.get('trigger')).split(",")

            for c in curr_trigs:
                trig_drill = str(c).split("_")

                mt_flag = False
                for mt in range(len(main_trigs)):
                    if main_trigs[mt]["name"] == trig_drill[0]:  # if main trigger listed already
                        mt_flag = True
                        # print("main trigger already listed")
                        main_trigs[mt]["y"] += 1
                        if trig_drill[1] == trig_drill[0]:  # if main trigger doesnt have subtrigger
                            pass  # nothing to do as dummy entry already exists
                        else:  # if main trigger has subtrigger
                            st_flag = False  # to indicate if subtrigger value has been incremented

                            for st in range(len(sub_trigs)):  # check if it is listed and update value
                                if sub_trigs[st]["id"] == trig_drill[0]:

                                    # st_idx = 0
                                    for st_d in range(len(sub_trigs[st]["data"])):  # this loop to check if entry already exists and increment
                                        if trig_drill[1] == sub_trigs[st]["data"][st_d][0]:  # if main trigger listed and subtrigger also listed
                                            sub_trigs[st]["data"][st_d][1] += 1
                                            st_flag = True

                            if not st_flag:  # if subtrigger is not listed then append
                                dd_data_list = sub_trigs[st]["data"]
                                dd_data_list.append([trig_drill[1], 1])
                                sub_trigs[st]["data"] = dd_data_list

                if not mt_flag:  # if main trigger is not already listed
                    # print("main trig not already listed")
                    # main_trigs.append(trig_drill[0])
                    # main_trigs_count.append(i.get('trigger__count'))
                    main_trigs_count_dict["name"] = trig_drill[0]
                    main_trigs_count_dict["y"] = 1
                    if trig_drill[1] == trig_drill[0]:
                        main_trigs_count_dict["drilldown"] = None
                    else:
                        main_trigs_count_dict["drilldown"] = trig_drill[0]
                    main_trigs.append(main_trigs_count_dict.copy())

                    if trig_drill[1] == trig_drill[0]:  # if main trigger has no sub triggers, create dummy
                        pass  # nothing to do
                    else:  # if main trigger has sub triggers, append to data list
                        sub_trigs_count_dict["name"] = trig_drill[0]
                        sub_trigs_count_dict["id"] = trig_drill[0]
                        sub_trigs_count_dict["data"].append([trig_drill[1], 1])
                        sub_trigs.append(sub_trigs_count_dict.copy())

    trigs_total_count = sum([item['y'] for item in main_trigs])

    for m_t in range(len(main_trigs)):
        main_trigs[m_t]["y"] = float(main_trigs[m_t]["y"])/float(trigs_total_count)*100

    for s_t in range(len(sub_trigs)):
        sub_trigs_count = sum([d[1] for d in sub_trigs[s_t]["data"]])
        for d in range(len(sub_trigs[s_t]["data"])):
            sub_trigs[s_t]["data"][d][1] = float(sub_trigs[s_t]["data"][d][1])/float(sub_trigs_count)*100

    data_json = json.dumps([main_trigs, sub_trigs], cls=DjangoJSONEncoder)

    #print("data json")
    #print(main_trigs)
    #print(sub_trigs)

    #print("returning from analysis service")
    return data_json


def getChart4(kw, brand, source, sku, fromDate, toDate):
    print("inside analysis service - getChart4Data")

    if fromDate == "" or toDate == "":
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku) \
            .values('driver')

    else:
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate]) \
            .values('driver')

    drivs_total_count = 0
    main_drivs = []
    main_drivs_count_dict = {"name": "", "y": 0, "drilldown": ""}
    sub_drivs = []
    sub_drivs_count_dict = {"id": "", "name": "", "data": []}

    for i in data2:
        if i.get('driver') and re.search(r'[a-zA-Z]+', i.get('driver')):
            curr_drivs = str(i.get('driver')).split(",")

            for c in curr_drivs:
                driv_drill = str(c).split("_")

                md_flag = False
                for md in range(len(main_drivs)):
                    if main_drivs[md]["name"] == driv_drill[0]:  # if main driver listed already
                        md_flag = True
                        # print("main driver already listed")
                        main_drivs[md]["y"] += 1
                        if driv_drill[1] == driv_drill[0]:  # if main driver doesnt have subdriver
                            pass  # nothing to do as dummy entry already exists
                        else:  # if main driver has subdriver
                            sd_flag = False  # to indicate if subdriver value has been incremented

                            for sd in range(len(sub_drivs)):  # check if it is listed and update value
                                if sub_drivs[sd]["id"] == driv_drill[0]:

                                    # st_idx = 0
                                    for sd_d in range(len(sub_drivs[sd]["data"])):  # this loop to check if entry already exists and increment
                                        if driv_drill[1] == sub_drivs[sd]["data"][sd_d][0]:  # if main driver listed and subdriver also listed
                                            sub_drivs[sd]["data"][sd_d][1] += 1
                                            sd_flag = True

                            if not sd_flag:  # if subdriver is not listed then append
                                dd_data_list = sub_drivs[sd]["data"]
                                dd_data_list.append([driv_drill[1], 1])
                                sub_drivs[sd]["data"] = dd_data_list

                if not md_flag:  # if main driver is not already listed
                    main_drivs_count_dict["name"] = driv_drill[0]
                    main_drivs_count_dict["y"] = 1
                    if driv_drill[1] == driv_drill[0]:
                        main_drivs_count_dict["drilldown"] = None
                    else:
                        main_drivs_count_dict["drilldown"] = driv_drill[0]
                    main_drivs.append(main_drivs_count_dict.copy())

                    if driv_drill[1] == driv_drill[0]:  # if main driver has no sub drivers, create dummy
                        pass  # nothing to do
                    else:  # if main driver has sub drivers, append to data list
                        sub_drivs_count_dict["name"] = driv_drill[0]
                        sub_drivs_count_dict["id"] = driv_drill[0]
                        sub_drivs_count_dict["data"].append([driv_drill[1], 1])
                        sub_drivs.append(sub_drivs_count_dict.copy())

    drivs_total_count = sum([item['y'] for item in main_drivs])

    for m_d in range(len(main_drivs)):
        main_drivs[m_d]["y"] = float(main_drivs[m_d]["y"])/float(drivs_total_count)*100

    for s_d in range(len(sub_drivs)):
        sub_drivs_count = sum([d[1] for d in sub_drivs[s_d]["data"]])
        for d in range(len(sub_drivs[s_d]["data"])):
            sub_drivs[s_d]["data"][d][1] = float(sub_drivs[s_d]["data"][d][1])/float(sub_drivs_count)*100

    data_json = json.dumps([main_drivs, sub_drivs], cls=DjangoJSONEncoder)

    # print("data json")
    # print(main_drivs)
    # print(sub_drivs)
    #
    # print("returning from analysis service")
    return data_json


def getCommonDrivChart(kw):
    print("inside analysis service - getCommonDrivChart")
    kw = str(kw)[:len(kw) - 4]

    data1 = Uploads.objects.filter(pCategory=kw).values_list('rid')
    # print("data1")
    # print(list(data1))

    data2 = UploadAnalyses.objects \
        .filter(rid_id__in=data1) \
        .values('driver')

    drivs_total_count = 0
    main_drivs = []
    main_drivs_count_dict = {"name": "", "y": 0, "drilldown": ""}
    sub_drivs = []
    sub_drivs_count_dict = {"id": "", "name": "", "data": []}

    for i in data2:
        if i.get('driver') and re.search(r'[a-zA-Z]+', i.get('driver')):
            curr_drivs = str(i.get('driver')).split(",")

            for c in curr_drivs:
                driv_drill = str(c).split("_")

                md_flag = False
                for md in range(len(main_drivs)):
                    if main_drivs[md]["name"] == driv_drill[0]:  # if main driver listed already
                        md_flag = True
                        # print("main driver already listed")
                        main_drivs[md]["y"] += 1
                        if driv_drill[1] == driv_drill[0]:  # if main driver doesnt have subdriver
                            pass  # nothing to do as dummy entry already exists
                        else:  # if main driver has subdriver
                            sd_flag = False  # to indicate if subdriver value has been incremented

                            for sd in range(len(sub_drivs)):  # check if it is listed and update value
                                if sub_drivs[sd]["id"] == driv_drill[0]:

                                    # st_idx = 0
                                    for sd_d in range(len(sub_drivs[sd]["data"])):  # this loop to check if entry already exists and increment
                                        if driv_drill[1] == sub_drivs[sd]["data"][sd_d][0]:  # if main driver listed and subdriver also listed
                                            sub_drivs[sd]["data"][sd_d][1] += 1
                                            sd_flag = True

                            if not sd_flag:  # if subdriver is not listed then append
                                dd_data_list = sub_drivs[sd]["data"]
                                dd_data_list.append([driv_drill[1], 1])
                                sub_drivs[sd]["data"] = dd_data_list

                if not md_flag:  # if main driver is not already listed
                    main_drivs_count_dict["name"] = driv_drill[0]
                    main_drivs_count_dict["y"] = 1
                    if driv_drill[1] == driv_drill[0]:
                        main_drivs_count_dict["drilldown"] = None
                    else:
                        main_drivs_count_dict["drilldown"] = driv_drill[0]
                    main_drivs.append(main_drivs_count_dict.copy())

                    if driv_drill[1] == driv_drill[0]:  # if main driver has no sub drivers, create dummy
                        pass  # nothing to do
                    else:  # if main driver has sub drivers, append to data list
                        sub_drivs_count_dict["name"] = driv_drill[0]
                        sub_drivs_count_dict["id"] = driv_drill[0]
                        sub_drivs_count_dict["data"].append([driv_drill[1], 1])
                        sub_drivs.append(sub_drivs_count_dict.copy())

    drivs_total_count = sum([item['y'] for item in main_drivs])

    for m_d in range(len(main_drivs)):
        main_drivs[m_d]["y"] = float(main_drivs[m_d]["y"])/float(drivs_total_count)*100

    for s_d in range(len(sub_drivs)):
        sub_drivs_count = sum([d[1] for d in sub_drivs[s_d]["data"]])
        for d in range(len(sub_drivs[s_d]["data"])):
            sub_drivs[s_d]["data"][d][1] = float(sub_drivs[s_d]["data"][d][1])/float(sub_drivs_count)*100

    data_json = json.dumps([main_drivs, sub_drivs], cls=DjangoJSONEncoder)

    # print("data json")
    # print(main_drivs)
    # print(sub_drivs)
    #
    # print("returning from analysis service")
    return data_json


def getCommonSentiChart(kw):
    print("inside analysis service - getCommonSentiChart()")
    kw = str(kw)[:len(kw)-4]
    print(kw)

    data1 = Uploads.objects.filter(pCategory=kw).values_list('rid')
    print(list(data1))

    data2 = UploadAnalyses.objects \
        .filter(rid_id__in=data1) \
        .values_list('sentiment') \
        .annotate(senti_count=Count('sentiment'))

    print(len(list(data2)))
    print(list(data2))

    senti_dict = {}
    senti_dict_list = []
    #sentiment_flags = [False, False, False]  # For [positive, negative, neutral]
    senti_counts = [0, 0, 0]

    for d in list(data2):
        # d = (sentiment, count)
        #print(d[0])
        #print(d[1])

        if d[0] == "Positive":
            senti_counts[0] = d[1]
            #sentiment_flags[0] = True
        elif d[0] == "Negative":
            senti_counts[1] = d[1]
            #sentiment_flags[1] = True
        elif d[0] == "Neutral":
            senti_counts[2] = d[1]
            #sentiment_flags[2] = True

    senti_dict["data"] = senti_counts
    senti_dict["name"] = "Overall"

    senti_dict_list.append(senti_dict.copy())

    print senti_dict_list

    data_json = json.dumps(senti_dict_list, cls=DjangoJSONEncoder)
    return data_json
