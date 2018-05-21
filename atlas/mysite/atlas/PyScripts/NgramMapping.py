import pandas as pd
from atlas.models import DimenMap, TaggedData
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import ATLAS1
import traceback


def main(request, sourcefile, dictfile):
    statuscode = 500
    if ".csv" in request:
        request = str(request).split(".")[0]

    # source_df= pd.read_csv(sourcefile, dtype={'ARTICLE_ID': str})

    #print(dictfile)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    # source_df = pd.read_csv(sourcefile)

    #source_df = sourcefile
    source_df = pd.read_csv(StringIO(sourcefile))
    #print(source_df)
    source_df['rid'] = source_df['rid'].apply(lambda x: '%.0f' % x)  # formats the column to float
    source_df['rid'] = source_df['rid'].astype('str')  # formats the column to str

    #dict_df = dictfile
    dict_df = pd.read_csv(dictfile)

    tagged_df_cols = ['rid']
    tagged_df_cols.extend(dict_df.columns)
    #print(tagged_df_cols)
    tagged_df = pd.DataFrame(columns=tagged_df_cols)

    # tagged_df['ARTICLE_ID'] = pd.to_numeric(tagged_df['ARTICLE_ID'], errors='coerce')
    # tagged_df['ARTICLE_ID'] = tagged_df['ARTICLE_ID'].astype('float64)

    try:
        for i1, r1 in source_df.iterrows():
            curr_conv = r1['rText']
            for i2, r2 in dict_df.iterrows():
                curr_entry = []
                try:
                    if str(r2['ngram']).center(len(r2['ngram']) + 2, ' ') in curr_conv:   # adds leading and trailing whitespaces to match as one phrase
                        #print(r1['ARTICLE_ID'])
                        curr_entry.append(str(r1['rid']))
                        curr_entry.extend(r2.tolist())  # condition, slicing
                        # print(curr_entry)
                        tagged_df.loc[len(tagged_df)] = curr_entry
                except TypeError:
                    pass

        # tagged_df['ARTICLE_ID'] = tagged_df['ARTICLE_ID'].astype(float)
        # df1 = df.apply(pd.to_numeric, args=('coerce',))

        #print(tagged_df)
        #tagged_df = tagged_df.drop([t for t in tagged_df_cols if '_' in t and not t == 'rid'], axis=1)
        #print(tagged_df)
        #tagged_df = tagged_df.drop_duplicates()
        # print(tagged_df)
        #tagged_df.to_csv("C:\\Users\\akshat.gupta\\Downloads\\tagged_data.csv")

        # Insert tagged data into database #############################################

        rs = list(DimenMap.objects.values())[0]
        # print(rs)
        # print(type(rs))
        headers_list = [t for t in tagged_df_cols if not t == 'rid' and not t == 'ngram']
        #print(headers_list)
        try:
            for idx, row in tagged_df.iterrows():
                dict2 = dict((el, " ") for el in rs.keys() if not el == 'dict_filename' and not el == 'id')
                #print(dict2)
                for h in headers_list:
                    try:
                        h1 = None
                        if "_" in h:
                            h1 = str(h).split("_")[1]  # as level name is split from dim_level format and stored
                        else:
                            h1 = h

                        # assigns the value of curr header of tag_dict_df row, >>> row[h]  >>> rhs
                        # to the key of dict2, such that  >>>  dict2[<...>] = ...  >>> lhs
                        # it is the same key as that in dict1,   >>> dict1.keys()[...]  >>> outermost box bracket of lhs
                        # which has the same value as the value of curr header of tag_dict_df row   >>> dict1.values().index(row[h])   >>> inner box bracket of lhs
                        dict2[rs.keys()[rs.values().index(h1)]] = row[h]

                    except:
                        print "Exception while adding tagged data to database"
                        print traceback.print_exc()
                obj1 = TaggedData(dataset_filename=request, rid=row['rid'], **dict2)
                obj1.save()
            print("Tagged output inserted into db")
        except:
            print("Couldn't insert into TaggedData")
            print(traceback.print_exc())

        statuscode = 200
    except:
        statuscode = 500

    return [tagged_df, statuscode]
