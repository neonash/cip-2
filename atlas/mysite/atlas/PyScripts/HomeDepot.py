from selenium import webdriver
import pandas as pd
import time
import traceback
from datetime import datetime
import logging
import urllib
from atlas.config import dbConfig


# Global variables
browser = None
next_page_link = ''  # Holds link to the next Result page
pagination = []  # Holds list of all Result pages
has_next_page = False  # If current page HAS a next page (for PRODUCTS)
links_list = []  # Holds links to all products on current Result page
all_links_list = []  # Holds links of all products through all pages
is_last_page = True  # If current page IS the last page (for REVIEWS)
all_reviews = []  # Holds all reviews of one product (iteration)
all_kw_all_rev = []  # Holds all reviews of all products/keywords
prods_info = []   # Holds all product information for all products
status_code = 500
kw_str = ""


###################################################################


# Scrape links for each product on current Result page, and store link to next Result page
def link_scraper():
    #print("inside link scraper")
    global links_list, next_page_link, pagination, has_next_page, browser

    links = []  # Links obtained on current Result page

    prods = browser.find_elements_by_xpath("//div[contains(@class,'pod-plp__description')]//a")  # Links to products
    for p in prods:
        links.append(p.get_attribute("href"))

    # To check if link to next Result page is present
    try:
        next_res_page = browser.find_element_by_xpath("//a[contains(@class,'hd-pagination__link') and contains(@title,'Next')]")
        next_page_link = next_res_page.get_attribute("href")
        has_next_page = True
    except:
        has_next_page = False

    try:
        for i in range(0, 3):  # for i in links:  # To add fetched product links from current Result page to 'links_list'
            links_list.append(links[i])  # links_list.append(i)
            print "Link: " + links[i]
            logging.info("Link: " + str(links[i]))

        print "Total products on this Result page: ", len(links_list)
        logging.info("Total products on this Result page: " + str(len(links_list)))
    except:
        print("Subcategory to be selected on Result page! Unable to scrape details for this product.")

###################################################################


