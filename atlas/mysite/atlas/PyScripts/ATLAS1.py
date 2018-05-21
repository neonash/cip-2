import HomeDepot
# import Amazon_I1
import Amazon_LtdLoops as Amazon
import Walmart
import logging
from datetime import datetime
import time
import traceback
import sys
import numpy as np
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import pandas as pd
from atlas.config import dbConfig
import django
django.setup()
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses, DimenMap, TagDicts, Social


print("Imports complete")
# ############################################################################

# Global variables
integ_data_frame = []
status_code = 500


# ############################################################################


# To remove empty rows created while integrating dataframes
def clean_integ_dataframe(final_df):
    final_df1 = final_df[final_df.pURL != " "]
    final_df1 = final_df1[final_df1.pCategory != " "]
    #final_df1 = final_df1.replace([' '], ['#N/A'])
    repl_dict = {' ': "#N/A", '': '#N/A'}
    repl_dict1 = {r'\r': ' ', r'\n': ' ', r'\t': ' '}
    final_df1["pBrand"].replace(repl_dict, inplace=True)
    final_df1["rText"].replace(repl_dict, inplace=True)
    final_df1["rUser"].replace(repl_dict, inplace=True)
    final_df1["pModel"].replace(repl_dict1, inplace=True)
    final_df1 = final_df1.dropna(axis="columns", how='all')
    #for i, j in zip(*np.where(pd.isnull(final_df1))):
    # final_df1.iloc[i, j] = "#N/A"
    final_df1 = final_df1.drop_duplicates()
    final_df1 = final_df1[final_df1.rText != "#N/A"]

    return final_df1

# ############################################################################


# To remove empty rows created while integrating dataframes
def clean_uploads_dataframe(final_df):
    #final_df1 = final_df[final_df.rid != " "]
    final_df1 = final_df[final_df['rid'].notnull()]
    repl_dict = {' ': "#N/A", '': '#N/A', r'\r': ' ', r'\n': ' ', r'\t': ' '}
    final_df1["rText"].replace(repl_dict, inplace=True)
    final_df1 = final_df1.dropna(axis="columns", how='all')
    final_df1 = final_df1.drop_duplicates()
    final_df1 = final_df1[final_df1.rText != "#N/A"]

    return final_df1

# ############################################################################


# To remove empty rows created while integrating product dataframes
def clean_integ_prod_dataframe(final_df):
    final_df1 = final_df[final_df.pURL != " "]
    final_df1 = final_df1[final_df1.pModel != " "]
    final_df1 = final_df1[final_df1.pBrand != " "]
    final_df1 = final_df1[final_df1.pCategory != " "]
    #final_df1 = final_df1.replace([' '], ['#N/A'])
    repl_dict = {' ': "#N/A", '': '#N/A'}
    repl_dict1 = {r'\r': ' ', r'\n': ' ', r'\t': ' '}
    final_df1["pBrand"].replace(repl_dict, inplace=True)
    #final_df1["rText"].replace(repl_dict, inplace=True)
    #final_df1["rUser"].replace(repl_dict, inplace=True)
    final_df1["pModel"].replace(repl_dict1, inplace=True)
    final_df1 = final_df1.dropna(axis="columns", how='all')
    #for i, j in zip(*np.where(pd.isnull(final_df1))):
    # final_df1.iloc[i, j] = "#N/A"
    final_df1 = final_df1.drop_duplicates()
    #final_df1 = final_df1[final_df1.rText != "#N/A"]

    return final_df1

# ############################################################################


# To remove empty rows created while integrating review dataframes
def clean_integ_rev_dataframe(final_df):
    final_df1 = final_df
    #final_df1 = final_df[final_df.pURL != " "]
    #final_df1 = final_df1[final_df1.pCategory != " "]

    #final_df1 = final_df1.replace([' '], ['#N/A'])
    repl_dict = {' ': "#N/A", '': '#N/A'}
    #repl_dict1 = {r'\r': ' ', r'\n': ' ', r'\t': ' '}
    #final_df1["pBrand"].replace(repl_dict, inplace=True)
    final_df1["rText"].replace(repl_dict, inplace=True)
    final_df1["rUser"].replace(repl_dict, inplace=True)
    #final_df1["pModel"].replace(repl_dict1, inplace=True)
    final_df1 = final_df1.dropna(axis="columns", how='all')
    #for i, j in zip(*np.where(pd.isnull(final_df1))):
    #   final_df1.iloc[i, j] = "#N/A"
    final_df1 = final_df1.drop_duplicates()
    final_df1 = final_df1[final_df1.rText != "#N/A"]

    return final_df1

