
#      /// REQUIREMENTS ///

#   URL =  https://www.amazon.com/Best-Sellers/zgbs
#   1)  Category Description        - 
#   2)  Category URL                - 
#   3)  Product URL                 -            
#   4)  Product Description         -     
#   5)  Product Image URL           - 
#   6)  Scrapping DateTime          -           
#   7)  Stock Availability          -          
#   8)  Seller Rank                 -
#   9)  ASIN                        - 
#   10) Review URL                  -
#   11) Dimension, Weight, Item/Model number    - 
#   12) Seller/Merchant Detail      - 
#   13) Multiple Seller’s Prices    -
#   14) Merchant’s Description      -
#   15) Buy Box Seller Information  -
#   16) Brand & Manufacturer        - 
#   17) ASIN, UPC, ISBN             -
#   18) Buy Box Prices              -
#   19) Marketplace (US, UK)        -


# Importing our necessary packages
import csv
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def progress_message(message):
    print("PROGRESS MESSAGE : "+message+" ..//")

# --------------------------------------------------------------------------------------------------------------------------------------------------

def full_url(url):
    if "amazon.com" not in url:
        url = "https://amazon.com" + url
    return url

# --------------------------------------------------------------------------------------------------------------------------------------------------

def configureWebDriver():
    global driver
    progress_message("Configuring Webdriver") 
    chr_options = Options()
    chr_options.add_experimental_option("detach", True)
    chr_options.add_argument('headless')
    chr_options.add_argument('--log-level=1')
    chr_options.add_argument('--ignore-certificate-errors')
    chr_options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome("C:\\Users\\user\\.wdm\\drivers\\chromedriver\\win32\\95.0.4638.17\\chromedriver.exe",options=chr_options)
    progress_message("Webdriver configured successfully")
    return driver

# --------------------------------------------------------------------------------------------------------------------------------------------------

def replace_all(text, dic):
    for key, val in dic.items():
        text = text.replace(key, val)
    return text

# --------------------------------------------------------------------------------------------------------------------------------------------------

