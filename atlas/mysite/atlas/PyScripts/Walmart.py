from selenium import webdriver
import pandas as pd
import time
import re
import traceback
from datetime import datetime
import logging
import json
from functools import reduce  # forward compatibility for Python 3
import operator
from atlas.config import dbConfig


# Global variables
browser = None
browser1 = None
chrome_path = dbConfig.dict["chromeDriver"]
status_code = 500
kw_str = ""

# ######################################################################

# Override function to access dictionary
def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)

# ######################################################################


def gen_api_request(p_id, page):
    global browser1
    prefix = "https://www.walmart.com/terra-firma/item/"
    suffix = "/reviews?sort=relevancy&filters=&limit=100&page="
    browser1.get(prefix + p_id + suffix + str(page))
    resp = json.loads(browser1.find_element_by_xpath("//body//pre").get_attribute("innerHTML"))
    # print(type(resp))
    return resp

# ######################################################################


def parse_resp(resp, p_id, p_url, kw_str1):
    # print(type(resp))
    one_review = pd.DataFrame({'siteCode': ['WM'],
                               'pCategory': [kw_str1],
                               'rUser': [' '],
                               'rTitle': [' '],
                               'rDate': [' '],
                               'rText': [' '],
                               'rRating': [' '],
                               'rURL': [p_url],
                               'pURL': [p_url],
                               'sentiScore': [' '],
                               'sentiment': [' '],
                               'trigger': [' '],
                               'driver': [' ']}, index=[0])

    this_page_reviews = pd.DataFrame({'siteCode': ['WM'],
                                      'pCategory': [kw_str1],
                                      'rUser': [' '],
                                      'rTitle': [' '],
                                      'rDate': [' '],
                                      'rText': [' '],
                                      'rRating': [' '],
                                      'rURL': [p_url],
                                      'pURL': [p_url],
                                      'sentiScore': [' '],
                                      'sentiment': [' '],
                                      'trigger': [' '],
                                      'driver': [' ']}, index=[0])
    prod_rev_count = getFromDict(getFromDict(getFromDict(resp, ["payload"]), ["pagination"]), ["total"])
    print("rev: ", str(prod_rev_count))
    list1 = getFromDict(getFromDict(resp, ["payload"]), ["customerReviews"])
    print("no of revs in this page: ", str(len(list1)))

    for i in list1:
        one_review = pd.DataFrame({'siteCode': ['WM'],
                                   'pCategory': [kw_str1],
                                   'rDate': [getFromDict(i, ["reviewSubmissionTime"])],
                                   'rUser': [getFromDict(i, ["userNickname"])],
                                   'rTitle': [getFromDict(i, ["reviewTitle"])],
                                   'rText': [getFromDict(i, ["reviewText"])],
                                   'rRating': [getFromDict(i, ["rating"])],
                                   'rURL': [p_url],
                                   'pURL': [p_url],
                                   'sentiScore': [' '],
                                   'sentiment': [' '],
                                   'trigger': [' '],
                                   'driver': [' ']}, index=[0])

        this_page_reviews = this_page_reviews.append(one_review)
    return this_page_reviews

# ######################################################################