# ############################################################################


def gen_rid(row1):
    l1 = len(row1['rText'])
    w1 = len(row1['rText'].encode('utf-8').split(" "))
    tmp1 = row1['pid'] + "_" + row1['rUser'] + "_" + str(l1) + "_" + str(w1)
    return tmp1

# #############################################################


# Main function:
def main(kw_str, site):
    global integ_data_frame, status_code
    website = ["HD", "AM", "WM"]
    status = []  # For storing status codes
    # For logging
    curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    log_file_name = 'ATLASLog_' + curr_timestamp + '.log'
    full_path = dbConfig.dict["logUrl"] + log_file_name
    # logging.basicConfig(filename=full_path, level=logging.INFO)  #This line of code stops application execution

    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "~~~~~~~~~~~~~~~~~~~~~~~ ATLAS ~~~~~~~~~~~~~~~~~~~~~~~"
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    integ_data_frame = pd.DataFrame({'siteCode': [' '],
                                     'pid': [' '],
                                     'pCategory': [' '],
                                     'pBrand': [' '],
                                     'pTitle': [' '],
                                     'pRating': [' '],
                                     'pModel': [' '],
                                     'pDescr': [' '],
                                     'pImgSrc': [' '],
                                     'price': [' '],
                                     'pURL': [' '],
                                     'rUser': [' '],
                                     'rTitle': [' '],
                                     'rDate': [' '],
                                     'rRating': [' '],
                                     'rText': [' '],
                                     'rURL': [' '],
                                     'sentiScore': [' '],
                                     'sentiment': [' '],
                                     'trigger': [' '],
                                     'driver': [' ']}, index=[0])

    integ_prod_data_frame = pd.DataFrame({'siteCode': [' '],
                                          'pid': [' '],
                                          'pCategory': [' '],
                                          'pBrand': [' '],
                                          'pRating': [' '],
                                          'pTitle': [' '],
                                          'pModel': [' '],
                                          'price': [' '],
                                          'pURL': [' '],
                                          'pDescr': [' '],
                                          'pImgSrc': [' ']}, index=[0])

    integ_rev_data_frame = pd.DataFrame({'rUser': [' '],
                                         'rid': [' '],
                                         'pid': [' '],
                                         'rTitle': [' '],
                                         'rDate': [' '],
                                         'rRating': [' '],
                                         'rText': [' '],
                                         'rURL': [' ']}, index=[0])

    time.sleep(0.5)

    #print "Scraping from all sites..."
    #logging.info("Scraping from all sites...")

    for s in site:
        print(s)
        if s == "hd":
            try:
                print "Now scraping product information and reviews from HOMEDEPOT..."
                logging.info("Now scraping product information and reviews from HOMEDEPOT...")
                returned_list_HD = HomeDepot.home_depot_all_info(kw_str)

                integ_data_frame = integ_data_frame.append(returned_list_HD[0])
                integ_prod_data_frame = integ_prod_data_frame.append(returned_list_HD[1])
                integ_rev_data_frame = integ_rev_data_frame.append(returned_list_HD[2])
                status_code = returned_list_HD[3]
                status.append(returned_list_HD[3])

                print "Status Code for HomeDepot: " + str(returned_list_HD[3])
            except:
                print("error on returning integ dfs!")
                print(traceback.print_exc())
        if s == "am":
            try:
                print "Now scraping product information and reviews from AMAZON..."
                logging.info("Now scraping product information and reviews from AMAZON...")
                # returned_list_AM = Amazon_I1.amazon_i_all_info(kw_str)
                returned_list_AM = Amazon.amazon_all_info(kw_str)

                integ_data_frame = integ_data_frame.append(returned_list_AM[0])
                integ_prod_data_frame = integ_prod_data_frame.append(returned_list_AM[1])
                integ_rev_data_frame = integ_rev_data_frame.append(returned_list_AM[2])
                status.append(returned_list_AM[3])

                print "Status Code for Amazon: " + str(returned_list_AM[3])
            except:
                print("error on returning integ dfs!")
                print(traceback.print_exc())

        if s == "wm":
            try:
                print "Now scraping product information and reviews from WALMART..."
                logging.info("Now scraping product information and reviews from WALMART...")
                returned_list_WM = Walmart.walmart_all_info(kw_str)

                integ_data_frame = integ_data_frame.append(returned_list_WM[0])
                integ_prod_data_frame = integ_prod_data_frame.append(returned_list_WM[1])
                integ_rev_data_frame = integ_rev_data_frame.append(returned_list_WM[2])
                status.append(returned_list_WM[3])

                print "Status Code for Walmart: " + str(returned_list_WM[3])
            except:
                print("error on returning integ dfs!")
                print(traceback.print_exc())

        status_dict = dict(zip(website, status))

    # 'for s in site'ends here ^^
    '''
    if status_code == returned_list_AM[1]:
        status_code = returned_list_AM[1]
    else:
        status_code = 500
    '''
    print status_dict
    for value in status_dict.itervalues():
        # print("checking status of all sources")
        if value == 500:
            status_code = value
            break
        else:
            status_code = value

    print("cleaning df")
    try:
        final_data_frame1 = clean_integ_dataframe(integ_data_frame)
    except:
        print("error while cleaning integ_data_frame")
        print(traceback.print_exc())
    try:
        final_prod_data_frame1 = clean_integ_prod_dataframe(integ_prod_data_frame)
    except:
        print("error while cleaning integ_prod_df")
        print(traceback.print_exc())
    try:
        final_rev_data_frame1 = clean_integ_rev_dataframe(integ_rev_data_frame)
    except:
        print("error while cleaning integ rev df")
        print(traceback.print_exc())

    print("FINAL PROD DF:-")
    print(final_prod_data_frame1)

    # Saving the CSV file with product information and reviews; one CSV for each product/keyword
    curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    output_file_name = kw_str + '_ATLAS_' + curr_timestamp + '.csv'
    full_path = dbConfig.dict["outputPath"] + output_file_name
    final_data_frame1.to_csv(full_path, index=False, encoding='utf-8', date_format='%Y-%m-%d')
    print "CSV file for this product saved at location: " + full_path
    logging.info("CSV file for this product saved at location: " + full_path)

    # print(final_data_frame1)
    with open(dbConfig.dict["outputUrl"], 'a') as f:
        final_data_frame1.to_csv(f, header=False, index=False, encoding='utf-8', date_format='%Y-%m-%d')

    f.close()


    for index, row in final_prod_data_frame1.iterrows():
        # col is referred by index of column array
        print("adding row to prod table")
        try:
            obj = Product.objects.create(pid=row['pid'], pCategory=row['pCategory'], pBrand=row['pBrand'],
                                         pDescr=row['pDescr'], pImgSrc=row['pImgSrc'], pModel=row['pModel'],
                                         pTitle=row['pTitle'], pURL=row['pURL'], pPrice=row['price'],
                                         pRating=row['pRating'], siteCode=row['siteCode'])
            print(row['pid'])
            obj.save()

        except:
            print("Error while adding row to prod table!")
            #print(row['pid'])
            print(traceback.print_exc())

    for index, row in final_rev_data_frame1.iterrows():
        # col is referred by index of column array
        print("adding row to rev/analysis tables")
        try:
            print("Adding rev record")
            fk_pid_obj = Product.objects.get(pid=row['pid'])
            rid = row['rid']
            print(rid)
            obj1 = Review.objects.create(rid=rid, pid=fk_pid_obj, rDate=row['rDate'], rDate2=row['rDate'], rRating=row['rRating'],
                                         rText=(row['rText']), rTitle=(row['rTitle']), rURL=row['rURL'],
                                         rUser=row['rUser'])
            print(row['rTitle'])
            obj1.save()

            print("Adding analysis record")
            obj2 = Analysis.objects.create(rid_id=rid)
            obj2.save()

        except:
            print("Error while adding row to rev table!")
            # print(row['rTitle'])
            print(traceback.print_exc())


    print ("Returning Status code from main file", status_code)
    return status_code

