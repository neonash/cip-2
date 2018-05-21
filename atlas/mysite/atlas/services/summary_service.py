import json
import pandas as pd
from django.core.serializers.json import DjangoJSONEncoder
import django
django.setup()
from atlas.PyScripts import ATLAS1
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses, DimenMap, TagDicts, TaggedData
from django.db.models import Count,Avg
from django.utils.dateformat import format
import time, datetime
from atlas.config import dbConfig
from django.core import serializers
import mpld3
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import svd


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


class CA(object):
    """Simple correspondence analysis.

    Inputs
     ------
    ct : array_like

      Two-way contingency table. If `ct` is a pandas DataFrame object,
      the index and column values are used for plotting.

    Notes
    -----
    The implementation follows that presented in 'Correspondence
    Analysis in R, with Two- and Three-dimensional Graphics: The ca
    Package,' Journal of Statistical Software, May 2007, Volume 20,
    Issue 3.

    """

    def __init__(self, ct):
        self.rows = ct.index.values if hasattr(ct, 'index') else None
        self.cols = ct.columns.values if hasattr(ct, 'columns') else None

        # contingency table
        N = np.matrix(ct, dtype=float)

        # correspondence matrix from contingency table
        P = N / N.sum()

        # row and column marginal totals of P as vectors
        r = P.sum(axis=1)
        c = P.sum(axis=0).T

        # diagonal matrices of row/column sums
        D_r_rsq = np.diag(1. / np.sqrt(r.A1))
        D_c_rsq = np.diag(1. / np.sqrt(c.A1))

        # the matrix of standarized residuals
        S = D_r_rsq * (P - r * c.T) * D_c_rsq

        # compute the SVD
        U, D_a, V = svd(S, full_matrices=False)
        D_a = np.asmatrix(np.diag(D_a))
        V = V.T

        # principal coordinates of rows
        F = D_r_rsq * U * D_a

        # principal coordinates of columns
        G = D_c_rsq * V * D_a

        # standard coordinates of rows
        X = D_r_rsq * U

        # standard coordinates of columns
        Y = D_c_rsq * V

        # the total variance of the data matrix
        inertia = sum([(P[i, j] - r[i, 0] * c[j, 0]) ** 2 / (r[i, 0] * c[j, 0])
                       for i in range(N.shape[0])
                       for j in range(N.shape[1])])

        self.F = F.A
        self.G = G.A
        self.X = X.A
        self.Y = Y.A
        self.inertia = inertia
        self.eigenvals = np.diag(D_a) ** 2

    def plot(self):
        """Plot the first and second dimensions."""
        xmin, xmax = None, None
        ymin, ymax = None, None
        if self.rows is not None:
            for i, t in enumerate(self.rows):
                x, y = self.F[i, 0], self.F[i, 1]
                plt.text(x, y, t, va='center', ha='center', color='r')
                xmin = min(x, xmin if xmin else x)
                xmax = max(x, xmax if xmax else x)
                ymin = min(y, ymin if ymin else y)
                ymax = max(y, ymax if ymax else y)
        else:
            plt.plot(self.F[:, 0], self.F[:, 1], 'ro')

        if self.cols is not None:
            for i, t in enumerate(self.cols):
                x, y = self.G[i, 0], self.G[i, 1]
                plt.text(x, y, t, va='center', ha='center', color='b')
                xmin = min(x, xmin if xmin else x)
                xmax = max(x, xmax if xmax else x)
                ymin = min(y, ymin if ymin else y)
                ymax = max(y, ymax if ymax else y)
        else:
            plt.plot(self.G[:, 0], self.G[:, 1], 'bs')

        if xmin and xmax:
            pad = (xmax - xmin) * 0.1
            plt.xlim(xmin - pad, xmax + pad)
        if ymin and ymax:
            pad = (ymax - ymin) * 0.1
            plt.ylim(ymin - pad, ymax + pad)

        plt.grid()
        plt.xlabel('Dim 1')
        plt.ylabel('Dim 2')

    def scree_diagram(self, perc=True, *args, **kwargs):
        """Plot the scree diagram."""
        eigenvals = self.eigenvals
        xs = np.arange(1, eigenvals.size + 1, 1)
        ys = 100. * eigenvals / eigenvals.sum() if perc else eigenvals
        plt.plot(xs, ys, *args, **kwargs)
        plt.xlabel('Dimension')
        plt.ylabel('Eigenvalue' + (' [%]' if perc else ''))


