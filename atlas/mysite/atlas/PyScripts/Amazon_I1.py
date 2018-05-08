from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import traceback
from datetime import datetime
import logging
import json
import requests
import ast
from functools import reduce  # forward compatibility for Python 3
import operator
from atlas.config import dbConfig


# Global variables
browser = None
result_urls_list = []  # To hold all Result page URLs
prod_URL = None  # To hold current Product page URL
prod_urls_list = []  # To hold all Product page URLs from a Result page
rev_url = None  # To hold current Review page URL
review_urls_list = []  # To hold all Review page URLs for a product
prod_title = ''
price = ''
prods_info = None  # Data frame to hold product information all products
all_reviews = None  # Data frame to hold all reviews of one product (iteration)
all_kw_all_rev = None  # Data frame to hold all reviews of all products/keywords
status_code = 500
kw_str = ""

# ########################################################################################


# Override function to access dictionary
def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)

##########################################################################################


# To extract common URL prefix (for Review pages) from Product page URL
def get_review_url_prefix(p_url):
    # To prepare final prefix
    p_url_1 = p_url.replace("/dp/", "/product-reviews/")
    start_index = None
    for m in re.finditer('ref=sr_1_', p_url_1):
        start_index = m.start()
        break
    var_prefix = p_url_1[:start_index + 4]  # To extract common prefix from beginning of URL to 'ref='; hence +4

    # To add common suffix for Review page URLs; full URL minus value of pageNumber
    common_suffix = "cm_cr_dp_see_all_btm?ie=UTF8&reviewerType=all_reviews&showViewpoints=1&sortBy=recent&pageNumber="
    r_url = var_prefix + common_suffix
    return r_url

##########################################################################################