# To fetch all reviews of the current product
def get_reviews(curr_link):
    global all_reviews, has_next_page, is_last_page, browser, kw_str

    browser.get(curr_link)  # Navigate to link
    time.sleep(5)

    try:
        # Each variable related to reviews stores an array of corresponding values from all reviews
        try:  # Element may or may not be present, hence try-except used
            prod_brand = str(browser.find_element_by_class_name("product-title__brand").text)
            if "Discontinued" in prod_brand:  # Generally prefixed to the brand, if product is discontinued
                prod_brand = prod_brand[12:]  # To extract only the brand name
                prod_brand = prod_brand.strip()  # Trims white spaces from both ends
        except:
            prod_brand = '#N/A'
        print "Product Brand: " + prod_brand
        logging.info("Product Brand: " + prod_brand)

        # Product title is always present
        prod_title = browser.find_element_by_class_name("product-title__title").text
        print "Product Title: " + prod_title
        logging.info("Product Title: " + prod_title)

        try:
            model_info = browser.find_element_by_class_name("brandModelInfo").text

            model_info = str(model_info).split("\n")[1]
            model_info = model_info[str(model_info).find("Internet #") + 10:]


        except:
            model_info = '#N/A'
        print "Model Number: " + model_info
        logging.info("Model Number: " + model_info)

        try:
            # rating_elem = browser.find_element_by_css_selector("div.BVRRRatingNormalOutOf")
            # rating_value = rating_elem.get_attribute("textContent")
            prod_rating = browser.find_element_by_xpath("//*[@itemprop='reviewRating']//*[@itemprop='ratingValue']").text
        except:
            prod_rating = '#N/A'
        print "Rating: " + prod_rating
        logging.info("Rating: " + prod_rating)

        try:
            price = browser.find_element_by_id('ajaxPrice').text
        except:
            price = '#N/A'
        print "Price: " + price
        logging.info("Price: " + price)

        try:
            prod_img_src = browser.find_element_by_id('mainImage').get_attribute("src")
        except:
            prod_img_src = "#"

        try:
            prod_descr = (browser.find_element_by_xpath("//*[@id='product-description-traditional']//div[1]").get_attribute("innerText")).encode('utf-8').strip()
        except:
            print(traceback.print_exc())
            prod_descr = "Not Available"
        print(prod_descr)

        try:  # To check if reviews are available for product
            review_text = browser.find_elements_by_class_name("BVRRReviewTextContainer")
        except:
            review_text = ''  # >>> DO NOT PUT N/A OR ANY OTHER VALUE <<< for the sake of 'if' condition below

        if len(review_text):  # Checking if reviews are available for the product, hence not appending anything if no review text found
            print "Now fetching reviews on this page..."
            logging.info("Now fetching reviews on this page...")
            is_last_page = False
            final_reviews_list = []
            while not is_last_page:  # While is_last_page is FALSE

                # Following WebElements are fetched for the current Review page only
                user_name = browser.find_elements_by_class_name("BVRRNickname")
                review_title = browser.find_elements_by_class_name("BVRRReviewTitleContainer")
                review_date = browser.find_elements_by_class_name("BVRRReviewDateContainer")
                review_rating = browser.find_elements_by_xpath(
                    "//div[@itemprop='reviewRating']//span[@itemprop='ratingValue']")
                review_text = browser.find_elements_by_xpath("//span[@class='BVRRReviewText']")  # Contains abbreviated versions of review texts (if any)

                print "Total reviews on this page: ", len(review_text)
                logging.info("Total reviews on this page: " + str(len(review_text)))

                # Reviews are ready.
                # Create a data frame for each review and append it to a main data frame
                print "Appending all the fetched reviews..."
                logging.info("Appending all the fetched reviews...")

                for i in range(0, len(review_date)):  # Loop through reviews
                    try:
                        one_review = pd.DataFrame({'siteCode': ['HD'],
                                                   'pCategory': [kw_str],
                                                   'pBrand': [prod_brand],
                                                   'pRating': [prod_rating],
                                                   'pTitle': [prod_title],
                                                   'pModel': [model_info],
                                                   'price': [price],
                                                   'pImgSrc': [prod_img_src],
                                                   'pDescr': [prod_descr],
                                                   'rUser': [user_name[i].text],
                                                   'rRating': [review_rating[i].get_attribute("innerText")],
                                                   'rTitle': [review_title[i].text],
                                                   'rDate': [review_date[i].text],
                                                   'rText': [review_text[i].get_attribute("innerText")],  # final_reviews_list[k]
                                                   'rURL': [curr_link],
                                                   'pURL': [curr_link],
                                                   'sentiScore': [' '],
                                                   'sentiment': [' '],
                                                   'trigger': [' '],
                                                   'driver': [' ']}, index=[0])

                        one_review['rDate'] = pd.to_datetime(one_review['rDate'])
                        # k += 1  # Increment index of latest fetched review
                        all_reviews = all_reviews.append(one_review)

                    except:
                        print "Error while collating this review!!!"
                        logging.info("Error while collating this review!!!")
                        print traceback.print_exc()
                        logging.info(traceback.print_exc())
                # 'for' loop for collating reviews ends here

                # FOLLOWING CODE IS WORKING FOR LOOPING THROUGH ALL REVIEW PAGES. COMMENTED OUT TEMPORARILY.
                # -------------------------------------------------------------------
                #print "Checking for more review pages..."
                #logging.info("Checking for more review pages...")
                #
                ## If next Review page is available, go to next Review page
                #if browser.find_elements_by_xpath("//span[@class='BVRRPageLink BVRRNextPage']"):  # If " > " (Next Review Page arrow) is fetched
                #    is_last_page = False
                #    # Emulate clicking it
                #    next_page_elem = browser.find_elements_by_xpath("//span[@class='BVRRPageLink BVRRPageNumber BVRRSelectedPageNumber']//following-sibling::span")
                #    for n in next_page_elem:
                #        n.click()
                #        break
                #    print "Going to next Review page..."
                #    logging.info("Going to next Review page...")
                #    time.sleep(2.5)
                #
                ## If " > " (Next Review Page arrow) is not fetched
                #else:
                #    print "No more Review pages..."
                #    logging.info("No more Review pages...")
                #    is_last_page = True
                #    break
                # --------------------------------------------------------------------------
                break
            # 'while not is_last_page' ends here

            #print "Total reviews fetched for this product: ", len(final_reviews_list)
            #logging.info("Total reviews fetched for this product: " + str(len(final_reviews_list)))

        # If no reviews available for this product, then create dummy data frame without reviews and append to main data frame
        else:
            print "No reviews available for this product..."
            logging.info("No reviews available for this product...")
            try:
                one_review = pd.DataFrame({'siteCode': ['HD'],
                                           'pCategory': [kw_str],
                                           'pBrand': [prod_brand],
                                           'pTitle': [prod_title],
                                           'pModel': [model_info],
                                           'price': [price],
                                           'pImgSrc': [prod_img_src],
                                           'pDescr': [prod_descr],
                                           'rUser': ['#N/A'],
                                           'pRating': [prod_rating],
                                            'rRating': ['#N/A'],
                                           'rTitle': ['#N/A'],
                                           'rDate': ['#N/A'],
                                           'rText': ['#N/A'],
                                           'rURL': [curr_link],
                                           'pURL': [curr_link],
                                           'sentiScore': [' '],
                                           'sentiment': [' '],
                                           'trigger': [' '],
                                           'driver': [' ']}, index=[0])
            except:
                print "Error while appending dummy review!"
                logging.info("Error while appending dummy review!")
                all_reviews = all_reviews.append(one_review)
        # 'else' of (if len(review_text)) ends here
        status_code = 200
    except:
        print "Error(!) while scraping reviews @ ", curr_link
        logging.info("Error(!) while scraping reviews @ " + curr_link)
        print traceback.print_exc()
        logging.info(traceback.print_exc())
        status_code = 500

    return status_code

