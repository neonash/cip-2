import json
import pandas as pd
from django.core.serializers.json import DjangoJSONEncoder
import django
django.setup()
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses
from django.db.models import Count,Avg
from django.utils.dateformat import format
import time, datetime
from atlas.config import dbConfig
from django.core import serializers


def getCountRevCards(kw, brand, source, sku, fromDate, toDate):
    if fromDate == "" or toDate == "":

        print(brand,source,sku)
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku) \
            .values_list('sentiment') \
            .annotate(senti_count=Count('sentiment'))

    else:
        data2 = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate]) \
            .values_list('sentiment') \
            .annotate(senti_count=Count('sentiment'))

    print(data2)

    count_list = list()
    totalCount = 0
    posCount = 0
    negCount = 0

    for d in data2:
        if d[0] == "Positive":
            posCount = d[1]
        elif d[0] == "Negative":
            negCount = d[1]
        totalCount += d[1]
    count_list.extend([totalCount, posCount, negCount])
    print(count_list)
    data_json = json.dumps(count_list, cls=DjangoJSONEncoder)
    return data_json


def getCountRevCardsOverall(kw):
    kw = str(kw)[:len(kw) - 4]
    rid_list = Uploads.objects.filter(pCategory=kw).values_list('rid')
    data2 = UploadAnalyses.objects.filter(rid_id__in=rid_list).values_list('sentiment') \
        .annotate(senti_count=Count('sentiment'))

    # print(data2)

    count_list = list()
    totalCount = 0
    posCount = 0
    negCount = 0

    for d in data2:
        if d[0] == "Positive":
            posCount = d[1]
        elif d[0] == "Negative":
            negCount = d[1]
        totalCount += d[1]

    count_list.extend([totalCount, posCount, negCount])
    data_json = json.dumps(count_list)
    return data_json


def getTopposneg(kw, brand, source, sku, fromDate, toDate):
    p_flag = False  # set true if no records tagged positive
    n_flag = False  # set to True if no records tagged negative
    pos_data = None
    neg_data = None
    if fromDate == "" or toDate == "":

        top_pos_ids = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, sentiment='Positive') \
            .order_by('-sentiScore') \
            .values_list('rid_id', flat=True)[:2]
        top_pos_ids1 = list(top_pos_ids)
        print(top_pos_ids1)

        if not top_pos_ids1:
            print("No records tagged positive!!")
            p_flag = True

        if not p_flag:  # if there are positive reviews
            pos_data = Review.objects.filter(rid__in=top_pos_ids1).only('rTitle', 'rText')
            print(pos_data)

        top_neg_ids = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, sentiment='Negative') \
            .order_by('sentiScore') \
            .values_list('rid_id', flat=True)[:2]
        top_neg_ids1 = list(top_neg_ids)
        print(top_neg_ids1)

        if not top_neg_ids1:
            print("No records tagged negative!!")
            n_flag = True

        if not n_flag:
            neg_data = Review.objects.filter(rid__in=top_neg_ids1).only('rTitle', 'rText')
            print(neg_data)

    else:

        top_pos_ids = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate], sentiment='Positive') \
            .order_by('-sentiScore') \
            .values_list('rid_id', flat=True)[:2]
        top_pos_ids1 = list(top_pos_ids)
        print(top_pos_ids1)

        if not top_pos_ids1:
            print("No records were tagged positive!")
            p_flag=True

        if not p_flag:
            pos_data = Review.objects.filter(rid__in=top_pos_ids1).only('rTitle', 'rText')
            print(pos_data)

        top_neg_ids = Analysis.objects \
            .filter(rid__pid__pCategory=kw, rid__pid__pBrand__in=brand, rid__pid__siteCode__in=source,
                    rid__pid__pModel__in=sku, rid__rDate2__range=[fromDate, toDate], sentiment='Negative') \
            .order_by('sentiScore') \
            .values_list('rid_id', flat=True)[:2]
        top_neg_ids1 = list(top_neg_ids)
        print(top_neg_ids1)

        if not top_neg_ids1:
            print("No records were tagged negative!")
            n_flag = True

        if not n_flag:
            neg_data = Review.objects.filter(rid__in=top_neg_ids1).only('rTitle', 'rText')
            print(neg_data)

    if not p_flag and not n_flag:
        data = pos_data.union(neg_data)
    elif not p_flag and n_flag:
        data = pos_data
    elif p_flag and not n_flag:
        data = neg_data
    else:
        print("No data to show!")
        data = [0]
    print(data)

    data1 = serializers.serialize("json", data)
    data_json = json.dumps(data1, cls=DjangoJSONEncoder)
    return data_json


