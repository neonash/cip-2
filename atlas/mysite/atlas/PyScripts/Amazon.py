from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
import traceback
from datetime import datetime
import logging
from atlas.config import dbConfig



# Global variables
browser = None
prod_URL = ''
prod_urls_list = []
rev_url = ''
review_urls_list = []
prod_title = ''
prod_brand = ''
price = ''
prod_img_src = ""
prod_descr = ""
review_author = ['']
review_title = ['']
review_date = ['']
review_text = ['']
review_rating = ['']
all_reviews = None
all_kw_all_rev = None  # Data frame to hold all reviews of all products/keywords
prods_info = None
kw_str = ""
chrome_path = dbConfig.dict["chromeDriver"]
status_code = 500


########################################################################


# To scrape product information from Amazon
'''
def amazon_prod_info(kw_str1):
    global browser, prod_URL, prod_title, price, prods_info, chrome_path, kw_str
    kw_str = kw_str1

    try:
        # chrome_path = 'C:\Python27\selenium\webdriver\chromedriver.exe'
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
            prods_info = pd.DataFrame({'pModel': [' '],
                                       'pTitle': [' '],
                                       'pBrand': [' '],
                                       #'pMfr': [' '],
                                       #'pModelNo': [' '],
                                       #'pModel': [' '],
                                       #'pMfrPartNo': [' '],
                                       'pURL': [' '],
                                       'price': [' ']}, index=[0])

            while has_next_page:
                try:
                    result_url = browser.current_url
                    # result_urls_list.append(result_url)

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
                for u in prod_urls:
                    browser.get(u)
                    time.sleep(2)
                    try:
                        redir_elem = browser.find_element_by_xpath("//span[@class='redir-dismiss-x']")
                        redir_elem.click()
                    except:
                        pass

                    print "Scraping product: " + u
                    logging.info("Scraping product: " + u)

                    prod_URL = u  # Current product URL

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
                    keys_list = ["Brand"]  # , "Manufacturer", "Item model number", "Model", "Manufacturer Part Number"]

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
                                    # print traceback.print_exc()
                                    # logging.info(traceback.print_exc())
                                    prod_info_value = '#N/A'

                            values_list[idx] = prod_info_value  # Finally obtain the value
                        # 'if' closes here

                    # Print keys and values extracted from current Product page
                    print keys_list
                    logging.info(keys_list)
                    print values_list
                    logging.info(values_list)

                    # Storing values of required keys in variables
                    prod_ASIN = prod_URL[prod_URL.find("/dp/") + 4: prod_URL.find("/dp/") + 14]  # +4 for ASIN begins after 4th character from "/dp/"; and +14 because ASIN is 10 characters long, starting from start index and end index character is excluded
                    print prod_ASIN
                    prod_brand = values_list[0]  # Brand
                    #prod_mfr = values_list[1]  # Manufacturer
                    #prod_model_no = values_list[2]  # Item model number
                    #prod_model = values_list[3]  # Model
                    #prod_mfr_part_no = values_list[4]  # Manufacturer Part Number

                    # Appending record to main data frame
                    prod_info = pd.DataFrame({'pModel': [prod_ASIN],
                                              'pCategory': [kw_str],
                                              'pTitle': [prod_title],
                                              'pBrand': [prod_brand],
                                              #'pMfr': [prod_mfr],
                                              #pModelNo': [prod_model_no],
                                              #'pModel': [prod_model],
                                              #'pMfrPartNo': [prod_mfr_part_no],
                                              'pURL': [prod_URL],
                                              'price': [price]}, index=[0])
                    prods_info = prods_info.append(prod_info)
                # 'for u in prod_urls' ends here

                # FOLLOWING CODE IS WORKING. IT LOOPS THROUGH ALL RESULT PAGES. COMMENTED OUT TEMPORARILY.
                #if has_next_page:
                #    print "Going to next Results page..."
                #    logging.info("Going to next Results page...")

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
        curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
        temp_keyword = kw_str.replace(" ", "")
        output_file_name = 'AmazonProdsInfo_' + temp_keyword + '_' + curr_timestamp + '.csv'
        full_path = 'C:\Users\Aparna.harihara\PycharmProjects\AuScer\Outputs\Amazon\\' + output_file_name
        print "Saving CSV file for this product @ " + full_path
        logging.info("Saving CSV file for this product @ " + full_path)
        prods_info.to_csv(full_path, index=False, encoding='utf-8')
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
'''

# ########################################################################################


