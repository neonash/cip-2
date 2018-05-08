import pandas as pd
import re
from time import time
import traceback
from atlas.config import dbConfig


def td_main(csv_file_path, kw_str):
    # input_content_file = "C:\Users\Aparna.harihara\PycharmProjects\AuScer\Outputs\ATLAS_Universal.csv"  # raw_data - 100.csv

    try:
        keywords_dict_file = dbConfig.dict['keywordsDict']
        #keywords_dict_file = r'D:\Aparna H\Sears\ATLAS\Codes\atlas-master 24042017\atlas-master\\mysite\\atlas\\database\\keywordsTD.csv'

        # output_file_loc = dbConfig.dict['tri_dri_Output']

        triggers = ['Upgrade', 'Replace', 'FirstTimeBuyer', 'Gift', 'Marketing-Sale']
        drivers = ['Brand', 'Cost', 'Recommendation', 'Innovation', 'Marketing-Ads']

        trig_perc = [0, 0, 0, 0, 0]
        driv_perc = [0, 0, 0, 0, 0]
        trig_dict = {}
        driv_dict = {}
        trig_dict_list = []
        driv_dict_list = []
        site_trig_dict = {}
        site_driv_dict = {}
        site_trig_dict_list = []
        site_driv_dict_list = []
        trig_site_wise_list = []
        driv_site_wise_list = []
        trig_driv_data_dict = {}
        final_dict = {}

        start_time = time()

        df = pd.read_csv(csv_file_path)  # change data source here
        df = df.dropna(subset=['rText'], how='all')
        # ip.columns=['Comments','Id','Date','Channel','Sentiment','Entity']
        df_by_kw = df.loc[df['pCategory'] == kw_str]
        unique_sites = df_by_kw.siteCode.unique()

        for u_s in unique_sites:

            print u_s
            ip_df = df_by_kw.loc[df_by_kw['siteCode'] == u_s]
            ip_df = ip_df.reset_index()

            kw = pd.read_csv(keywords_dict_file)

            Theme_vol = pd.DataFrame()
            temp_list = []

            for each_kw in range(len(kw)):
                # print each_kw
                op = pd.DataFrame()
                ip_df["Index1"] = 0

                for each in range(len(ip_df)):

                    if re.findall(kw.ix[each_kw, 'Keywords'], ip_df.ix[each, "rText"], re.I):
                        ip_df.ix[each, "Index1"] = 1

                    if (each + 1) % 100000 == 0:
                        print str(each + 1) + "th Comment"
                op = ip_df[ip_df['Index1'] == 1]
                #op.to_csv(output_file_loc + kw.ix[each_kw, 'ToD'] + ".csv", index=False)  # change data source
                print "No. of Documents for theme - ", kw.ix[each_kw, "ToD"], "=", len(op)
                Theme_vol = [kw.ix[each_kw, 'ToD'], len(op)]
                temp_list.append(Theme_vol)

                # print type(each_kw)
                if each_kw <= 4:
                    trig_perc[each_kw] = len(op)
                elif each_kw > 4:
                    driv_perc[each_kw-5] = len(op)
                else:
                    pass

            for i in range(0, 5):  # len(triggers) = len(drivers) in this case (len = 5)
                '''
                trig_dict["name"] = triggers[i]
                trig_dict["y"] = trig_perc[i]
                trig_dict_list.append(trig_dict.copy())

                driv_dict["name"] = drivers[i]
                driv_dict["y"] = driv_perc[i]
                driv_dict_list.append(driv_dict.copy())
                '''
                trig_dict[triggers[i]] = trig_perc[i]  # trig_data_dict
                driv_dict[drivers[i]] = driv_perc[i]  # driv_data_dict

            '''
            print "Trigger Dictionary: "
            print trig_dict_list
            print "Driver Dictionary: "
            print driv_dict_list
            '''

            if u_s == "AM":
                site_trig_dict["name"] = "Amazon"
                site_trig_dict["data"] = trig_dict
                site_trig_dict_list.append(site_trig_dict.copy())

                site_driv_dict["name"] = "Amazon"
                site_driv_dict["data"] = driv_dict
                site_driv_dict_list.append(site_driv_dict.copy())
            elif u_s == "HD":
                site_trig_dict["name"] = "HomeDepot"
                site_trig_dict["data"] = trig_dict
                site_trig_dict_list.append(site_trig_dict.copy())

                site_driv_dict["name"] = "HomeDepot"
                site_driv_dict["data"] = driv_dict
                site_driv_dict_list.append(site_driv_dict.copy())
            elif u_s == "WM":
                site_trig_dict["name"] = "Walmart"
                site_trig_dict["data"] = trig_dict
                site_trig_dict_list.append(site_trig_dict.copy())

                site_driv_dict["name"] = "Walmart"
                site_driv_dict["data"] = driv_dict
                site_driv_dict_list.append(site_driv_dict.copy())
            else:
                site_trig_dict["name"] = "Other"
                site_trig_dict["data"] = trig_dict
                site_trig_dict_list.append(site_trig_dict.copy())

                site_driv_dict["name"] = "Other"
                site_driv_dict["data"] = driv_dict
                site_driv_dict_list.append(site_driv_dict.copy())

        #site_senti_dict["data"] = senti_dict.copy()

        #trig_site_wise_list.append(site_trig_dict_list)
        #driv_site_wise_list.append(site_driv_dict_list)
        trig_driv_data_dict["triggerData"] = site_trig_dict_list
        trig_driv_data_dict["driverData"] = site_driv_dict_list
        #final_dict["trigdrivData"] = trig_driv_data_dict

        end_time = time()
        #temp_list_df = pd.DataFrame(temp_list)
        #temp_list_df.to_csv(output_file_loc + "VolumeNumbers.csv")  # change data source here
        print "Running Time : " + str(end_time - start_time) + " secs"

        status_code = 200

        return [trig_driv_data_dict, status_code]
    except:
        print traceback.print_exc()
        status_code = 500
        return [None, status_code]