# To scrape product information from Amazon
def amazon_prod_info(kw_str1):
    global browser, prod_URL, prod_title, price, prods_info, kw_str
    kw_str = kw_str1

    try:
        # chrome_path = 'C:\Python27\selenium\webdriver\chromedriver.exe'
        chrome_path = dbConfig.dict["chromeDriver"]
        browser = webdriver.Chrome(chrome_path)

        print 'Keywords: ', kw_str
        logging.info('Keywords: ' + kw_str)

        print "Scraper started at ", datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")
        logging.info("Scraper started at " + datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p"))

        # Searches for each keyword and extracts links for each product through all product pages
        #for i in range(0, len(keywords_list)):
        print "Searching for '" + kw_str + "'..."
        logging.info("Searching for '" + kw_str + "'...")

        browser.get("https://www.amazon.com")

        element = browser.find_element_by_id("twotabsearchtextbox")  # Search box on Amazon homepage
        element.send_keys(kw_str)  # Emulates entering keyword in search box
        element.send_keys(Keys.RETURN)  # Emulates pressing Enter
        time.sleep(2)

        try:
            has_next_page = True  # Initializing to True to make loop run atleast once (for first page) (~ do while loop)
            prod_urls = []
            prods_info = pd.DataFrame({'pModel': [' '],  # ASIN
                                       'pCategory': [kw_str],
                                       'pTitle': [' '],
                                       'pBrand': [' '],
                                       # 'pMfr': [' '],
                                       # 'pModelNo': [' '],
                                       # 'pModel': [' '],
                                       # 'pMfrPartNo': [' '],
                                       'pURL': [' '],
                                       'price': [' ']}, index=[0])

            while has_next_page:
                try:
                    result_url = browser.current_url
                    result_urls_list.append(result_url)

                    next_page_tag = browser.find_element_by_id("pagnNextLink")  # Link to next Result page
                    result_url = next_page_tag.get_attribute("href")  # Stored for emulating click action later in the code

                    has_next_page = True

                    print "Next Results page URL stored: " + result_url
                    logging.info("Next Results page URL stored: " + result_url)

                except:  # If link to next Result page not found
                    has_next_page = False

                # Find all products listed on the Result page (including irrelevant results like suggestions and ads)
                prod_tags = browser.find_elements_by_xpath("//ul[@id='s-results-list-atf']//li[contains(@id,'result_')]")

                prod_tags1 = []  # To hold products from 'prod_tags', but only relevant Results (clean set)

                for p in prod_tags:
                    if "Sponsored" not in p.text and "Shop by Category" not in p.text:  # Filter out irrelevant results
                        # To remove phrases (if present) like "Best Seller" or "Amazon's Choice" from product details
                        temp_string = p.text

                        # Select first line of innerHTML content and check for phrases
                        # If either of the phrases is present, select the second line of innerHTML (product title)
                        while "Amazon" in temp_string[:temp_string.find("\n")] or "Best Seller" in temp_string[:temp_string.find("\n")]:
                            temp_string = temp_string[temp_string.find("\n")+1:]  # '\n' treated as 1 character; hence +1

                        try:
                            prod_tags1.append(temp_string[:temp_string.find("\n")])
                        except:
                            prod_tags1.append(temp_string)

                # Tags containing results fetched with different XPath to extract Product page link
                prod_tags2 = browser.find_elements_by_xpath("//ul[@id='s-results-list-atf']//li[contains(@id,'result_')]//a[ @class ='a-link-normal s-access-detail-page  a-text-normal']")

                prod_urls = []  # All Product page links on a Result page

                for p in range(0, len(prod_tags1)):
                    for q in range(0, len(prod_tags2)):
                        # To check if both lists refer to the same product, and then store its URL
                        if prod_tags1[p] in prod_tags2[q].text or prod_tags2[q].text in prod_tags1[p]:
                            # Append URL to current Result page's product URLs list
                            prod_urls.append(prod_tags2[q].get_attribute("href"))

                            # Append URL to list of product URLs across all Result pages
                            prod_urls_list.append(prod_tags2[q].get_attribute("href"))

                # Loop through all product URLs on current Result page
                for u in range(0, 3):  # for u in prod_urls:
                    browser.get(prod_urls[u])
                    time.sleep(2)

                    print "Scraping product: " + prod_urls[u]
                    logging.info("Scraping product: " + prod_urls[u])

                    prod_URL = prod_urls[u]  # Current product URL

                    try:  # May not be present when asks ZIP code to confirm location
                        prod_title = browser.find_element_by_id("productTitle").text
                    except:
                        prod_keys.append('#N/A')

                    try:  # May or may not be present always
                        price = browser.find_element_by_id("priceblock_ourprice").text  # Variants in display
                    except:
                        try:
                            price = browser.find_element_by_id("priceblock_saleprice").text  # Variants in display
                        except:
                            price = '#N/A'

                    try:  # Available properties for current product, referring as 'keys'
                        prod_keys = browser.find_elements_by_class_name("prodDetSectionEntry")
                    except:
                        prod_keys.append('#N/A')

                    # List of required keys hardcoded
                    keys_list = ["Brand Name"]  # , "Manufacturer", "Item model number", "Model", "Manufacturer Part Number"]

                    # Initializing list of values held by keys for same product
                    values_list = ['#N/A']  # , '#N/A', '#N/A', '#N/A', '#N/A']

                    # Loop through keys available for product
                    for pkv in range(len(prod_keys)):
                        # If available key matches required key
                        if prod_keys[pkv].text in keys_list:
                            idx = keys_list.index(prod_keys[pkv].text)  # Store index of key

                            try:
                                # Obtain respective value for that key
                                # Indexing in XPath starts from 1; hence +1
                                prod_info_value = browser.find_element_by_xpath("//*[@id='productDetails_techSpec_section_1']//tbody//tr[" + str(pkv + 1) + "]//td").text
                            except:
                                try:  # Product information may be given under one of two headings or ID attributes
                                    prod_info_value = browser.find_element_by_xpath("//*[@id='productDetails_detailBullets_sections1']//tbody//tr[" + str(pkv + 1) + "]//td").text
                                except:
                                    try:
                                        redir_elem = browser.find_element_by_xpath("//span[@class='redir-dismiss-x']")
                                        redir_elem.click()
                                        try:
                                            # Repeat trying to extract table data
                                            prod_info_value = browser.find_element_by_xpath("//*[@id='productDetails_techSpec_section_1']//tbody//tr[" + str(pkv + 1) + "]//td").text
                                        except:
                                            try:  # Product information may be given under one of two headings or ID attributes
                                                prod_info_value = browser.find_element_by_xpath("//*[@id='productDetails_detailBullets_sections1']//tbody//tr[" + str(pkv + 1) + "]//td").text
                                            except:
                                                prod_info_value = '#N/A'

                                    except:
                                        print traceback.print_exc()
                                        logging.info(traceback.print_exc())

                                        prod_info_value = '#N/A'

                            values_list[idx] = prod_info_value  # Finally obtain the value
                        # 'if' closes here

                    # Print keys and values extracted from current Product page
                    print keys_list
                    logging.info(keys_list)
                    print values_list
                    logging.info(values_list)

                    # Storing values of required keys in variables
                    prod_ASIN = prod_URL[prod_URL.find("/dp/") + 4: prod_URL.find(
                        "/dp/") + 14]  # +4 for ASIN begins after 4th character from "/dp/"; and +14 because ASIN is 10 characters long, starting from start index and end index character is excluded
                    print prod_ASIN
                    prod_brand = values_list[0]  # Brand
                    # prod_mfr = values_list[1]  # Manufacturer
                    # prod_model_no = values_list[2]  # Item model number
                    # prod_model = values_list[3]  # Model
                    # prod_mfr_part_no = values_list[4]  # Manufacturer Part Number

                    # Appending record to main data frame
                    prod_info = pd.DataFrame({'pModel': [prod_ASIN],  # ASIN
                                              'pCategory': [kw_str],
                                              'pTitle': [prod_title],
                                              'pBrand': [prod_brand],
                                              # 'pMfr': [prod_mfr],
                                              # 'pModelNo': [prod_model_no],
                                              # 'pModel': [prod_model],
                                              # 'pMfrPartNo': [prod_mfr_part_no],
                                              'pURL': [prod_URL],
                                              'price': [price]}, index=[0])
                    prods_info = prods_info.append(prod_info)
                # 'for u in prod_urls' ends here

                # FOLLOWING CODE IS WORKING. IT LOOPS THROUGH ALL RESULT PAGES. COMMENTED OUT TEMPORARILY.
                #if has_next_page:
                #    print "Going to next Results page..."
                #    logging.info("Going to next Results page...")
                #
                #    browser.get(result_url)
                #    time.sleep(4)
                    has_next_page = False  # REMOVE LATER
            # 'while has_next_page' ends here
            status_code = 200
        #'try' inside 'for' for looping through keywords ends here

        except:
            print "Error!!!"
            logging.info("Error!!!")
            print traceback.print_exc()
            logging.info(traceback.print_exc())
            status_code = 500

        # Saving CSV for each keyword/product
        '''
        curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
        temp_keyword = keywords_list[i].replace(" ", "")
        output_file_name = 'AmazonProdsInfo_' + temp_keyword + '_' + curr_timestamp + '.csv'
        full_path = r'C:\Users\\akshat.gupta\Documents\django-atlas\mysite\\atlas\PyScripts\Outputs\Amazon_I\\' + output_file_name
        print "Saving CSV file for this product @ " + full_path
        logging.info("Saving CSV file for this product @ " + full_path)
        prods_info.to_csv(full_path, index=False, encoding='utf-8')
        '''
        # 'for' for looping through keywords ends here
    # 'try' inside function ends here

    except TypeError:
        pass
    except:
        print "Error!!!"
        logging.info("Error!!!")
        print traceback.print_exc()
        logging.info(traceback.print_exc())
        status_code = 500

# ########################################################################################


# To extract reviews from API response
def get_reviews(resp, prod_URL, rev_URL, kw_str1):
    global kw_str
    kw_str = kw_str1
    
    one_review = pd.DataFrame({ 'siteCode': ['AM'],
                               'pCategory': [kw_str],
                                'rUser': [' '],
                                'rTitle': [' '],
                                'rDate': [' '],
                                'rText': [' '],
                                'rRating': [' '],
                                'rURL': [' '],
                                'pURL': [' ']}, index=[0])

    this_page_reviews = pd.DataFrame({'siteCode': ['AM'],
                                      'pCategory': [kw_str],
                                      'rUser': [' '],
                                      'rTitle': [' '],
                                      'rDate': [' '],
                                      'rText': [' '],
                                      'rRating': [' '],
                                      'rURL': [' '],
                                      'pURL': [' ']}, index=[0])

    list1_data = getFromDict((getFromDict(resp, ["extractorData", "data"]))[0], ["group"])
    # dict1_data = list1_data[0]
    # list2_data = getFromDict(dict1_data, ["group"])

    # print type(list2_data)
    # print list2_data

    for i in list1_data:  # i is each set of review details
        rev_contents = ['', '', '', '', '']  # Review contents: rDate, rUser, rTitle, rText, rRating

        rev_contents[0] = getFromDict(getFromDict(i, ["rDate"])[0], ["text"])
        # print rev_contents[0]

        rev_contents[1] = getFromDict(getFromDict(i, ["rUser"])[0], ["text"])
        # print rev_contents[1]
        # print getFromDict(getFromDict(i, ["rUser"])[0], ["href"])

        rev_contents[2] = getFromDict(getFromDict(i, ["rTitle"])[0], ["text"])
        # print rev_contents[2]
        # print getFromDict(getFromDict(i, ["rTitle"])[0], ["href"])

        rev_contents[3] = getFromDict(getFromDict(i, ["rText"])[0], ["text"])
        # print rev_contents[3]

        rev_contents[4] = getFromDict(getFromDict(i, ["rRating"])[0], ["text"])
        # print rev_contents[4]
        # print getFromDict(getFromDict(i, ["rRating"])[0], ["href"])

        # print "$$$$"

        one_review = pd.DataFrame({'siteCode': ['AM'],
                                   'pCategory': [kw_str],
                                   'rDate': [rev_contents[0]],
                                   'rUser': [rev_contents[1]],
                                   'rTitle': [rev_contents[2]],
                                   'rText': [rev_contents[3]],
                                   'rRating': [rev_contents[4]],
                                   'rURL': [rev_URL],
                                   'pURL': [prod_URL]}, index=[0])

        this_page_reviews = this_page_reviews.append(one_review)

    return this_page_reviews

# #######################################################################################


# To make API request
def make_api_request(url):

    # URL of specific extractor trained to scrape reviews
    # extractor_url = "https://extraction.import.io/query/extractor/090219b7-e654-4f65-a332-dec4faa9c7a9"
    # extractor_url = "https://extraction.import.io/query/extractor/07c45ff7-8c61-436f-aef6-bc347862cf90"
    extractor_url = "https://extraction.import.io/query/extractor/c9f287a7-f3c3-4904-8612-edd8a9e1b84b"
    api_key = 'b09881abbf844c46ba85b24f5c34ada541a56e16e986686fce9afd7bdceed88084c424652266c69ffa369fb8febd05378e3fc2ef195e763912af1ede79413f102b65ab9bc7cb2e40aacdd681f9aea699'
    live_api_query = extractor_url + "?_apikey=" + api_key + "&url=" + url

    a = json.loads(requests.get(live_api_query).text)
    time.sleep(1)
    return a

#########################################################################################


# IMPORTANT : ONLY CHANGE FOR LOOP FOR PROD_URLS AND LAST PAGE NUMBER
# To scrape product information and reviews from Amazon (using Import.io)
def amazon_i_all_info(kw_str1):
    global browser, rev_url, prod_title, price, prods_info, all_reviews, all_kw_all_rev, review_urls_list, kw_str
    kw_str = kw_str1

    try:
        print 'Keywords: ', kw_str
        logging.info('Keywords: ' + kw_str)

        # chrome_path = 'C:\Python27\selenium\webdriver\chromedriver.exe'
        chrome_path = dbConfig.dict["chromeDriver"]
        browser = webdriver.Chrome(chrome_path)

        print "Scraper started at ", datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")
        logging.info("Scraper started at " + datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p"))

        # Searches for each keyword and extracts links for each product through all product pages
        #for i in range(0, len(keywords_list)):
        print "Searching for '" + kw_str + "'..."
        logging.info("Searching for '" + kw_str + "'...")

        browser.get("https://www.amazon.com")

        element = browser.find_element_by_id("twotabsearchtextbox")  # Search box on Amazon homepage
        element.send_keys(kw_str)  # Emulates entering keyword in search box
        element.send_keys(Keys.RETURN)  # Emulates pressing Enter
        time.sleep(2)

        prod_urls = []
        rev_urls = []
        prods_info = pd.DataFrame({'pModel': [' '],  # ASIN
                                   'pTitle': [' '],
                                   'pBrand': [' '],
                                   # 'pMfr': [' '],
                                   # 'pModelNo': [' '],
                                   # 'pModel': [' '],
                                   # 'pMfrPartNo': [' '],
                                   'pURL': [' '],
                                   'price': [' ']}, index=[0])

        all_reviews = pd.DataFrame({'siteCode': ['AM'],
                                    'pCategory': [kw_str],
                                    'rUser': [' '],
                                    'rTitle': [' '],
                                    'rDate': [' '],
                                    'rText': [' '],
                                    'rRating': [' '],
                                    'rURL': [' '],
                                    'pURL': [' ']}, index=[0])

        # Creates aggregated data frame to hold all product information and reviews of all keywords
        all_kw_all_rev = pd.DataFrame({'siteCode': ['AM'],
                                       'pCategory': [kw_str],
                                       'pBrand': [' '],
                                       'pTitle': [' '],
                                       'pModel': [' '],
                                       'price': [' '],
                                       'pURL': [' '],
                                       'rUser': [' '],
                                       'rTitle': [' '],
                                       'rDate': [' '],
                                       'rRating': [' '],
                                       'rText': [' '],
                                       'rURL': [' ']}, index=[0])

        try:
            has_next_page = True  # Initializing to True to make loop run atleast once (for first page) (~ do while loop)
            while has_next_page:
                try:
                    result_url = browser.current_url
                    result_urls_list.append(result_url)

                    next_page_tag = browser.find_element_by_id("pagnNextLink")  # Link to next Result page
                    result_url = next_page_tag.get_attribute("href")  # Stored for emulating click action later in the code

                    has_next_page = True

                    print "Next Results page URL stored: " + result_url
                    logging.info("Next Results page URL stored: " + result_url)

                except:  # If link to next Result page not found
                    has_next_page = False

                # Find all products listed on the Result page (including irrelevant results like suggestions and ads)
                prod_tags = browser.find_elements_by_xpath("//ul[@id='s-results-list-atf']//li[contains(@id,'result_')]")

                prod_tags1 = []  # To hold products from 'prod_tags', but only relevant Results (clean set)

                for p in prod_tags:
                    if "Sponsored" not in p.text and "Shop by Category" not in p.text:  # Filter out irrelevant results
                        # To remove phrases (if present) like "Best Seller" or "Amazon's Choice" from product details
                        temp_string = p.text

                        # Select first line of innerHTML content and check for phrases
                        # If either of the phrases is present, select the second line of innerHTML (product title)
                        while "Amazon" in temp_string[:temp_string.find("\n")] or "Best Seller" in temp_string[:temp_string.find("\n")]:
                            temp_string = temp_string[temp_string.find("\n") + 1:]  # '\n' treated as 1 character; hence +1

                        try:
                            prod_tags1.append(temp_string[:temp_string.find("\n")])
                        except:
                            prod_tags1.append(temp_string)

                # Tags containing results fetched with different XPath to extract Product page link
                prod_tags2 = browser.find_elements_by_xpath("//ul[@id='s-results-list-atf']//li[contains(@id,'result_')]//a[ @class ='a-link-normal s-access-detail-page  a-text-normal']")

                prod_urls = []  # All Product page links on a Result page

                for p in range(0, len(prod_tags1)):
                    for q in range(0, len(prod_tags2)):
                        # To check if both lists refer to the same product, and then store its URL
                        if prod_tags1[p] in prod_tags2[q].text or prod_tags2[q].text in prod_tags1[p]:
                            # Append URL to current Result page's product URLs list
                            prod_urls.append(prod_tags2[q].get_attribute("href"))

                            # Append URL to list of product URLs across all Result pages
                            prod_urls_list.append(prod_tags2[q].get_attribute("href"))

                # Loop through all product URLs on current Result page
                for u1 in range(0, 3):  # for u in prod_urls:  # change later
                    u = prod_urls[u1]  # remove this line
                    browser.get(u)

                    print "Scraping product: " + u
                    logging.info("Scraping product: " + u)

                    prod_URL = u  # Current product URL

                    # Same code as amazon_prod_info-------------------

                    try:  # May not be present when asks ZIP code to confirm location
                        prod_title = browser.find_element_by_id("productTitle").text
                    except:
                        price = '#N/A'

                    try:  # May or may not be present always
                        price = browser.find_element_by_id("priceblock_ourprice").text  # Variants in display
                    except:
                        try:
                            price = browser.find_element_by_id("priceblock_saleprice").text  # Variants in display
                        except:
                            price = '#N/A'

                    try:  # Available properties for current product, referring as 'keys'
                        prod_keys = browser.find_elements_by_class_name("prodDetSectionEntry")  # all keys
                    except:
                        prod_keys.append('#N/A')

                    # List of required keys hardcoded
                    keys_list = ["Brand Name"]  # , "Manufacturer", "Item model number", "Model", "Manufacturer Part Number"]

                    # Initializing list of values held by keys for same product
                    values_list = ['#N/A']  # , '#N/A', '#N/A', '#N/A', '#N/A']

                    # Loop through keys available for product
                    for pkv in range(len(prod_keys)):

                        # If available key matches required key
                        if prod_keys[pkv].text in keys_list:
                            idx = keys_list.index(prod_keys[pkv].text)  # Store index of key

                            try:
                                # Obtain respective value for that key
                                # Indexing in XPath starts from 1; hence +1
                                prod_info_value = browser.find_element_by_xpath("//*[@id='productDetails_techSpec_section_1']//tbody//tr[" + str(pkv + 1) + "]//td").text
                            except:
                                try:  # Product information may be given under one of two headings or ID attributes
                                    prod_info_value = browser.find_element_by_xpath("//*[@id='productDetails_detailBullets_sections1']//tbody//tr[" + str(pkv + 1) + "]//td").text
                                except:
                                    print traceback.print_exc()
                                    logging.info(traceback.print_exc())

                                    prod_info_value = '#N/A'

                            values_list[idx] = prod_info_value  # Finally obtain the value
                        # 'if' closes here

                    # Print keys and values extracted from current Product page
                    print keys_list
                    logging.info(keys_list)
                    print values_list
                    logging.info(values_list)

                    # Storing values of required keys in variables
                    prod_ASIN = prod_URL[prod_URL.find("/dp/") + 4: prod_URL.find(
                        "/dp/") + 14]  # +4 for ASIN begins after 4th character from "/dp/"; and +14 because ASIN is 10 characters long, starting from start index and end index character is excluded
                    print prod_ASIN
                    prod_brand = values_list[0]  # Brand
                    # prod_mfr = values_list[1]  # Manufacturer
                    # prod_model_no = values_list[2]  # Item model number
                    # prod_model = values_list[3]  # Model
                    # prod_mfr_part_no = values_list[4]  # Manufacturer Part Number

                    # Appending record to main data frame
                    prod_info = pd.DataFrame({'pModel': [prod_ASIN],  # ASIN
                                              'pTitle': [prod_title],
                                              'pBrand': [prod_brand],
                                              # 'pMfr': [prod_mfr],
                                              # 'pModelNo': [prod_model_no],
                                              # 'pModel': [prod_model],
                                              # 'pMfrPartNo': [prod_mfr_part_no],
                                              'pURL': [prod_URL],
                                              'price': [price]}, index=[0])
                    prods_info = prods_info.append(prod_info)
                    # Same code as amazon_prod_info, ends here ^-----------------------------^

                    rev_url_prefix = get_review_url_prefix(prod_URL)  # Obtain the common prefix for reviews, from product URL
                    rev_url = rev_url_prefix + "1"  # Full URL, starting with page number = 1
                    review_urls_list.append(rev_url)

                    print rev_url
                    logging.info(rev_url)

                    browser.get(rev_url)

                    # To extract last page number of Review pages
                    try:
                        elem = browser.find_element_by_xpath("//ul[@class = 'a-pagination']//li[last() - 1]")
                        last_page_number = int(elem.text)
                    except:  # If only one page of reviews is present
                        last_page_number = 1

                    print "Total Review pages: " + str(last_page_number)
                    logging.info("Total Review pages: " + str(last_page_number))

                    # Loop from page 2 till last page, as page 1 is already added to reviews_urls_list, and add to list
                    #for i1 in range(2, last_page_number + 1):  # +1 because 2nd parameter is an excluded index)

                    # for i1 in range(2, 3):  # numbers in range 1 to 3, not including 3
                    #rev_url = rev_url_prefix + "2"  # str(i1)  # Generate the URL by changing page number
                    #review_urls_list.append(rev_url)
                    #print rev_url
                    #logging.info(rev_url)
                    # else ends here---

                    # Now loop through the generated Review URLs and give as input to Import.io API query string
                    print "Count of review urls in list: " + str(len(review_urls_list))
                    for r2 in review_urls_list:
                        print "Review URL in this loop: " + r2
                        response = make_api_request(r2)
                        time.sleep(3)

                        # print type(response)
                        this_pg_reviews = get_reviews(response, prod_URL, r2, kw_str)
                        all_reviews = all_reviews.append(this_pg_reviews)
                        # time.sleep(3)

                        # Line break indicator for readability
                        print "Going to next Review page..."
                        logging.info("Going to next Review page...")

                    # 'for' looping through review_urls_list ends here
                    review_urls_list = []

                # 'for u in prod_urls' closes here ^

                # remove later. Just for debugging
                has_next_page = False

                if has_next_page:
                    print "Going to next Results page..."
                    logging.info("Going to next Results page...")

                    browser.get(result_url)
                    time.sleep(4)

            # 'while has_next_page' closes here
        # 'try' inside 'for' for looping through keywords ends here
            status_code = 200

        except TypeError:
            pass
        except:
            print "Error!!!"
            logging.info("Error!!!")
            print traceback.print_exc()
            logging.info(traceback.print_exc())
            status_code = 500

        # Saving CSV with product information for each keyword/product
        '''
        curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
        temp_keyword = keywords_list[i].replace(" ", "")
        output_file_name = 'AmazonProdsInfo_' + temp_keyword + '_' + curr_timestamp + '.csv'
        full_path = dbConfig.dict["amazonOutput"] + output_file_name
        print "Saving CSV file with product information for this product @ " + full_path
        logging.info("Saving CSV file with product information for this product @ " + full_path)
        prods_info.to_csv(full_path, index=False, encoding='utf-8')

        # Saving CSV with reviews for each keyword/product
        output_file_name = 'AmazonI_' + temp_keyword + '_' + curr_timestamp + '.csv'
        full_path = dbConfig.dict["amazonOutput"] + output_file_name
        print "Saving CSV file with reviews for this product @ " + full_path
        logging.info("Saving CSV file with reviews for this product @ " + full_path)
        all_reviews.to_csv(full_path, index=False, encoding='utf-8')
        '''
        # Before saving the final CSV, add product details to it
        export_reviews = pd.merge(prods_info, all_reviews, on='pURL', how="outer")

        all_kw_all_rev = all_kw_all_rev.append(export_reviews)

        #  'for' looping through keywords ends here

        return [all_kw_all_rev, status_code]
    # 'try' inside function ends here

    except:
        print "Error!!!"
        logging.info("Error!!!")
        print traceback.print_exc()
        logging.info(traceback.print_exc())
        status_code = 500