def getPivotcontent(kw):
    #all_cols = ATLAS1.gen_all_cols()
    all_cols = ['dim1', 'dim2','dim3', 'dim4', 'dim5', 'dim6', 'dim7','dim8', 'dim9', 'dim10', 'dim11', 'dim12','dim13',
                'dim14', 'dim15', 'd1_l1', 'd1_l2','d1_l3','d1_l4','d1_l5','d2_l1', 'd2_l2', 'd2_l3', 'd2_l4', 'd2_l5', 'd3_l1',
                'd3_l2', 'd3_l3', 'd3_l4', 'd3_l5', 'd4_l1', 'd4_l2','d4_l3', 'd4_l4', 'd4_l5', 'd6_l1', 'd6_l2', 'd6_l3',
                'd6_l4', 'd6_l5', 'd7_l1', 'd7_l2', 'd7_l3', 'd7_l4','d7_l5', 'd8_l1', 'd8_l2', 'd8_l3', 'd8_l4', 'd8_l5',
                'd9_l1', 'd9_l2', 'd9_l3', 'd9_l4', 'd9_l5', 'd10_l1','d10_l2', 'd10_l3', 'd10_l4', 'd10_l5', 'd11_l1',
                'd11_l2', 'd11_l3', 'd11_l4', 'd11_l5','d12_l1','d12_l2', 'd12_l3', 'd12_l4', 'd12_l5', 'd13_l1',
                'd13_l2', 'd13_l3', 'd13_l4', 'd13_l5', 'd14_l1','d14_l2', 'd14_l3', 'd14_l4', 'd14_l5', 'd15_l1',
                'd15_l2', 'd15_l3', 'd15_l4', 'd15_l5']
    data = TaggedData.objects.filter(dataset_filename=kw).values('dim1', 'dim2','dim3', 'dim4', 'dim5', 'dim6', 'dim7',
                                                                 'dim8', 'dim9', 'dim10', 'dim11', 'dim12','dim13',
                                                                 'dim14', 'dim15', 'd1_l1', 'd1_l2','d1_l3','d1_l4','d1_l5',
                                                                 'd2_l1', 'd2_l2', 'd2_l3', 'd2_l4', 'd2_l5', 'd3_l1',
                                                                 'd3_l2', 'd3_l3', 'd3_l4', 'd3_l5', 'd4_l1', 'd4_l2',
                                                                 'd4_l3', 'd4_l4', 'd4_l5', 'd6_l1', 'd6_l2', 'd6_l3',
                                                                 'd6_l4', 'd6_l5', 'd7_l1', 'd7_l2', 'd7_l3', 'd7_l4',
                                                                 'd7_l5', 'd8_l1', 'd8_l2', 'd8_l3', 'd8_l4', 'd8_l5',
                                                                 'd9_l1', 'd9_l2', 'd9_l3', 'd9_l4', 'd9_l5', 'd10_l1',
                                                                 'd10_l2', 'd10_l3', 'd10_l4', 'd10_l5', 'd11_l1',
                                                                 'd11_l2', 'd11_l3', 'd11_l4', 'd11_l5','d12_l1',
                                                                 'd12_l2', 'd12_l3', 'd12_l4', 'd12_l5', 'd13_l1',
                                                                 'd13_l2', 'd13_l3', 'd13_l4', 'd13_l5', 'd14_l1',
                                                                 'd14_l2', 'd14_l3', 'd14_l4', 'd14_l5', 'd15_l1',
                                                                 'd15_l2', 'd15_l3', 'd15_l4', 'd15_l5')

    data1 = DimenMap.objects.filter(dict_filename=kw).values()
    print(data1)
    data = list(data)
    data1 = list(data1)[0]
    print(data1)
    for d in data:
        for i in all_cols:
            d[data1[i]] = d.pop(i)
    #print("-------------------------------------------------------------------------------")
    print(data)
    data_json = json.dumps(list(data), cls=DjangoJSONEncoder)
    #print("-------------------------------------------------------------------------------")
    #print("Data_json is : neo -- ", data_json)
    return data_json


