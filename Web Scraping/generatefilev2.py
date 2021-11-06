import requests
from bs4 import BeautifulSoup
import pandas as pd
url ="https://www.amazon.com/Best-Sellers/zgbs"
HEADERS ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
response = requests.get(url, headers=HEADERS)
print(response)
response.text[:500]

with open("bestseller.html","w",encoding="utf-8") as f:
    f.write(response.text)
with open("bestseller.html","r") as f:
    html_content = f.read()
    
content = BeautifulSoup(html_content,"html.parser")
type(content)

doc = content.find("ul",{"id":"CardInstancevQ8Dv1I8_T-UZ-eKQxA_Fw"})
hearder_link_tags = doc.find_all("li")
############## find and get different item categories description and Url at any department 
topics_link = []
for tag in hearder_link_tags[1:]:
#     print(tag)
        topics_link.append({
        "title": tag.text.strip(),
        "url": tag.find("a")["href"] })
# print(topics_link)

#################store in dictionary
table_topics = { k:[ d.get(k) for d in topics_link]
                   for k in set().union(*topics_link)}
table_topics
len(table_topics["url"])

import time 
import numpy as np

def fetch(url):
    ''' The function take url and headers to download and parse the page using request.get and BeautifulSoup library
    it return a parent tag of typeBeautifulSoup object
    Argument:
    -url(string): web page url to be downloaded and parse
    Return:
    -doc(Beautiful 0bject): it's the parent tag containing the information that we need parsed from the page'''

    HEADERS= {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    response = requests.get(url,headers= HEADERS)
    
    if response.status_code != 200:
        print("Status code:", response.status_code)
        raise Exception("Failed to link to web page " + url)
    
    page_content  = BeautifulSoup(response.text,"html.parser")
    doc = page_content.findAll('div', attrs={'class':'a-section a-spacing-none aok-relative'})
    return doc


def parse_page(table_topics,pageNo):
    """The function take all topic categories and number of page to parse for each topic as input, apply get request to download each
    page, the use Beautifulsoup to parse the page. the function output are article_tags list containing all pages content, t_description
    list containing correspponding topic or categories then an url list for corresponding Url.
    Argument:
    -table_topics(dict): dictionary containing topic description and url
    -pageNo(int): number of page to parse per topic
    Return:
    -article_tags(list): list containing successfully parsed pages content where each index is a Beautifulsoup type
    -t_description(list): list containing  successfully parsed topic description
    -t_url(list): list containing successfully parsed page topic url
    -fail_tags(list): list containing pages url that failed first parsing 
    -failed_topic(list): list contaning pages topic description that failed first parsing
    """
    article_tags,t_description, t_url,fail_tags,failed_topic =[],[],[],[],[]
    for i in range(0,len(table_topics["url"])):
         # take the url
        topic_url = table_topics["url"][i]
        topics_description =  table_topics["title"][i]
        try:
            for j in range(1,pageNo+1):
                ref = topic_url.find("ref")
                url = topic_url[:ref]+"ref=zg_bs_pg_"+str(j)+"?_encoding=UTF8&pg="+str(j)
                time.sleep(10)
                #use resquest to obtain HMTL page content   +str(pageNo)+
                doc = fetch(url)
                if len(doc)==0:
                    print("failed to parse page{}".format(url))
                    fail_tags.append(url)
                    failed_topic.append(topics_description)
                else:
                    print("Sucsessfully parse:",url)
                    article_tags.append(doc)
                    t_description.append(topics_description)
                    t_url.append(topic_url) 
        except Exception as e:
            print(e)
    return article_tags,t_description,t_url,fail_tags,failed_topic


def reparse_failed_page(fail_page_url,failed_topic):
    """The function take topic categories url, and description that failed to be accessible due to captcha in the first parsing process,
     try to fetch and parse thoses page for a second time.
     the function return article_tags list containing all pages content, topic_description,topic_url and other pages url and topic that failed to load content again
    Argument:
    -fail_page_url(dict): list containing failed first parsing web page url 
    -failed_topic(int): list contaning failed first parsing ictionary containing topic description and url
    Return:
    -article_tags2(list): list containing successfully parsed pages content where each index is a Beautifulsoup type
    -t_description(list): list containing  successfully parsed topic description
    -t_url(list): list containing successfully parsed page topic url
    -fail_p(list): list containing pages url that failed again 
    -fail_t(list): list contaning pages topic description that failed gain 
    """
    print("check if there is any failed pages,then print number:",len(fail_page_url))
    article_tag2, topic_url, topic_d, fail_p, fail_t = [],[],[],[],[]
    try:
        for i in range(len(fail_page_url)):
            time.sleep(20)
            doc = fetch(url)
            if len(doc)==0:
                print("page{}failed again".format(fail_page_url[i]))
                fail_p.append(fail_page_url[i])
                fail_t.append(failed_topic[i])
            else:
                article_tag2.append(doc)
                topic_url.append(fail_page_url[i])
                topic_d.append(failed_topic[i])
    except Exception as e:
        print(e)
    return article_tag2,topic_d,topic_url,fail_p,fail_t

    
def parse(table_topics,pageNo):
    """The function take table_topics, and number of page to parse for ecah topic url,the main purpose of this funtion is 
     to realize a double attempt to parse maximum number of pages it can .It's a combination of result getting from first 
     and second parse.
     Argument
     -table_topics(dict): dictionary containing topic description and url
     -pageNo(int): number of page to parse per topic
     Return:
     -all_arcticle_tag(list): list containing all successfully parsed pages content where each index is a Beautifulsoup type
     -all_topics_description(list): list containing  all successfully parsed topic description
     -all_topics_url(list): list containing all successfully parsed page topic url
    """
    article_tags,t_description,t_url,fail_tags,failed_topic = parse_page(table_topics,pageNo)
    if len(fail_tags)!=0:
        article_tags2,t_description2,t_url2,fail_tags2,failed_topic2 = reparse_failed_page(fail_tags,failed_topic)
        all_arcticle_tag = [*article_tags,*article_tags2]
        all_topics_description = [*t_description,*t_description2]
        all_topics_url = [*t_url,*t_url2]
        #return all_arcticle_tag,all_topics_description,all_topics_url
    else:
        print("successfully parsed all pages")
        all_arcticle_tag =   article_tags
        all_topics_description =t_description
        all_topics_url = t_url
       # return article_tags,t_description,t_url,fail_tags,failed_topic
    return all_arcticle_tag,all_topics_description,all_topics_url


all_arcticle_tag,all_topics_description,all_topics_url = parse(table_topics,2)
len(all_arcticle_tag)


def get_topic_url_item_description(doc,topic_description,topic_url):
    """The funtion takes a parent tag attribute, topic description and topic url as input, after finding the item name tags,
    the function return the item name(description), his corresponding topic(category) and his category url
    Argument:
    -doc(BeautifulSoup element): parents tag
    -topic_description(string): topic name or category
    -topic_url(string): topic url
    Return:
    -item_description(string): item name
    -topic_description(string):corresponding topic
    - topic_url(string): corresponding topic url"""
    name = doc.find("span", attrs={'class':'zg-text-center-align'})
    try:
        item_description = name.find_all('img', alt=True)[0]["alt"]
    except:
        item_description = ''
    return item_description,topic_description,topic_url 


def get_item_price(d):
    """The function take a parent tag attribute as input and find for corresponding child tag(item price),
    then return maximum price and minimum price for corresponding item and 0 when no price is found
    Argument:
    -d(BeautifulSoup element): parent tag
    Return:
    -min_price(float): item minimum price
    -max_price(float): item maximum price
    """
    p = d.find("span",attrs={"class":"a-size-base a-color-price"})
    try :
        if "-" in p.text :
            min_price = float(((p.text).split("-")[0]).replace("$",""))
            max_price = float((((p.text).split("-")[1]).replace(",","")).replace("$",""))
        else :
            min_price = float(((p.text[:5]).replace(",","")).strip().replace("$",""))
            max_price = 0.0
    except:
        min_price = 0.0
        max_price = 0.0
    return min_price,max_price


def get_item_rate(d):
    """The function take a parent tag attribute as input and find for corresponding child tag(rate),
    then return item rating out of 5, and 0.0 when can't find a rate
    Argument:
    -d(BeautifulSoup element): parent tag
    Return:
    -rating(float): item rating out or 5
    """
    rate = d.find("span",attrs={"class":"a-icon-alt"})
    try :
        rating = float(rate.text[:3])
    except:
        rating = 0.0
    return rating


def get_item_review(d):
    """The function take a parent tag attribute as input and find for corresponding child tag(costumers review),
    then return item review, and 0 when can't find number  of review
    Argument:
    -d(BeautifulSoup element): parent tag
    Return:
    -review(float): item costumer review
    """
    review = d.find("a",attrs ={"class":"a-size-small a-link-normal"})
    try :
        review = int((review.text).replace(",",""))
    except:
        review = 0
    return review


def get_item_img_url(d):
    """The function take a parent tag attribute as input and find for corresponding child tag(image),
    then return item image url, and 'no image' if can't find an image
    -d(BeautifulSoup element): parent tag
    Return:
    -img(float): item image url
    """
    image = d.findAll("img", src = True)
    try:
        img = image[0]["src"]
    except:
        img = 'No image'
    return img


def get_item_url(d):
    link_url = d.findAll("a", href = True)
    try:
        link_url = a['href']
    except:
        link_url = 'No URL'
    return link_url


def get_info(article_tags,t_description,t_url):
    """The function take a list of pages content which each index is a Beautiful element that will be use to find parent tag,list of topic description and  topic url then
     the return a dictionary made of list of each item information data such as: his corresponding topic, the topic url,
     the item description, minimum price(maximum price if exist), item rating, costumer review, and item image url
    Argument:
    -article_tags(list): list containing all pages content where each index is a Beautifulsoup type
    -t_description(list): list containing  topic description
    -t_url(list): list containing topic url
    Return:
    -dictionary(dict): dictionary containing all item information data taken from each parse page topic
    """
    import datetime
    topic_description, topics_url, item, item_img_url, product_url = [],[],[],[],[]
    minimum_price, maximum_price, rating, costuomer_review, data_date_time = [],[],[],[],[]
    for idx in range(0,len(article_tags)):
        doc = article_tags[idx]#.findAll('div', attrs={'class':'a-section a-spacing-none aok-relative'})
        for d in doc :
            names,topic_name,topic_url = get_topic_url_item_description(d,t_description[idx],t_url[idx])
            min_price,max_price = get_item_price(d)
            rate = get_item_rate(d)
            review = get_item_review(d)
            img_url = get_item_img_url(d)
            data_dt = datetime.datetime.now()
            item_url = get_item_url(d)
            ####put each item data inside corresponding list
            item.append(names)
            topic_description.append(topic_name)
            topics_url.append(topic_url)
            minimum_price.append(min_price)
            maximum_price.append(max_price)
            rating.append(rate)
            costuomer_review.append(review)
            item_img_url.append(img_url)
            data_date_time.append(data_dt)
            product_url.append(item_url)
    return {
           "Topic": topic_description,
           "Topic_url": topics_url,
           "Item_description": item,
           "Rating out of 5": rating,
           "Minimum_price": minimum_price,
           "Maximum_price": maximum_price,
           "Review" :costuomer_review,
           "Item Image Url" : item_img_url,
           "Import DateTime" : data_date_time,
           "Item Url" : product_url}


data = get_info(all_arcticle_tag,all_topics_description,all_topics_url)
dataframe = pd.DataFrame(data)
dataframe
dataframe.shape
dataframe.to_csv('AmazonBestSeller.csv', index=None)