# To make API requests, parse its responses and extract reviews (all reviews of the product are returned)
def get_reviews(p_id, p_url, kw_str1):
    global browser1, status_code
    curr_pg = 1
    prefix = "https://www.walmart.com/terra-firma/item/"
    suffix = "/reviews?sort=relevancy&filters=&limit=100&page="
    browser1.get(prefix + p_id + suffix + str(curr_pg))
    resp = json.loads(browser1.find_element_by_xpath("//body//pre").get_attribute("innerHTML"))
    # print(type(resp))

    # To hold one review's data
    one_review = pd.DataFrame({'siteCode': ['WM'],
                               'pCategory': [kw_str1],
                               'rUser': [' '],
                               'rTitle': [' '],
                               'rDate': [' '],
                               'rText': [' '],
                               'rRating': [' '],
                               'rURL': [p_url],
                               'pURL': [p_url],
                               'sentiScore': [' '],
                               'sentiment': [' '],
                               'trigger': [' '],
                               'driver': [' ']}, index = [0])

    # To hold all reviews on one page of responses
    this_page_reviews = pd.DataFrame({'siteCode': ['WM'],
                                      'pCategory': [kw_str1],
                                      'rUser': [' '],
                                      'rTitle': [' '],
                                      'rDate': [' '],
                                      'rText': [' '],
                                      'rRating': [' '],
                                      'rURL': [p_url],
                                      'pURL': [p_url],
                                      'sentiScore': [' '],
                                      'sentiment': [' '],
                                      'trigger': [' '],
                                      'driver': [' ']}, index = [0])

    # To hold all reviews across all pages of responses
    all_reviews = pd.DataFrame({'siteCode': ['WM'],
                                'pCategory': [kw_str1],
                                'rUser': [' '],
                                'rTitle': [' '],
                                'rDate': [' '],
                                'rText': [' '],
                                'rRating': [' '],
                                'rURL': [p_url],
                                'pURL': [p_url],
                                'sentiScore': [' '],
                                'sentiment': [' '],
                                'trigger': [' '],
                                'driver': [' ']}, index = [0])

    try:
        # Count of total reviews available in the responses
        prod_rev_count = int(getFromDict(getFromDict(getFromDict(resp, ["payload"]), ["pagination"]), ["total"]))
        print("rev: ", str(prod_rev_count))
        prod_rev_count1 = prod_rev_count

        if prod_rev_count > 0:
            # While more reviews remaining to be extracted
            while prod_rev_count1 > 0:
                rev_list = getFromDict(getFromDict(resp, ["payload"]), ["customerReviews"])
                print("no of revs in this page: ", str(len(rev_list)))
                for i in rev_list:
                    # Loop through each review in the current page

                    # Collate values of one review in data frame
                    one_review = pd.DataFrame({'siteCode': ['WM'],
                                               'pCategory': [kw_str1],
                                               'rDate': [getFromDict(i, ["reviewSubmissionTime"])],
                                               'rUser': [getFromDict(i, ["userNickname"])],
                                               'rTitle': [getFromDict(i, ["reviewTitle"])],
                                               'rText': [getFromDict(i, ["reviewText"])],
                                               'rRating': [getFromDict(i, ["rating"])],
                                               'rURL': [p_url],
                                               'pURL': [p_url],
                                               'sentiScore': [' '],
                                               'sentiment': [' '],
                                               'trigger': [' '],
                                               'driver': [' ']}, index=[0])

                    one_review['rDate'] = pd.to_datetime(one_review['rDate'])

                    # Append one review data to data-frame containing all reviews of current page
                    this_page_reviews = this_page_reviews.append(one_review)

                # Append current page reviews to data-frame containing reviews across all pages in response
                all_reviews = all_reviews.append(this_page_reviews)
                prod_rev_count1 -= len(rev_list)

                # If more reviews to be extracted
                if prod_rev_count1 > 0:
                    # Increment page number by 1 and place API request again for next page
                    curr_pg += 1
                    browser1.get(prefix + p_id + suffix + str(curr_pg))
                    resp = json.loads(browser1.find_element_by_xpath("//body//pre").get_attribute("innerHTML"))

            status_code = 200

        else:  # if no reviews present, append dummy data frame
            print("No reviews for this product.")
            all_reviews = all_reviews.append(pd.DataFrame({'siteCode': ['WM'],
                                                           'pCategory': [kw_str1],
                                                           'rDate': ['#N/A'],
                                                           'rUser': ['#N/A'],
                                                           'rTitle': ['#N/A'],
                                                           'rText': ['#N/A'],
                                                           'rRating': ['#N/A'],
                                                           'rURL': [p_url],
                                                            'pURL': [p_url],
                                                            'sentiScore': [' '],
                                                            'sentiment': [' '],
                                                            'trigger': [' '],
                                                            'driver': [' ']}, index = [0]))

            status_code = 200

    except:
        # If any error while parsing responses, append dummy data-frame
        print("Error in API response! Appending dummy dataframe.")
        all_reviews = all_reviews.append(pd.DataFrame({'siteCode': ['WM'],
                                                       'pCategory': [kw_str1],
                                                       'rDate': ['#N/A'],
                                                       'rUser': ['#N/A'],
                                                       'rTitle': ['#N/A'],
                                                       'rText': ['#N/A'],
                                                       'rRating': ['#N/A'],
                                                       'rURL': [p_url],
                                                        'pURL': [p_url],
                                                        'sentiScore': [' '],
                                                        'sentiment': [' '],
                                                        'trigger': [' '],
                                                        'driver': [' ']}, index = [0]))

        status_code = 500

    return [all_reviews, status_code]