def getTopposnegOverall(kw):
    kw = str(kw)[:len(kw) - 4]

    top_pos_ids = UploadAnalyses.objects.filter(rid__pCategory=kw, sentiment='Positive').order_by('-sentiScore') \
            .values_list('rid_id', flat=True)[:2]
    top_pos_ids1 = list(top_pos_ids)
    print(top_pos_ids1)

    top_neg_ids = UploadAnalyses.objects.filter(rid__pCategory=kw, sentiment='Negative').order_by('sentiScore') \
                   .values_list('rid_id', flat=True)[:2]
    top_neg_ids1 = list(top_neg_ids)
    print(top_neg_ids1)

    #id_list = list(top_pos['rid_id'])
    #print(id_list)
    pos_data = Uploads.objects.filter(rid__in=top_pos_ids1).only('rTitle','rText')
    print(pos_data)
    neg_data = Uploads.objects.filter(rid__in=top_neg_ids1).only('rTitle','rText')
    print(neg_data)


    #data = list()
    #data.append(pos_data)
    #data.append(neg_data)

    data = pos_data.union(neg_data)
    print("Printing data")
    print(data)

    data1 = serializers.serialize("json", data)
    data_json = json.dumps(data1, cls=DjangoJSONEncoder)
    return data_json


def getBrand(kw):
    brands = Product.objects.filter(pCategory=kw).distinct().values('pBrand')  # to return dictionary of values for each column
    #brands = Product.objects.filter(pCategory=request).distinct().values_list('pBrand', flat=True)  # to return only values of that column
    brands_json = json.dumps(list(brands), cls=DjangoJSONEncoder)
    return brands_json


def getSource(kw, brand):
    #sources = Product.objects.filter(pCategory=kw, pBrand__in=brand).distinct().values_list('siteCode', flat=True, flat=True)  # to return dictionary of values for each column
    sources = Product.objects.filter(pCategory=kw, pBrand__in=brand).distinct().values('siteCode')  # to return dictionary of values for each column
    # sources_file = pd.read_csv(dbConfig.dict['sourcesUrl'], header=0)
    # sources1 = []
    # for s in list(sources):
    #   sources1.append([r['siteName'] for i, r in sources_file.iterrows() if s == r['siteCode']])
    # print(sources1)
    sources_json = json.dumps(list(sources), cls=DjangoJSONEncoder)
    #print sources_json
    return sources_json


def getSourceRevmap1(source_vals):
    sources_file = pd.read_csv(dbConfig.dict['sourcesUrl'], header=0)
    sources1 = []

    for s in list(source_vals):
        sources1.append([r['siteCode'] for i, r in sources_file.iterrows() if s == r['siteName']])
    print(sources1)
    sources_json = json.dumps(list(sources1), cls=DjangoJSONEncoder)
    print sources_json
    return sources_json


def getSku(kw, brand, source):
    sku = Product.objects.filter(pCategory=kw, pBrand__in=brand, siteCode__in=source).distinct().values('pModel')  # to return dictionary of values for each column
    sku_json = json.dumps(list(sku), cls=DjangoJSONEncoder)
    return sku_json


def getChart1(kw, brand, source, sku, fromDate, toDate):
    dates = Review.objects.values_list('rDate')
    dates2 = Review.objects.values_list('rDate2')
    data = dates.annotate(Count('rid')).filter(pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source
                                               , pid__pModel__in=sku).order_by('rDate')
    if (fromDate == "" or toDate == ""):
        data2 = dates2.annotate(Count('rid')).filter(pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source
                                                   , pid__pModel__in=sku).order_by('rDate2')
    else:
        data2 = dates2.annotate(Count('rid')).filter(pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source
                                                    , pid__pModel__in=sku, rDate2__range=[fromDate, toDate]).order_by('rDate2')

    d2 = list(data2)
    a = list(data)
    # print(a)
    # print(d2)
    c = [[int(time.mktime(b[0].timetuple()))*1000, b[1]] for b in d2]
    #print("--------------------------------------------------------------")
    #print(dir(data))
    #print(c)
    #print("--------------------------------------------------------------")
    #print("Query= ", data.query)
    data_json = json.dumps(c, cls=DjangoJSONEncoder)
    #print(data_json)
    return data_json