###################################################################


# To scrape product information and reviews from HomeDepot
def home_depot_all_info(kw_str1):
    global all_reviews, all_kw_all_rev, next_page_link, has_next_page, all_links_list, links_list, browser, kw_str, status_code
    kw_str = kw_str1

    print 'Keyword: ', kw_str
    logging.info('Keyword: ' + kw_str)

    # chrome_path = 'C:\Python27\selenium\webdriver\chromedriver.exe'
    chrome_path = dbConfig.dict["chromeDriver"]
    browser = webdriver.Chrome(chrome_path)

    # Create main data frame to hold all product information and reviews of current keyword
    all_reviews = pd.DataFrame({'siteCode': ['HD'],
                                'pCategory': [kw_str],
                                'pBrand': [' '],
                                'pTitle': [' '],
                                'pModel': [' '],
                                'pRating': [' '],
                                'price': [' '],
                                'pImgSrc': [' '],
                                'pDescr': [' '],
                                'rUser': [' '],
                                'rRating': [' '],
                                'rTitle': [' '],
                                'rDate': [' '],
                                'rText': [' '],
                                'rURL': [' '],
                                'pURL': [' '],
                                'sentiScore': [' '],
                                'sentiment': [' '],
                                'trigger': [' '],
                                'driver': [' ']}, index=[0])

    # Creates aggregated data frame to hold all product information and reviews of all keywords
    all_kw_all_rev = pd.DataFrame({'siteCode': ['HD'],
                                   'pCategory': [kw_str],
                                   'pBrand': [' '],
                                   'pTitle': [' '],
                                   'pModel': [' '],
                                   'price': [' '],
                                   'pRating': [' '],
                                   'pImgSrc': [' '],
                                   'pDescr': [' '],
                                   'rUser': [' '],
                                   'rRating': [' '],
                                   'rTitle': [' '],
                                   'rDate': [' '],
                                   'rText': [' '],
                                   'rURL': [' '],
                                   'pURL': [' '],
                                   'sentiScore': [' '],
                                   'sentiment': [' '],
                                   'trigger': [' '],
                                   'driver': [' ']}, index=[0])

    print "Scraper started at ", datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")

    #kw_str = keywords_list[0]
    # Searches for each keyword and extracts links for each product through all product pages
    #for i in range(0, len(keywords_list)):
    print "Searching for '" + kw_str + "'..."
    logging.info("Searching for '" + kw_str + "'...")

    kw_str_encod = urllib.quote(kw_str)

    browser.get("http://www.homedepot.com/s/" + kw_str_encod + "?NCNI-5")
    time.sleep(5)

    '''
    element = browser.find_element_by_id("headerSearch")   # Search box on the site homepage
    element.send_keys(kw_str)  # Enter keyword into search box
    element.send_keys(Keys.RETURN)  # Emulate pressing Enter
    '''

    all_links_list = []  # Refresh for each product

    try:
        time.sleep(5)  # Wait till results are loaded
        x = browser.current_url
        print "On the first Results page: " + x
        #logging.info("On the first Results page: " + x)
        #print("debug0")
        pagination.append(x)
        #print("debug1")

        # Get links to products on this Result page, and link to next Result page
        link_scraper()  # Updates 'links_list' and 'next_page_link'
        #print("debug2")

        try:
            for i1 in range(len(links_list)):
                curr_link = links_list[i1]

                print "Getting product information and reviews for this product: " + curr_link
                logging.info("Getting product information and reviews for this product: " + curr_link)

                get_reviews(curr_link)
                status_code = 200
        except:
            print("...")
            status_code = 500

        # FOLLOWING CODE IS WORKING FOR LOOPING THROUGH ALL RESULT PAGES. COMMENTED OUT TEMPORARILY.
        #while has_next_page:  # While current Results page is not the last page
        #    print "Going to next Results page: " + next_page_link
        #    logging.info("Going to next Results page: " + next_page_link)
        #
        #    browser.get(next_page_link)
        #    time.sleep(4)
        #    pagination.append(next_page_link)
        #
        #    # Reset following variables for each Results page
        #    next_page_link = ''
        #    has_next_page = False
        #    all_links_list += links_list  # Emptying 'links_list' into 'all_links_list'
        #    links_list = []
        #
        #    link_scraper()  # Updates 'links_list' and 'next_page_link'
        #
        #    for i1 in range(len(links_list)):
        #        curr_link = links_list[i1]
        #
        #        print "Getting product information and reviews for this product: " + curr_link
        #        logging.info("Getting product information and reviews for this product: " + curr_link)
        #
        #        get_reviews(curr_link)
        ## 'while has_next_page' ends here

        browser.close()
    # 'try' outside 'for' for looping through products on results page ends here

    except TypeError:
        # pass
        print("TypeError handled")
    except:
        print "Inside 'except' of looping through keywords..."
        logging.info("Inside 'except' of looping through keywords...")
        status_code = 500
        print(traceback.print_exc())

    # Done scraping for current keyword
    print "Done scraping for '" + kw_str + "'..."
    logging.info("Done scraping for '" + str(kw_str) + "'...")

    print "Total Results pages traversed: ", str(len(pagination))
    logging.info("Total Results pages traversed: " + str(len(pagination)))

    #print "Total products fetched: ", len(all_links_list)
    #logging.info("Total products fetched: " + str(len(all_links_list)))

    print "Scraper finished at... ", datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p")
    logging.info("Scraper finished at... " + datetime.now().strftime("%A, %d %B %Y %I:%M:%S %p"))

    '''
    # Saving the CSV file with product information and reviews; one CSV for each product/keyword
    curr_timestamp = datetime.now().strftime("%d%B%Y_%I%M%S%p")
    temp_keyword = kw_str.replace(" ", "")
    output_file_name = 'HomeDepot_' + temp_keyword + '_' + curr_timestamp + '.csv'
    full_path = 'C:\Users\Aparna.harihara\PycharmProjects\AuScer\Outputs\HomeDepot\\' + output_file_name
    all_reviews.to_csv(full_path, index=False, encoding='utf-8')
    print "CSV file for this product saved at location: " + full_path
    logging.info("CSV file for this product saved at location: " + full_path)
    '''


    #browser.close()

    all_kw_all_rev = all_kw_all_rev.append(all_reviews)
    all_kw_all_rev['pid'] = all_kw_all_rev['pCategory'] + "_" + all_kw_all_rev['pBrand'] + "_" + all_kw_all_rev['pModel']
    all_kw_all_rev['rid'] = all_kw_all_rev['pid'] + "_" + all_kw_all_rev['rUser']
    for index, row in all_kw_all_rev.iterrows():
        row['rid'] += "_" + str(len(row['rText'].encode('utf-8').split(" "))) + "_" + str(len(row['rText']))
    print("%%%%%%%%%%%%%%%%%%%%%")
    print(all_kw_all_rev)
    print("%%%%%%%%%%%%%%%%%%%%%")

    all_prod_slice = all_kw_all_rev[['pid', 'pCategory', 'pBrand', 'pRating', 'pDescr', 'pImgSrc', 'pModel', 'pTitle', 'pURL', 'price', 'siteCode']].copy()
    all_rev_slice = all_kw_all_rev[['pid', 'rid', 'rDate', 'rRating', 'rText', 'rTitle', 'rURL', 'rUser']].copy()
    #all_rev_slice['rid'] = all_rev_slice['pid'] + "_" + all_rev_slice['rUser']

    return [all_kw_all_rev, all_prod_slice, all_rev_slice, status_code]