def printProductDetails(productDetails):
    f = open("notes.txt","a",encoding='utf-8') 
    f.write("\n{")
    for key,val in productDetails.items():
        f.write("\n\t"+key+" : "+str(val))
    f.write("\n}\n")

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getDescription(soup):
    description = soup.find("title").text
    if ":" in description:
        # replace unnecessary keywords in description
        dic = {
            "Amazon.com":"",
            "Appstore for Android":"",
            ":":"",
        }
        description = replace_all(description.strip(),dic)
    return description

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getAsin(product_url):
    asin = "No ASIN found"
    url = product_url.split("/")
    if "dp" in url:
        asin = url[url.index("dp")+1].strip()
    return asin

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getManufacturer(soup):
    manufacturer = "No details available"
    a_tag = soup.find("a",id="bylineInfo")
    if not a_tag: 
        a_tag = soup.find("a",id="brand")
    # replace unnecessary keywords in Manufacturer text
    dic = {
        "Visit the " : "",
        "Brand:" : "",
        "Store" : "",
        "by " : ""
    }
    manufacturer = replace_all(a_tag.text.strip(),dic)
    return manufacturer

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getImageUrl(soup):
    img_url = "No image found"
    img = soup.find("img",id="landingImage")
    if img:
        img_url = img.attrs['src']
    else:
        img = soup.find("img",id="js-masrw-main-image")
        if img:
            img_url = img.attrs['src'].strip()
    return img_url

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getStockAvailability(soup):
    status = "Unknown availability status"
    availability = soup.find("div",id="availability")
    if availability:
        status = availability.span.text.strip()
    else:
        availability = soup.find("div",id="mas-availability")
        if availability:
            status = availability.text.strip()
    return status

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getRating(soup,product_url):
    rating = "No ratings"
    num_ratings = "No ratings"
    div = soup.find("div",id="averageCustomerReviews")
    if div:
        span = div.find("span",class_="a-icon-alt")
        rating = span
        num_ratings = div.find("span",id="acrCustomerReviewText").text.strip().replace("ratings","")
    else:
        span = soup.find("span",class_="masrwDesktopAcr"+getAsin(product_url))
        if span:
            i_tag = span.find("i")
            rating = i_tag
            a_tag = span.find("a",class_="a-link-normal")
            num_ratings = a_tag.text.replace("customer ratings","")
    if rating and type(rating) != str:
        rating = rating.text.replace("out of 5 stars","/ 5")
    return rating, num_ratings

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getProductDetails(product_url, price="Price not Available"):
    try:
        driver.get(product_url)
        soup_obj = BeautifulSoup(driver.page_source, 'lxml')
    except:
        raise Exception("Unable to load the product page : "+product_url)

    scraping_time, dimensions, asin, manufacturer, seller_rank = [None]*5
    review_url = product_url

    # debug file 
    debug_file = open("debug.txt","a",encoding='utf-8')
    debug_file.write(product_url+"\n")
    
    # extracting basic product data 
    scraping_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    asin = getAsin(product_url)
    manufacturer = getManufacturer(soup_obj)
    description = getDescription(soup_obj)
    img_url = getImageUrl(soup_obj)
    availability = getStockAvailability(soup_obj)
    rating, num_ratings = getRating(soup_obj,product_url)

    # extracting the product technical details (dimensions, manufacturer, asin, seller rank)
    # 3 types of html element classes contain the above technical details
    classes = [
        ("table","a-keyvalue prodDetTable"),
        ("ul","a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"),
        ("table","a-bordered")
    ]
    # table_attrs store the list of all tags that contain technical attributes
    # table_vals store the list of all tags that contain information to the technical attributes
    table_attrs = []
    table_vals = []
    for ind in range(3):
        info_div = list(soup_obj.find_all(classes[ind][0],class_=classes[ind][1]))
        if info_div:
            # debug_file.write(classes[ind][1]+"\n")
            if ind!=1:
                if ind==0:
                    for div in info_div:   
                        # debug_file.write("\tdiv class -> " + str(div.attrs["class"]) + "\n")
                        attrs = list(div.find_all("th"))
                        table_attrs.extend(attrs)
                        vals = list(div.find_all("td"))
                        table_vals.extend(vals)
                else:
                    for div in info_div:   
                        if len(div.attrs["class"]) == 1:
                            rows = list(div.find_all("tr"))
                            for row in rows:
                                attr,val = row.find_all("td")
                                table_attrs.append(attr)
                                table_vals.append(val)
                for c in range(len(table_attrs)):
                    attr = table_attrs[c].text
                    val = table_vals[c]
                    if "Manufacturer" in attr or "Publisher" in attr or "Developed" in attr:
                        if not manufacturer:
                            manufacturer = val.text.strip()
                    elif "ASIN" in attr or "ISBN" in attr or "UPC" in attr:
                        if not asin:
                            asin = val.text.strip()
                    elif "Dimension" in attr or "Size" in attr:
                        if not dimensions:
                            dimensions = val.text.strip()
                    elif "Rank" in attr:
                        ranks = val.span.find_all("span")
                        rank_list = []
                        for span in ranks:
                            rank = span.text.strip()
                            if "(" in rank:
                                rank = rank[:rank.index("(")]
                            rank_list.append(rank)
                        seller_rank = ', '.join(rank_list)
            else:
                for div in info_div:
                    spans = div.find_all("span","a-list-item")
                    for span in spans:
                        span_info = span.text.split(":")
                        if len(span_info)==2:
                            attr = span_info[0]
                            val = span_info[1]
                            if "Manufacturer" in attr or "Publisher" in attr or "Developed" in attr:
                                manufacturer = val.strip()
                            elif "ASIN" in attr or "ISBN" in attr:
                                asin = val.strip()
                            elif "Dimension" in attr or "Size" in attr:
                                dimensions = val.strip()
                            elif "Rank" in attr:
                                seller_rank = val[:val.index('(')] + val[val.index(')')+1:].strip().replace("\n",", ")
    product_info = {
        'description' : description,
        'product_url' : product_url,
        'rating' : rating,
        'price' : price,
        'num_ratings' : num_ratings,
        'scraping_time' : scraping_time,
        'image_url' : img_url,
        'dimensions' : dimensions,
        'asin' : asin,
        'manufacturer' : manufacturer,
        'availability' : availability,
        'review_url' : review_url,
        'seller_rank' : seller_rank,
    }
    printProductDetails(product_info)
    return product_info