def getAssocDims(kw):
    print("inside getassocdims")
    data1 = DimenMap.objects.values().get(dict_filename=kw)
    dims = []

    for k, v in data1.iteritems():
        if not k == "id" and not k == "dict_filename" and not "_" in k and len(v) > 1 and not v in ["Brand", "brand"]:
            print(v)
            dims.append(v)
    print(dims)

    print(type(dims))
    data_json = json.dumps(dims, cls=DjangoJSONEncoder)
    return data_json


def getAssocLevels(kw, dim):
    print("inside getassoclevels")
    data1 = DimenMap.objects.values().get(dict_filename=kw)
    dim_col = ""
    level_cols = []
    levels = []

    for k, v in data1.iteritems():
        if v == dim:
            dim_col = k

    x = dim_col[dim_col.index("m") + 1:]  # extract dim number
    for i in range(1, 6):
        level_cols.append("d" + x + "_l" + str(i))
    # print(level_cols)

    levels_dict = dict((l, "") for l in level_cols)
    for k, v in data1.iteritems():
        for l in level_cols:
            if k == l:
                levels_dict[l] = v
    print(levels_dict)

    print(type(levels))
    data_json = json.dumps(levels, cls=DjangoJSONEncoder)
    return data_json


def get_assoc_data(kw, dim):
    print(kw)
    if ".csv" in kw:
        kw = str(kw).split(".")[0]
    # Get list of brands and levels of selected dim
    data1 = DimenMap.objects.values().get(dict_filename=kw)
    brand_col = ""
    dim_col = ""
    level_cols = []
    levels = []

    for k, v in data1.iteritems():
        if v == "brand":
            brand_col = k
        if v == dim:
            dim_col = k

    x = dim_col[dim_col.index("m") + 1:]   # extract dim number
    for i in range(1, 6):
        level_cols.append("d" + x + "_l" + str(i))
    #print(level_cols)

    levels_dict = dict((l, "") for l in level_cols)
    for k, v in data1.iteritems():
        for l in level_cols:
            if k == l:
                levels_dict[l] = v
    print(levels_dict)

    brands = []
    brands = TaggedData.objects.filter(dataset_filename=kw).values_list(brand_col, flat=True)
    brands = list(set(brands))
    brands = [x for x in brands if str(x) != 'nan']
    print(brands)

    has_levels = [x for x in levels_dict.values() if not x == ""]

    # Form dataframe to hold values
    if len(has_levels) > 0:
        data_df = pd.DataFrame({'brand': brands})
        #print(data_df)
        for l in levels_dict.values():
            data_df[l] = 0
        # print('-'.join(levels))
        # pd.concat([data_df, pd.DataFrame(columns='-'.join(levels))])
        print(data_df)

        # Fill in values
        data2 = TaggedData.objects.filter(dataset_filename=kw).values()
        rids = []
        rids = TaggedData.objects.filter(dataset_filename=kw).values_list('rid', flat=True)
        rids = list(set(rids))
        print(rids)

        # for r in rids:
        #     bl_check = [False, False]
        #     for d in range(len(data2)):
        #         for b in brands:
        #             for l in levels_dict:
        #                 if r in data2[d].values() and (b in data2[d].values() or levels_dict[levels_dict.keys()[0]] in data2[d].values()):
        #                     if b in data2[d].values():
        #                         bl_check[1] = True
        #                     elif levels[l] in data2[d].values():
        #                         bl_check[0] = True
        #                 if False not in bl_check:
        #                     data_df[data_df.index[data_df['brand'] == b], data_df.columns.get_loc(levels_dict[l])] += 1
    else:
        data_df = []

    print(data_df)

    return data_df


def getAssociationdata(kw, dim):
    data_df = get_assoc_data(kw, dim)
    df = pd.io.parsers.read_csv(dbConfig.dict['associationInput'])
    df = df.set_index('brand')
    df1 = df
    df1 = df1.to_json(orient='index')
    # print df.describe()
    # print df.head()
    # print("-----------------------------------", df1)
    ca = CA(df)

    fig = plt.figure('Brand Perception Chart')
    ca.plot()
    #    plt.figure(101)
    # ca.scree_diagram()

    # plt.show()
    b = mpld3.fig_to_dict(fig)

    dict_combine = {"source_data": df1, "graph_data": b}
    # data1 = serializers.serialize("json", dict_combine)

    data_json = json.dumps(dict_combine, cls=DjangoJSONEncoder)
    #print("-------------------------------------------------------------------------------")
    #print("Data_json is : neo -- ", data_json)
    #print(type(data_json))
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