# #################################################################


# To fetch product information from HomeDepot at current Product page
'''
def get_prod_info(curr_link):
    global prods_info

    browser.get(curr_link)  # Navigate to link
    time.sleep(5)

    try:  # Element may or may not be present, hence try-except used
        prod_brand = str(browser.find_element_by_class_name("product-title__brand").text)
        if "Discontinued" in prod_brand:  # Generally prefixed to the brand, if product is discontinued
            prod_brand = prod_brand[12:]  # To extract only the brand name
            prod_brand = prod_brand.strip()  # Trims white spaces from both ends
    except:
        prod_brand = '#N/A'
    print "Product Brand: " + prod_brand
    logging.info("Product Brand: " + prod_brand)

    # Product title is always present
    prod_title = browser.find_element_by_class_name("product-title__title").text
    print "Product Title: " + prod_title
    logging.info("Product Title: " + prod_title)

    try:
        model_info = browser.find_element_by_class_name("brandModelInfo").text
    except:
        model_info = '#N/A'
    print "Model Number: " + model_info
    logging.info("Model Number: " + model_info)

    try:
        rating_elem = browser.find_element_by_css_selector("div.BVRRRatingNormalOutOf")
        rating_value = rating_elem.get_attribute("textContent")
    except:
        rating_value = '#N/A'
    print "Rating: " + rating_value
    logging.info("Rating: " + rating_value)

    try:
        price = browser.find_element_by_id('ajaxPrice').text
    except:
        price = '#N/A'
    print "Price: " + price
    logging.info("Price: " + price)

    try:
        # 'prod_info' contains current product's information and is appended to main data frame 'prods_info'
        prod_info = pd.DataFrame({'pBrand': [prod_brand],
                                  'pTitle': [prod_title],
                                  'pModel': [model_info],
                                  'price': [price],
                                  'rRating': [rating_value],
                                  'pURL': [curr_link]}, index=[0])
        prods_info = prods_info.append(prod_info)
        status_code = 200
    except:
        print "Error while appending product information!"
        logging.info("Error while appending product information!")
        status_code = 500
    return status_code
'''

###############################################################################################