# --------------------------------------------------------------------------------------------------------------------------------------------------
    
def getProductList(category_url,current_page):
    """
        DOCSTRING ---->
        This function parses the top selling products of a particular category.
        
        Arguments : category_url (string) - url of page containing top selling products list of a particular category
                    current_page - current web page number 
        
        Returns : product_list (list of dictionaries), next_page_url(string) 
                    product_list - list of dictionaries containing the product details of a category
    """ 
    product_list = []
    driver.get(category_url)

    soup_obj = BeautifulSoup(driver.page_source, 'lxml')

    items_list = soup_obj.find_all("span",class_="aok-inline-block zg-item")
    for item in items_list:
        product_url = item.a.attrs['href']
        product_price = item.find("span",class_="a-color-price")
        if product_price:
            product_price = product_price.text.strip()
        else:
            product_price = "Not available"

        product_url = full_url(product_url)

        product_info = getProductDetails(product_url,product_price)   
        product_list.append(product_info)

    next_page = soup_obj.find("li",class_="a-normal")
    if next_page:
        if int(next_page.text) == current_page + 1:
            next_page_url = next_page.a.attrs['href'].strip()
            if "amazon.com" not in next_page_url:
                next_page_url = "https://amazon.com" + next_page_url
            product_list.extend(getProductList(next_page_url,current_page+1))
    return product_list

# --------------------------------------------------------------------------------------------------------------------------------------------------

def getHeaders(url):
    driver.get(url)
    driver.refresh()
    soup = BeautifulSoup(driver.page_source, 'lxml')

    dept_list = soup.find("ul",class_="_p13n-zg-nav-tree-all_style_zg-browse-root__-jwNv")
    dept_list = list(dept_list.find_all("li"))
    dept_list.remove(dept_list[3])
    dept_list.remove(dept_list[2])
    dept_list.remove(dept_list[0])

    return dept_list

# --------------------------------------------------------------------------------------------------------------------------------------------------

def driver_code():
    driver = configureWebDriver()
    url = "https://www.amazon.com/Best-Sellers/zgbs/"

    dept_list = getHeaders(url)

    # creating a csv file if it doesn't exist
    with open('scraped_details.csv', 'a') as fp:
        pass
    fp.close()
    # empty dataframe
    product_details_df = pd.DataFrame()

    # for every department, extract top selling products (in different pages)
    for header in dept_list[4:]:
        category = header.a.text.strip()
        category_url = header.a.attrs['href']
        
        if "amazon.com" not in category_url:
            category_url = "https://amazon.com" + header.a.attrs['href']
        
        product_list = getProductList(category_url,1)
        
        for index in range(len(product_list)):
            product_list[index]['category_title'] = category
            product_list[index]['category_url'] = category_url

        temp_df = pd.DataFrame(product_list)
        product_details_df.append(temp_df)
        product_details_df.to_csv("scraped_details.csv")    

    # sample_url = "https://www.amazon.com/Tombow-56167-Markers-10-Pack-Blendable/dp/B0044JIU2S/ref=zg_bs_arts-crafts_98?_encoding=UTF8&psc=1&refRID=CXCPRRG6YR09ZMDB2BYQ"
    # det = getProductDetails(sample_url)


driver_code()





    