def getCommonReviewCountChart(kw):
    print("Inside getCommonReviewCount")
    kw = str(kw)[:len(kw) - 4]

    data1 = Uploads.objects.filter(pCategory=kw).values_list('rid')

    dates = Uploads.objects.filter(pCategory=kw).values_list('rDate')
    dates2 = Uploads.objects.filter(pCategory=kw).values_list('rDate2')

    data = dates.annotate(Count('rid')).filter(rid__in=data1).order_by('rDate')
    print(data)

    a = list(data)

    c = [[int(time.mktime(b[0].timetuple()))*1000, b[1]] for b in a]
    #print("--------------------------------------------------------------")
    #print(dir(data))
    #print(c)
    #print("--------------------------------------------------------------")
    #print("Query= ", data.query)
    data_json = json.dumps(c, cls=DjangoJSONEncoder)
    #print(data_json)
    return data_json


def neighborhood(iterable):
    iterator = iter(iterable)
    prev_item = None
    current_item = next(iterator)  # throws StopIteration if empty.
    for next_item in iterator:
        yield (prev_item, current_item, next_item)
        prev_item = current_item
        current_item = next_item
    yield (prev_item, current_item, None)


def getChart2(kw, brand, source, sku, fromDate, toDate):
    if (fromDate == "" or toDate == ""):
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
    b = list(data2)
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


def getChart3(kw, brand, source, sku, fromDate, toDate):
    dates = Review.objects.values_list('rDate')
    dates2 = Review.objects.values_list('rDate2')

    if (fromDate == "" or toDate == ""):
        data2 = Review.objects.filter \
            (pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source, pid__pModel__in=sku) \
            .values_list('pid__pBrand', 'pid__pModel') \
            .annotate(Count('pid__pModel'))
    else:
        data2 = Review.objects.filter \
            (pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source, pid__pModel__in=sku, rDate2__range=[fromDate, toDate]) \
            .values_list('pid__pBrand', 'pid__pModel') \
            .annotate(Count('pid__pModel'))


    print (brand)
    d2 = list(data2)
    series = []
    temp_list = []
    temp1 = []
    dict2 = {}
    temp_dict = {}
    temp_dict1 = {}
    for prev, item, next in neighborhood(d2):
        if next is not None:
            if item[0] == next[0]:
                temp_dict[item[1]] = item[2]
            else:
                temp_dict[item[1]] = item[2]
                temp_dict1[item[0]] = temp_dict
                temp_dict = {}
        else:
            if item[0] == prev[0]:
                temp_dict[item[1]] = item[2]
                temp_dict1[item[0]] = temp_dict
            else:
                temp_dict = {}
                temp_dict[item[1]] = item[2]
                temp_dict1[item[0]] = temp_dict


    #print(temp_dict1)
    #a = list(data)
    dict1 = {}
    # for i in d2:
    #     dict
    #print(a)
    #print(d2)
    #c = [[int(time.mktime(b[0].timetuple()))*1000, b[1]] for b in d2]
    #print("--------------------------------------------------------------")
    #print(dir(data))
    #print(c)
    print("--------------------------------------------------------------")
    #print("Query= ", data.query)
    data_json = json.dumps(temp_dict1, cls=DjangoJSONEncoder)
    #print(data_json)
    return data_json


def getPieChart(kw, brand, source, sku, fromDate, toDate):
    if fromDate=="" and toDate == "":
        data2 = Review.objects.filter(pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source,
                                      pid__pModel__in=sku) \
            .values_list('pid__siteCode') \
            .annotate(siteCode_count=Count('rid'))
    else:
        data2 = Review.objects.filter(pid__pCategory=kw, pid__pBrand__in=brand, pid__siteCode__in=source,
                                      pid__pModel__in=sku, rDate2__range=[fromDate, toDate]) \
            .values_list('pid__siteCode') \
            .annotate(siteCode_count=Count('rid'))
    print("Printing data2 for piechart")
    print(data2)
    dict_list = []
    one_dict = {}
    sources_file = pd.read_csv(dbConfig.dict['sourcesUrl'], header=0)

    for d in data2:
        one_dict['name'] = [r['siteName'] for i, r in sources_file.iterrows() if d[0] == r['siteCode']]
        print(one_dict['name'])
        one_dict['y'] = d[1]
        dict_list.append(one_dict.copy())
    print dict_list
    data_json = json.dumps(dict_list, cls=DjangoJSONEncoder)
    return data_json