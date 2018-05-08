import HomeDepot
# import Amazon_I1
import Amazon_LtdLoops as Amazon
import Walmart
import logging
from datetime import datetime
import time
import traceback
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import pandas as pd
from atlas.config import dbConfig
import django
django.setup()
from atlas.models import Product, Review, Analysis, Uploads, UploadAnalyses
import arrow


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


# FILE UPLOAD Main function:
def main2(kw_str, filecontents):
    global status_code
    if ".csv" in kw_str:
        kw_str = kw_str[:-4]
    print("product category :>", kw_str)

    print("type of contents_df:", type(filecontents))
    filecontents = pd.read_csv(StringIO(filecontents))
    print("contents_df: ", filecontents)

    # For logging
    #curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    #log_file_name = 'ATLASLog_' + curr_timestamp + '.log'
    #full_path = dbConfig.dict["logUrl"] + log_file_name
    # logging.basicConfig(filename=full_path, level=logging.INFO)  #This line of code stops application execution

    # End user UI
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "~~~~~~~~~~~~~~~~~~~~~~~ ATLAS ~~~~~~~~~~~~~~~~~~~~~~~"
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    time.sleep(0.5)

    #print "Scraping from all sites..."
    #logging.info("Scraping from all sites...")

    print("cleaning df")
    try:
        final_data_frame1 = clean_uploads_dataframe(filecontents)
    except:
        final_data_frame1 = filecontents
        print("error while cleaning integ_data_frame")
        print(traceback.print_exc())

    print("FINAL DF:-")
    print(final_data_frame1)  # .to_string(index=False))

    # # Saving the CSV file with product information and reviews; one CSV for each product/keyword
    # curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    # output_file_name = kw_str + '_ATLAS_' + curr_timestamp + '.csv'
    # full_path = dbConfig.dict["outputPath"] + output_file_name
    # final_data_frame1.to_csv(full_path, index=False, encoding='utf-8', date_format='%Y-%m-%d')
    # print "CSV file for this product saved at location: " + full_path
    # logging.info("CSV file for this product saved at location: " + full_path)
    #
    # with open(dbConfig.dict["outputUrl"], 'a') as f:
    #     final_data_frame1.to_csv(f, header=False, index=False, encoding='utf-8', date_format='%Y-%m-%d')
    #
    # f.close()

    print("Adding row to uploads and uploadanalyses tables")
    flag_u = False  # flags for each table to indicate if even one record was successfully inserted into database or not

    # flag_ua = False
    # df_col_names = list(final_data_frame1)
    # print(df_col_names)

    #default_date = datetime(2000, 01, 01, 00, 00, 00)
    #default_date.strftime('%Y/%m/%d')

    dt = datetime(2000, 1, 1)
    unix_dt = arrow.get(dt).timestamp

    #d.strftime('%Y-%m-%d')
    # unixtime = time.mktime(d.timetuple())

    for index, row in final_data_frame1.iterrows():
        # col is referred by index of column array
        db_cols = {'rid': " ", 'rDate': unix_dt, 'rDate2': dt, 'rRating': 0.0, 'rText': " ", 'rTitle': " ",
                        'rURL': " ", 'rUser': " "}
        fk_rid_obj = ""

        try:
            for dbc in db_cols.keys():
                if dbc in final_data_frame1.columns.values:
                    if dbc == 'rDate2':
                        db_cols['rDate2'] = row['rDate2']
                        print(db_cols['rDate2'])
                        db_cols['rDate'] = datetime.strptime(row['rDate2'], '%Y-%m-%d')
                        print(db_cols['rDate'])
                        # db_cols['rDate'] = datetime.fromtimestamp(arrow.get(db_cols['rDate2'])).timestamp
                        #db_cols['rDate'] = time.mktime(datetime.strptime(str(row['rDate2']),'%Y-%m-%d').strftime('%Y-%m-%d').timetuple())
                    else:
                        db_cols[dbc] = row[dbc]
                    print(db_cols[dbc])

            obj = Uploads.objects.create(rid=db_cols['rid'], rDate=db_cols['rDate'], rDate2=db_cols['rDate2'],
                                         rRating=db_cols['rRating'], rText=db_cols['rText'], rTitle=db_cols['rTitle'],
                                         rURL=db_cols['rURL'], rUser=db_cols['rUser'], pCategory=kw_str)
            fk_rid_obj = row['rid']
            print("rid:", fk_rid_obj)
            obj.save()
            print("Row added to uploads table")
            flag_u = 200

        except:
            print("Error while adding row to uploads table!")
            # print(row['rid'])
            print(traceback.print_exc())

        try:
            obj2 = UploadAnalyses.objects.create(rid_id=fk_rid_obj)
            obj2.save()
            print("Empty row added to uploadanalyses table. Will be populated later")
            flag_ua = True

        except:
            print("Error while adding row to uploadanalyses table!")
            #print(row['id'])
            print(traceback.print_exc())

    if flag_u == 200:
        status_code = 200
    else:
        print("No records added to uploads tables!")
        status_code = 500

    print ("Returning Status code from main file", status_code)
    return status_code

####################################################################################