####################################################################################


def read_dims(headers_list):
    table_data_df = pd.DataFrame({'dimension': [' '],
                                  'level1': [' '],
                                  'level2': [' '],
                                  'level3': [' '],
                                  'level4': [' '],
                                  'level5': [' ']}, index=None)
    i = 0
    j = i + 1
    list_entry = [headers_list[i]]
    while j < len(headers_list):
        if "_" in headers_list[j]:
            lvl = str(headers_list[j]).split("_")[1]
            list_entry.append(lvl)
            if j == len(headers_list) - 1:  # if last item is a level, save list entry
                while len(list_entry) < 6:
                    list_entry.append(" ")
                #print(list_entry)
                if i == 0:
                    table_data_df.loc[0] = list_entry
                else:
                    table_data_df.loc[len(table_data_df)] = list_entry
            j += 1
        else:
            # store previous entry
            while len(list_entry) < 6:
                list_entry.append(" ")
            #print(list_entry)
            if i == 0:
                table_data_df.loc[0] = list_entry
            else:
                table_data_df.loc[len(table_data_df)] = list_entry

            # create new entry
            dim = headers_list[j]
            i = j
            list_entry = [dim]
            j = i + 1
            if j == len(headers_list):  # if last item is a dimension, save list entry
                while len(list_entry) < 6:
                    list_entry.append(" ")
                #print(list_entry)
                if i == 0:
                    table_data_df.loc[0] = list_entry
                else:
                    table_data_df.loc[len(table_data_df)] = list_entry

    # table_data_df.to_csv("C:\\Users\\akshat.gupta\\Desktop\\table_data_df.csv")
    # table_data_df['dimension'].replace(' ', np.nan, inplace=True)
    # table_data_df = table_data_df.dropna(axis="index", how='any')

    while not len(table_data_df) == 15:
        table_data_df.loc[len(table_data_df)] = [" ", " ", " ", " ", " ", " "]

    #print(table_data_df)

    return table_data_df

