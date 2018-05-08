import csv
import pandas as pd
from atlas.config import dbConfig


def main(sourcefile, dictfile):
    statuscode = 500
    # source_df= pd.read_csv(sourcefile, dtype={'ARTICLE_ID': str})
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    # source_df = pd.read_csv(sourcefile)
    source_df = sourcefile
    source_df['ARTICLE_ID'] = source_df['ARTICLE_ID'].apply(lambda x: '%.0f' % x)
    source_df['ARTICLE_ID'] = source_df['ARTICLE_ID'].astype('str')
    # for i, r in source_df.iterrows():
    #     print(r['ARTICLE_ID'])
    #source_df['ARTICLE_ID'] = pd.to_numeric(source_df['ARTICLE_ID'], errors='coerce')
    # dict_df = pd.read_csv(dictfile)
    dict_df = dictfile
    tagged_df_cols = ['ARTICLE_ID']
    tagged_df_cols.extend(dict_df.columns)
    tagged_df = pd.DataFrame(columns=tagged_df_cols)
    # tagged_df['ARTICLE_ID'] = pd.to_numeric(tagged_df['ARTICLE_ID'], errors='coerce')
    # tagged_df['ARTICLE_ID'] = tagged_df['ARTICLE_ID'].astype('float64)

    try:
        for i1, r1 in source_df.iterrows():
            curr_conv = r1['CONTENT']
            #print("---")
            for i2, r2 in dict_df.iterrows():

                curr_entry = []
                try:
                    if str(r2['n_gram']).center(len(r2['n_gram']) + 2, ' ') in curr_conv:   # adds leading and trailing whitespaces to match as one phrase
                        #print(r1['ARTICLE_ID'])
                        curr_entry.append(str(r1['ARTICLE_ID']))
                        curr_entry.extend(r2.tolist())  # condition, slicing
                        # print(curr_entry)
                        tagged_df.loc[len(tagged_df)] = curr_entry
                except TypeError:
                    pass

        # tagged_df['ARTICLE_ID'] = tagged_df['ARTICLE_ID'].astype(float)
        # df1 = df.apply(pd.to_numeric, args=('coerce',))

        # print(tagged_df)
        tagged_df = tagged_df.drop([t for t in tagged_df_cols if '_' in t and not t == 'ARTICLE_ID'], axis=1)
        tagged_df = tagged_df.drop_duplicates()
        print("data tagged and saved")
        # print(tagged_df)
        tagged_df.to_csv("C:\\Users\\akshat.gupta\\Downloads\\tagged_data.csv")
        statuscode = 200
    except:
        statuscode = 500

    return [tagged_df, statuscode]