# To extract common URL prefix (for Review pages) from Product page URL
def get_review_url_prefix(p_url):
    # To prepare final prefix
    p_url_1 = p_url.replace("/dp/", "/product-reviews/")
    start_index = None
    for m in re.finditer('ref=', p_url_1):
        start_index = m.start()
        break
    var_prefix = p_url_1[:start_index + 4]  # To extract common prefix from beginning of URL to 'ref='; hence +4
    common_suffix = "cm_cr_dp_see_all_btm?ie=UTF8&reviewerType=all_reviews&showViewpoints=1&sortBy=recent&pageNumber="
    r_url = var_prefix + common_suffix
    return r_url

########################################################################


# To fetch reviews from Amazon (without Import.io)
def get_reviews():
    global all_reviews, prod_URL, prod_title, price, review_author, review_title, review_date, review_text, review_rating, rev_url

    try:
        # To check if reviews are available for this product
        b = browser.find_element_by_xpath("//span[@data-hook='total-review-count']").text
        if b == "0":  # If no reviews are available for this product
            one_review = pd.DataFrame({'siteCode': ['AM'],
                                       'pCategory': [kw_str],
                                       #'pTitle': [prod_title],
                                       #'pBrand': [prod_brand],
                                       'pURL': [prod_URL],
                                       #'price': [price],
                                       'rUser': ["#N/A"],
                                       'rTitle': ["#N/A"],
                                       'rDate': ["#N/A"],
                                       'rText': ["#N/A"],
                                       'rRating': ['#N/A'],
                                       'rURL': [rev_url],
                                       'sentiConfi': [' '],
                                       'sentiment': [' '],
                                       'trigger': [' '],
                                       'driver': [' ']}, index=[0])
            all_reviews = all_reviews.append(one_review)
        else:  # If reviews are available for this product
            # Contains corresponding values from all reviews in the current Review page
            review_author = browser.find_elements_by_xpath("//div[@id='cm_cr-review_list']//a[@data-hook='review-author']")
            review_title = browser.find_elements_by_xpath("//div[@id='cm_cr-review_list']//a[@data-hook='review-title']")
            review_date = browser.find_elements_by_xpath("//div[@id='cm_cr-review_list']//span[@data-hook='review-date']")
            review_text = browser.find_elements_by_xpath("//div[@id='cm_cr-review_list']//span[@data-hook='review-body']")
            review_rating = browser.find_elements_by_xpath("//div[@id='cm_cr-review_list']//i[@data-hook='review-star-rating']//span")

            # Loop through reviews
            for i2 in range(0, len(review_text)):
                try:  # Collating reviews one by one
                    one_review = pd.DataFrame({'siteCode': ['AM'],
                                               'pCategory': [kw_str],
                                               #'pTitle': [prod_title],
                                               #'pBrand': [prod_brand],
                                               'pURL': [prod_URL],
                                               #'price': [price],
                                               'rUser': [review_author[i2].text],
                                               'rTitle': [review_title[i2].text],
                                               'rDate': [review_date[i2].text[3:]],  # Date is prefixed by 'on '; hence +3
                                               'rText': [review_text[i2].text],
                                               #'rRating': [review_rating[i2].get_attribute("innerHTML")],
                                               'rRating': [re.search(r'[0-9](.[0-9])?', (review_rating[i2].get_attribute("innerText"))).group(0)],
                                               'rURL': [rev_url],
                                               'sentiConfi': [' '],
                                               'sentiment': [' '],
                                               'trigger': [' '],
                                               'driver': [' ']}, index=[0])

                    one_review['rDate'] = pd.to_datetime(one_review['rDate'])
                    all_reviews = all_reviews.append(one_review)

                except IndexError:  # If text in review_author is not a hyperlink
                    one_review = pd.DataFrame({'siteCode': ['AM'],
                                               'pCategory': [kw_str],
                                               #'pTitle': [prod_title],
                                               #'pBrand': [prod_brand],
                                               'pURL': [prod_URL],
                                               #'price': [price],
                                               'rUser': ["#N/A"],
                                               'rTitle': [review_title[i2].text],
                                               'rDate': [review_date[i2].text[3:]],
                                               'rText': [review_text[i2].text],
                                               #'rRating': [review_rating[i2].text],
                                               'rRating': [re.search(r'[0-9](.[0-9])?', (review_rating[i2].get_attribute("innerText"))).group(0)],
                                               'rURL': [rev_url],
                                               'sentiConfi': [' '],
                                               'sentiment': [' '],
                                               'trigger': [' '],
                                               'driver': [' ']}, index=[0])

                    one_review['rDate'] = pd.to_datetime(one_review['rDate'])
                    all_reviews = all_reviews.append(one_review)
                except:
                    print "Error in collating reviews at " + rev_url
                    logging.info("Error in collating reviews at " + rev_url)
                    print traceback.print_exc()
                    logging.info(traceback.print_exc())
            # 'for' looping through reviews ends here
        # 'else' of (if b==0) ends here
    # 'try' inside function ends here

    except TypeError:
        pass
    except:
        print "Error in get_reviews()"
        logging.info("Error in get_reviews()")
        print traceback.print_exc()
        logging.info(traceback.print_exc())