# ######################################################################


# To scrape product information and review information from Walmart site
def walmart_all_info(kw_str1):
    global kw_str, browser, browser1, chrome_path, status_code
    kw_str = kw_str1

    try:
        print 'Keyword: ', kw_str
        logging.info('Keyword: ' + kw_str)

        browser = webdriver.Chrome(chrome_path)
        browser1 = webdriver.Chrome(chrome_path)

        print "Scraper started at ", datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")
        logging.info("Scraper started at " + datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p"))

        # Searches for each keyword and extracts links for each product through all product pages
        # for i in range(0, len(keywords_list)):
        print "Searching for '" + kw_str + "'..."
        logging.info("Searching for '" + kw_str + "'...")

        search_url = "https://www.walmart.com/search/?query=" + kw_str
        browser.get(search_url)

        # element = browser.find_element_by_id("global-search-input")  # Search box on Walmart homepage
        # element.send_keys(kw_str)  # Emulates entering keyword in search box
        # element.send_keys(Keys.RETURN)  # Emulates pressing Enter
        time.sleep(2)

        prod_urls = []
        rev_urls = []

        prods_info = pd.DataFrame({'pModel': [' '],
                                   'pTitle': [' '],
                                   'pBrand': [' '],
                                   'pURL': [' '],
                                   'pRating': [' '],
                                   'price': [' '],
                                   'pImgSrc': [' '],
                                   'pDescr': [' ']}, index=[0])

        all_reviews = pd.DataFrame({'siteCode': ['WM'],
                                    'pCategory': [kw_str],
                                    'rUser': [' '],
                                    'rTitle': [' '],
                                    'rDate': [' '],
                                    'rText': [' '],
                                    'rRating': [' '],
                                    'rURL': [' '],
                                    'pURL': [' '],
                                    'sentiScore': [' '],
                                    'sentiment': [' '],
                                    'trigger': [' '],
                                    'driver': [' ']}, index = [0])

        # Creates aggregated data frame to hold all product information and reviews of all keywords
        all_kw_all_rev = pd.DataFrame({'siteCode': ['WM'],
                                        'pCategory': [kw_str],
                                        'pBrand': [' '],
                                        'pTitle': [' '],
                                        'pModel': [' '],
                                       'pRating': [' '],
                                        'price': [' '],
                                        'pURL': [' '],
                                        'pImgSrc': [' '],
                                        'pDescr': [' '],
                                        'rUser': [' '],
                                        'rTitle': [' '],
                                        'rDate': [' '],
                                        'rRating': [' '],
                                        'rText': [' '],
                                        'rURL': [' '],
                                        'sentiScore': [' '],
                                        'sentiment': [' '],
                                        'trigger': [' '],
                                        'driver': [' ']}, index = [0])

        try:
            has_next_page = True

            # Loop as long as current page is not last
            while has_next_page:
                time.sleep(2)
                # First extract all products listed
                prod_list = browser.find_elements_by_xpath(
                    "//div[@id='searchProductResult']//div[contains(@data-tl-id,'ProductTileListView-')]//div[@class='search-result-product-title listview']//a[1]")
                # Extract product IDs of sponsored products listed
                spons_prod_list = browser.find_elements_by_xpath("//div[@data-us-item-id]")

                # Variables
                all_href = []
                all_prod_id_list = []
                spons_prod_id_list = []
                final_prod_id_list = []
                final_prod_href_list = []
                final_prod_title_list = []
                final_prod_rating_list = []
                final_prod_price_list = []
                final_prod_brand_list = []
                final_prod_img_src_list = []
                final_prod_descr_list = []

                temp_idx_list = []  # To hold indices of product IDs that are NOT sponsored
                p_title = ""
                p_price = ""
                p_brand = ""
                p_rating = ""
                p_img_src = ""
                p_descr = ""

                # Loop through all products listed (including sponsored ones)
                for i in prod_list:
                    # Get the href link to the product page
                    curr_href = i.get_attribute("href")
                    # If query string parameters are present, remove them
                    if "?" in curr_href:
                        curr_href = curr_href.split("?")[0]
                    all_href.append(curr_href)
                    # Extract product ID from href link
                    curr_prod_id = curr_href.split("/")[len(curr_href.split("/")) - 1]
                    all_prod_id_list.append(curr_prod_id)

                # Loop through sponsored products list and store their product ID
                for s in spons_prod_list:
                    curr_spons_href = s.get_attribute("data-us-item-id")
                    spons_prod_id_list.append(curr_spons_href)


                # Shortlist products which are not sponsored. Store their list indices for current page temporarily
                for v in range(len(all_prod_id_list)):
                    if all_prod_id_list[v] not in spons_prod_id_list:
                        temp_idx_list.append(v)
                        final_prod_id_list.append(all_prod_id_list[v])

                # Loop through list indices of final list of products listed as results for search
                # for t in temp_idx_list:  # uncomment to loop thru all products
                for t in range(0, 5):
                    # Product ID
                    print("t=" + str(temp_idx_list[t]))  # make temp_idx_list[t] as t
                    print(all_prod_id_list[temp_idx_list[t]])  # make temp_idx_list[t] as t

                    # Product URL
                    final_prod_href_list.append(all_href[temp_idx_list[t]])  # make temp_idx_list[t] as t
                    print(all_href[temp_idx_list[t]])  # make temp_idx_list[t] as t

                    try:
                        browser1.get(all_href[temp_idx_list[t]])  # make temp_idx_list[t] as t
                        time.sleep(1.5)

                        # Product Title
                        try:
                            p_title = browser1.find_element_by_class_name("prod-ProductTitle").text
                        except:
                            p_title = "#N/A"
                        final_prod_title_list.append(p_title)
                        print(p_title)

                        # Product Price
                        try:
                            p_price = browser1.find_element_by_xpath(
                                "//div[contains(@class, 'prod-rightContainer')]//div[@class ='prod-PriceHero']").get_attribute("innerText")

                        except:
                            try:
                                p_price = browser1.find_element_by_xpath("//span[@data-tl-id='Price-ProductOffer']").get_attribute(
                                    "innerText")
                            except:
                                p_price = "#N/A"

                        if "#N/A" not in p_price:
                            mat = re.findall(r'\$?\s?[0-9]+.[0-9]+', p_price, re.M)
                            if len(mat) > 1:
                                p_price = mat[len(mat) - 1]

                        final_prod_price_list.append(p_price)
                        print(p_price)

                        # Product brand
                        try:
                            p_brand = browser1.find_element_by_class_name("prod-BrandName").text
                        except:
                            p_brand = "#N/A"

                        final_prod_brand_list.append(p_brand)
                        print(p_brand)

                        # Product rating
                        try:
                            p_rating = browser1.find_element_by_xpath("//span[@itemprop='ratingValue']").text
                        except:
                            p_rating = "0.0"

                        final_prod_rating_list.append(p_rating)
                        # print(p_rating)

                        try:
                            p_img_src = browser1.find_element_by_class_name("prod-HeroImage-image").get_attribute("src")
                        except:
                            p_img_src = "#"

                        final_prod_img_src_list.append(p_img_src)
                        print(p_img_src)

                        try:
                            p_descr = (browser1.find_element_by_xpath("//*[@data-tl-id='AboutThis-ShortDescription']").get_attribute("innerText")).encode('utf-8').strip()
                        except:
                            #print(traceback.print_exc())
                            p_descr = "Not Available"
                        print(p_descr)

                    except:
                        print("unable to load product details")
                        p_title = "#N/A"
                        p_price = "#N/A"
                        p_brand = "#N/A"
                        p_rating = "0.0"
                        p_img_src = "#"
                        p_descr = "Not Available"

                    print("writing prods_info")
                    # Create data-frame for adding current product's info
                    prods_info = prods_info.append(pd.DataFrame({'pModel': [all_prod_id_list[temp_idx_list[t]]],  # all_prod_id_list[t]
                                                                 'pTitle': [p_title],
                                                                 'pBrand': [p_brand],
                                                                 'pRating': [p_rating],
                                                                 'pURL': [all_href[temp_idx_list[t]]],  # all_href[t]
                                                                 'price': [p_price],
                                                                 'pImgSrc': [p_img_src],
                                                                 'pDescr': [p_descr]}, index=[0]))

                # Extract reviews of each product and append to aggregated data-frame
                for i in range(len(final_prod_href_list)):  # final_prod_id_list
                    [all_reviews_1p, status_code] = get_reviews(final_prod_id_list[i], final_prod_href_list[i], kw_str)
                    all_reviews = all_reviews.append(all_reviews_1p)

                has_next_page = False  # REMOVE TO LOOP THRU RESULT PAGES

                # UNCOMMENT TO LOOP THRU ALL RESULT PAGES
                '''
                next_page_elem = browser.find_element_by_class_name("paginator-btn-next")
                try:
                    next_page_elem.click()
                    has_next_page = True
                    print("Going to next Results page...")
                except:
                    has_next_page = False
                '''
            # 'while has_next_page' ends here

            status_code = 200
            browser.close()
            browser1.close()

        # If error while extracting/parsing reviews
        except TypeError:
            print "Sorry! Unable to scrape!"
            print traceback.print_exc()
            status_code = 500

        # Any other error
        except:
            print "Error in function!!!"
            print traceback.print_exc()
            status_code = 500

        # browser.close()
        # browser1.close()

        # Before saving the final CSV, add product details to review details
        export_reviews = pd.merge(prods_info, all_reviews, on='pURL', how="outer")
        all_kw_all_rev = all_kw_all_rev.append(export_reviews)

        all_kw_all_rev['pid'] = all_kw_all_rev['pCategory'] + "_" + all_kw_all_rev['pBrand'] + "_" + all_kw_all_rev['pModel']
        all_kw_all_rev['rid'] = all_kw_all_rev['pid'] + "_" + all_kw_all_rev['rUser']
        for index, row in all_kw_all_rev.iterrows():
            row['rid'] += "_" + str(len(row['rText'].encode('utf-8').split(" "))) + "_" + str(len(row['rText']))
        print("%%%%%%%%%%%%%%%%%%%%%")
        print(all_kw_all_rev)
        print("%%%%%%%%%%%%%%%%%%%%%")

        all_prod_slice = all_kw_all_rev[['pid', 'pCategory', 'pRating', 'pBrand', 'pDescr', 'pImgSrc', 'pModel', 'pTitle', 'pURL', 'price', 'siteCode']].copy()
        all_rev_slice = all_kw_all_rev[['pid', 'rid', 'rDate', 'rRating', 'rText', 'rTitle', 'rURL', 'rUser']].copy()
        #all_rev_slice['rid'] = all_rev_slice['pid'] + "_" + all_rev_slice['rUser']

        return [all_kw_all_rev, all_prod_slice, all_rev_slice, status_code]

    except:
        status_code = 500
        print "Error in called function!"
        print traceback.print_exc()
        return [None, None, None, status_code]