# ##################################################################################


def gen_dims():
    dims = []
    for i in range(1, 16):  # 1 thru 15
        dims.append("dim" + str(i))
    return dims

# ################################################################################


def gen_levels():
    dims = gen_dims()
    levels = []
    for i in range(1, len(dims) + 1):  # dims 1 thru 15
        for j in range(1, 6):  # levels 1 thru 5 per dim
            levels.append("d" + str(i) + "_l" + str(j))
    return [dims, levels]

# ################################################################################


def gen_all_cols():
    [dims, levels] = gen_levels()
    all_cols = []

    for i in range(0, len(dims)):  # dims 1 thru 15
        all_cols.append(dims[i])
        curr_levels = levels[0:5]
        all_cols.extend(curr_levels)
        del levels[0:5]

    return all_cols

# ###############################################################################


# FILE UPLOAD Main function:
def main2(kw_str, filecontents, tag_dict):
    global status_code
    if ".csv" in kw_str:
        kw_str = kw_str[:-4]
    print("product category :>", kw_str)

    flag_u = 500

    filecontents = pd.read_csv(StringIO(filecontents))

    # For logging
    #curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    #log_file_name = 'ATLASLog_' + curr_timestamp + '.log'
    #full_path = dbConfig.dict["logUrl"] + log_file_name
    # logging.basicConfig(filename=full_path, level=logging.INFO)  #This line of code stops application execution

    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "~~~~~~~~~~~~~~~~~~~~~~~ ATLAS ~~~~~~~~~~~~~~~~~~~~~~~"
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    time.sleep(0.5)

    # Inserting tag_dict dimension map into database ######################

    print("Adding tag_dict dimension mapping to db")
    # print(dbConfig.dict['tagDict'])
    # tag_dict_df = pd.read_csv(dbConfig.dict['tagDict'])  # FOR DEBUGGING
    tag_dict_df = pd.read_csv(tag_dict)  # FOR PRODUCTION

    table_data_df = None
    headers_list1 = tag_dict_df.columns.values.tolist()
    headers_list = headers_list1[1:]  # to avoid first column

    try:
        # to extract dimensions and levels from uploaded dict >>>
        table_data_df = read_dims(headers_list)
    except:
        print "Exception caught while extracting dimensions"
        print traceback.print_exc()

    all_cols = gen_all_cols()
    all_col_vals = []

    dict1 = {}
    try:
        for idx, row in table_data_df.iterrows():
            try:
                all_col_vals.append(row["dimension"])
                all_col_vals.append(row["level1"])
                all_col_vals.append(row["level2"])
                all_col_vals.append(row["level3"])
                all_col_vals.append(row["level4"])
                all_col_vals.append(row["level5"])
            except:
                print "Exception while adding dimension mapping to database"
                print traceback.print_exc()

        dict1 = dict(zip(all_cols, all_col_vals))
        # print dict1
        obj1 = DimenMap(dict_filename=kw_str, **dict1)
        obj1.save()
    except:
        print("Couldn't insert into DimenMap")
        print(traceback.print_exc())

    # Inserting tag_dict into db ##############################################

    print("Inserting tag_dict into db")
    #print(dict1)
    headers_list2 = tag_dict_df.columns.values.tolist()
    headers_list2 = headers_list2[1:]  # to ignore 'ngram' column
    dict2 = dict((el, " ") for el in all_cols)
    try:
        for idx, row in tag_dict_df.iterrows():
            try:
                for h in headers_list2:
                    h1 = None
                    if "_" in h:
                        h1 = str(h).split("_")[1]  # as level name is split from dim_level format and stored
                    else:
                        h1 = h
                    #print(h1)
                    #print(dict1.values().index(h1))
                    #print(dict1.keys()[dict1.values().index(h1)])
                    #print(dict2[dict1.keys()[dict1.values().index(h1)]])

                    # assigns the value of curr header of tag_dict_df row, >>> row[h]  >>> rhs
                    # to the key of dict2, such that  >>>  dict2[<...>] = ...  >>> lhs
                    # it is the same key as that in dict1,   >>> dict1.keys()[...]  >>> outermost box bracket of lhs
                    # which has the same value as the value of curr header of tag_dict_df row   >>> dict1.values().index(row[h])   >>> inner box bracket of lhs
                    dict2[dict1.keys()[dict1.values().index(h1)]] = row[h]

                    #print(dict2[dict1.keys()[dict1.values().index(h1)]])

                obj2 = TagDicts(dict_filename=kw_str, ngram=row['ngram'], **dict2)
                obj2.save()
            except:
                print "Exception while adding tag dict to database"
                print traceback.print_exc()

    except:
        print("Couldn't insert into TagDicts")
        print(traceback.print_exc())

    # Inserting uploaded dataset into database ####################################

    print("Inserting uploaded dataset into database ")
    try:
        headers_list3 = [str(h).split(".")[2] for h in Social._meta.get_fields()]
        # print(headers_list3)
        headers_list3 = headers_list3[2:]  # to remove 'id' and 'dataset_filename' cols from loop
        dict3 = dict((el, None) for el in headers_list3)
        dt = '2000-01-01'
        unix_dt = datetime.strptime('2000-01-01', "%Y-%m-%d")
        dict3['rDate2'] = dt
        dict3['rDate'] = unix_dt
        for i, r in filecontents.iterrows():
            for h in headers_list3:
                try:
                    if h in filecontents.columns.values.tolist():
                        #print(h)
                        #print(r[h])
                        dict3[h] = r[h]
                        if h == 'rDate2' or h == 'rDate':
                            dict3['rDate2'] = r[h]
                            dict3['rDate'] = datetime.strptime(r[h], "%Y-%m-%d")
                except:
                    pass
            obj3 = Social(dataset_filename=kw_str, **dict3)
            obj3.save()
            flag_u = 200
    except:
        print("Couldn't insert source dataset into db")
        print(traceback.print_exc())

    #####################################################
    # COMMENTED OUT - BELOW CODE IS FOR REVIEW DATA

    # print("cleaning df")
    # try:
    #     final_data_frame1 = clean_uploads_dataframe(filecontents)
    # except:
    #     final_data_frame1 = filecontents
    #     print("error while cleaning integ_data_frame")
    #     #print(traceback.print_exc())
    #
    # print("FINAL DF:-")
    # print(final_data_frame1)  # .to_string(index=False))
    #
    # # # Saving the CSV file with product information and reviews; one CSV for each product/keyword
    # # curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    # # output_file_name = kw_str + '_ATLAS_' + curr_timestamp + '.csv'
    # # full_path = dbConfig.dict["outputPath"] + output_file_name
    # # final_data_frame1.to_csv(full_path, index=False, encoding='utf-8', date_format='%Y-%m-%d')
    # # print "CSV file for this product saved at location: " + full_path
    # # logging.info("CSV file for this product saved at location: " + full_path)
    # #
    # # with open(dbConfig.dict["outputUrl"], 'a') as f:
    # #     final_data_frame1.to_csv(f, header=False, index=False, encoding='utf-8', date_format='%Y-%m-%d')
    # #
    # # f.close()
    #
    # print("Adding row to uploads and uploadanalyses tables")
    # flag_u = False  # flags for each table to indicate if even one record was successfully inserted into database or not
    #
    # # flag_ua = False
    # # df_col_names = list(final_data_frame1)
    # # print(df_col_names)
    #
    # #default_date = datetime(2000, 01, 01, 00, 00, 00)
    # #default_date.strftime('%Y/%m/%d')
    #
    # dt = datetime(2000, 1, 1)
    # unix_dt = arrow.get(dt).timestamp
    #
    # #d.strftime('%Y-%m-%d')
    # # unixtime = time.mktime(d.timetuple())
    #
    # for index, row in final_data_frame1.iterrows():
    #     # col is referred by index of column array
    #     db_cols = {'rid': " ", 'rDate': unix_dt, 'rDate2': dt, 'rRating': 0.0, 'rText': " ", 'rTitle': " ",
    #                     'rURL': " ", 'rUser': " "}
    #     fk_rid_obj = ""
    #
    #     try:
    #         for dbc in db_cols.keys():
    #             if dbc in final_data_frame1.columns.values:
    #                 if dbc == 'rDate2':
    #                     db_cols['rDate2'] = datetime.strptime(row['rDate2'], '%Y-%m-%d')
    #                     print(db_cols['rDate2'])
    #                     db_cols['rDate'] = int(db_cols['rDate2'].timestamp())
    #                     print(db_cols['rDate'])
    #                     # db_cols['rDate'] = datetime.fromtimestamp(arrow.get(db_cols['rDate2'])).timestamp
    #                     #db_cols['rDate'] = time.mktime(datetime.strptime(str(row['rDate2']),'%Y-%m-%d').strftime('%Y-%m-%d').timetuple())
    #                 else:
    #                     db_cols[dbc] = row[dbc]
    #                 print(db_cols[dbc])
    #
    #         obj = Uploads.objects.create(rid=db_cols['rid'], rDate=db_cols['rDate'], rDate2=db_cols['rDate2'],
    #                                      rRating=db_cols['rRating'], rText=db_cols['rText'], rTitle=db_cols['rTitle'],
    #                                      rURL=db_cols['rURL'], rUser=db_cols['rUser'], pCategory=kw_str)
    #         fk_rid_obj = row['rid']
    #         print("rid:", fk_rid_obj)
    #         obj.save()
    #         print("Row added to uploads table")
    #         flag_u = 200
    #
    #     except:
    #         print("Error while adding row to uploads table!")
    #         # print(row['rid'])
    #         #print(traceback.print_exc())
    #
    #     try:
    #         obj2 = UploadAnalyses.objects.create(rid_id=fk_rid_obj)
    #         obj2.save()
    #         print("Empty row added to uploadanalyses table. Will be populated later")
    #         flag_ua = True
    #
    #     except:
    #         print("Error while adding row to uploadanalyses table!")
    #         #print(row['id'])
    #         #print(traceback.print_exc())
    # ###############################################################################
    if flag_u == 200:
        status_code = 200
    else:
        print("No records added to uploads tables!")
        status_code = 500

    print ("Returning Status code from main file", status_code)
    return status_code

####################################################################################