########################################################################


# To scrape product information and reviews from Amazon (without Import.io)
def amazon_all_info(kw_str1):
    global prod_title, rev_url, price, prod_img_src, prod_descr, browser, prod_URL, prods_info, kw_str, chrome_path, all_reviews, all_kw_all_rev, status_code
    kw_str = kw_str1

    try:
        print 'Keyword: ', kw_str
        logging.info('Keyword: ' + kw_str)

        # chrome_path = 'C:\Python27\selenium\webdriver\chromedriver.exe'
        browser = webdriver.Chrome(chrome_path)

        print "Scraper started at ", datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")
        logging.info("Scraper started at " + datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p"))

        # Searches for each keyword and extracts links for each product through all product pages
        #for i in range(0, len(kw_str)):
        print "Searching for '" + kw_str + "'..."
        logging.info("Searching for '" + kw_str + "'...")

        browser.get("https://www.amazon.com")

        element = browser.find_element_by_id("twotabsearchtextbox")  # Search box on Amazon homepage
        element.send_keys(kw_str)  # Emulates entering keyword in search box
        element.send_keys(Keys.RETURN)  # Emulates pressing Enter
        time.sleep(2)

        prod_urls = []
        result_urls_list = []

        prods_info = pd.DataFrame({'pModel': [' '],  # ASIN
                                   'pTitle': [' '],
                                   'pBrand': [' '],
                                   # 'pMfr': [' '],
                                   # 'pModelNo': [' '],
                                   # 'pModel': [' '],
                                   # 'pMfrPartNo': [' '],
                                   'pURL': [' '],
                                   'price': [' '],
                                   'pImgSrc': [' '],
                                   'pDescr': [' ']}, index=[0])

        all_reviews = pd.DataFrame({'siteCode': ['AM'],
                                    'pCategory': [kw_str],
                                    'rUser': [' '],
                                    'rTitle': [' '],
                                    'rDate': [' '],
                                    'rText': [' '],
                                    'rRating': [' '],
                                    'rURL': [' '],
                                    'pURL': [' '],
                                    'sentiConfi': [' '],
                                    'sentiment': [' '],
                                    'trigger': [' '],
                                    'driver': [' ']}, index=[0])

        # Creates aggregated data frame to hold all product information and reviews of all keywords
        all_kw_all_rev = pd.DataFrame({'siteCode': ['AM'],
                                       'pCategory': [kw_str],
                                       'pBrand': [' '],
                                       'pTitle': [' '],
                                       'pModel': [' '],
                                       'price': [' '],
                                       'pImgSrc': [' '],
                                       'pDescr': [' '],
                                       'pURL': [' '],
                                       'rUser': [' '],
                                       'rTitle': [' '],
                                       'rDate': [' '],
                                       'rRating': [' '],
                                       'rText': [' '],
                                       'rURL': [' '],
                                       'sentiConfi': [' '],
                                       'sentiment': [' '],
                                       'trigger': [' '],
                                       'driver': [' ']}, index=[0])

        try:
            has_next_page = True  # Initializing to True to make loop run atleast once (for first Result page) (~ do while loop)

            while has_next_page:
                try:
                    result_url = browser.current_url
                    result_urls_list.append(result_url)

                    next_page_tag = browser.find_element_by_id("pagnNextLink")  # Link to next Result page
                    result_url = next_page_tag.get_attribute("href")  # Stored for emulating click action later in the code

                    has_next_page = True

                    print "Next Results page URL stored: " + result_url
                    #logging.info("Next Results page URL stored: " + result_url)

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
                        while "Amazon's Choice" in temp_string[:temp_string.find("\n")] or "Best Seller" in temp_string[:temp_string.find("\n")]:
                            temp_string = temp_string[temp_string.find("\n") + 1:]  # '\n' treated as 1 character; hence +1

                        try:
                            prod_tags1.append(temp_string[:temp_string.find("\n")])
                        except:
                            prod_tags1.append(temp_string)

                # Tags containing results fetched with different XPath to extract Product page link
                #prod_tags2 = browser.find_elements_by_xpath("//ul[@id='s-results-list-atf']//li[contains(@id,'result_')]//a[ @class ='a-link-normal s-access-detail-page  a-text-normal']")
                try:
                    prod_tags2 = browser.find_elements_by_xpath(
                        "//ul[@id='s-results-list-atf']//li[contains(@id,'result_')]//div[@class='s-item-container']//a[@class='a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal']")  # (@class,'a-link-normal s-access-detail-page a-text-normal')]")
                except:
                    prod_tags2 = prod_tags1

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
                for u1 in range(0, 2):  # for u in prod_urls:  # change later
                    u = prod_urls[u1]  # remove this line
                    browser.get(u)
                    time.sleep(1.5)

                    print "Scraping product: " + u
                    logging.info("Scraping product: " + u)

                    prod_URL = u  # Current product URL

                    # Same code as amazon_prod_info ^^^

                    try:  # May not be present when asks ZIP code to confirm location
                        prod_title = browser.find_element_by_id("productTitle").text
                    except:
                        prod_title = '#N/A'

                    try:  # May or may not be present always
                        price = browser.find_element_by_id("priceblock_ourprice").text
                    except:
                        try:
                            price = browser.find_element_by_id("priceblock_saleprice").text  # Variants in display
                        except:
                            price = '#N/A'

                    try:
                        prod_brand = browser.find_element_by_id("brand").text
                    except:
                        prod_brand = '#N/A'

                    try:
                        prod_img_src = browser.find_element_by_xpath("//*[@id='landingImage']").get_attribute("src")
                    except:
                        prod_img_src = "#"

                    try:
                        prod_descr = (browser.find_element_by_id('productDescription').get_attribute("innerText")).encode('utf-8').strip()
                    except:
                        print(traceback.print_exc())
                        prod_descr = "Not Available"

                    # WORKING CODE FOR EXTRACTING FEATURES. DO NOT REMOVE. COMMENTED TEMPORARILY-----------------------
                    '''
                    try:
                        # Available properties for current product, referring as 'keys'
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
                    '''
                    # ------------------------------------------------------------------------------------------------

                    # Storing values of required keys in variables
                    prod_ASIN = prod_URL[prod_URL.find("/dp/") + 4: prod_URL.find(
                        "/dp/") + 14]  # +4 for ASIN begins after 4th character from "/dp/"; and +14 because ASIN is 10 characters long, starting from start index and end index character is excluded
                    print prod_ASIN

                    # DO NOT DELETE. WORKING CODE COMMENTED TEMPORARILY.----------------------------------------------
                    '''
                    prod_brand = values_list[0]  # Brand
                    prod_mfr = values_list[1]  # Manufacturer
                    prod_model_no = values_list[2]  # Item model number
                    prod_model = values_list[3]  # Model
                    prod_mfr_part_no = values_list[4]  # Manufacturer Part Number
                    '''
                    # ------------------------------------------------------------------------------------------------

                    # Appending record to main data frame
                    prod_info = pd.DataFrame({'pModel': [prod_ASIN],
                                              'pTitle': [prod_title],
                                              'pBrand': [prod_brand],
                                              'pURL': [prod_URL],
                                              'price': [price],
                                              'pImgSrc': [prod_img_src],
                                              'pDescr': [prod_descr]}, index=[0])

                    # DO NOT DELETE. WORKING CODE COMMENTED TEMPORARILY.----------------------------------------------
                    '''
                    'pMfr': [prod_mfr],
                    'pModelNo': [prod_model_no],
                    'pModel': [prod_model],
                    'pMfrPartNo': [prod_mfr_part_no],
                    '''
                    # ------------------------------------------------------------------------------------------------

                    prods_info = prods_info.append(prod_info)
                    # Same code as amazon_prod_info, ends here ^^^

                    rev_url_prefix = get_review_url_prefix(
                        prod_URL)  # Obtain the common prefix for reviews, from product URL
                    rev_url = rev_url_prefix + "1"  # Full url, starting with page number = 1
                    review_urls_list.append(rev_url)

                    print rev_url
                    #logging.info(rev_url)

                    browser.get(rev_url)
                    time.sleep(2)
                    get_reviews()  # Scrape reviews from first page

                    # To extract last page number of Review pages
                    try:
                        elem = browser.find_element_by_xpath("//ul[contains(@class, 'a-pagination')]//li[last() - 1]")
                        last_page_number = int(str(elem.text).replace(",", ""))
                    except:  # If only one page of reviews is present
                        last_page_number = 1

                    print "Total Review pages: " + str(last_page_number)
                    #logging.info("Total Review pages: " + str(last_page_number))

                    # WORKING CODE. TEMPORARILY COMMENTED TO REDUCE LOOPS. DO NOT REMOVE.------------------------

                    # Loop from page 2 till last page, as page 1 is already added to reviews_urls_list, and add to list
                    if last_page_number == 1:
                        has_next_page = False

                    else:
                        for i1 in range(2, last_page_number + 1):  # +1 because 2nd parameter is count, not index; and count will be length +1)
                            rev_url = rev_url_prefix + str(i1)  # Generate the URL by changing page number
                            review_urls_list.append(rev_url)

                            print rev_url
                            #logging.info(rev_url)

                            browser.get(rev_url)
                            get_reviews()

                    # ---------------------------------------------------------------------------------------------

                # 'for u in prods_url' closes here^^^

                # remove later. Just for debugging
                #has_next_page = False

                if has_next_page:
                    print "Going to next Results page..."
                    logging.info("Going to next Results page...")

                    browser.get(result_url)
                    time.sleep(4)
            # 'while has_next_page' closes here

            status_code = 200
            browser.close()

        except:  # try inside for loop keywords_list
            print "Error!!!"
            logging.info("Error!!!")
            status_code = 500
            print traceback.print_exc()
            logging.info(traceback.print_exc())

        print "Scraping '" + kw_str + "' done..."
        logging.info("Scraping '" + kw_str + "' done...")

        '''
        # Saving ProdsInfo file for each keyword/product searched
        curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
        temp_keyword = kw_str.replace(" ", "")
        output_file_name = 'AmazonProdsInfo_' + temp_keyword + '_' + curr_timestamp + '.csv'
        full_path = 'C:\Users\Aparna.harihara\PycharmProjects\AuScer\Outputs\Amazon\\' + output_file_name
        print "Saving file at ... " + full_path
        logging.info("Saving file at ... " + full_path)
        prods_info.to_csv(full_path, index=False, encoding='utf-8')

        # Saving CSV file for reviews
        curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
        temp_keyword = kw_str.replace(" ", "")
        output_file_name = 'Amazon_' + temp_keyword + '_' + curr_timestamp + '.csv'
        full_path = 'C:\Users\Aparna.harihara\PycharmProjects\AuScer\Outputs\Amazon\\' + output_file_name
        print "Saving the file at... " + full_path
        logging.info("Saving the file at... " + full_path)
        all_reviews.to_csv(full_path, index=False, encoding='utf-8')
        '''
        # for loop keywords_list closes here

        # browser.close()

        # Before saving the final CSV, add product details to it
        export_reviews = pd.merge(prods_info, all_reviews, on='pURL', how="outer")
        #print export_reviews

        all_kw_all_rev = all_kw_all_rev.append(export_reviews)
        all_kw_all_rev['pid'] = all_kw_all_rev['pCategory'] + "_" + all_kw_all_rev['pBrand'] + "_" + all_kw_all_rev['pModel']
        all_kw_all_rev['rid'] = all_kw_all_rev['pid'] + "_" + all_kw_all_rev['rUser']
        for index, row in all_kw_all_rev.iterrows():
            row['rid'] += "_" + str(len(row['rText'].encode('utf-8').split(" "))) + "_" + str(len(row['rText']))
        print("%%%%%%%%%%%%%%%%%%%%%")
        print(all_kw_all_rev)
        print("%%%%%%%%%%%%%%%%%%%%%")

        all_prod_slice = all_kw_all_rev[['pid', 'pCategory', 'pBrand', 'pDescr', 'pImgSrc', 'pModel', 'pTitle', 'pURL', 'price', 'siteCode']].copy()
        all_rev_slice = all_kw_all_rev[['pid', 'rid', 'rDate', 'rRating', 'rText', 'rTitle', 'rURL', 'rUser']].copy()
        #all_rev_slice['rid'] = all_rev_slice['pid'] + "_" + all_rev_slice['rUser']

        return [all_kw_all_rev, all_prod_slice, all_rev_slice, status_code]
    except:
        print "Error!!!"
        logging.info("Error!!!")
        print traceback.print_exc()
        logging.info(traceback.print_exc())
        status_code = 500
        return [None, None, None, status_code]

#######################################################################
