from bs4.builder import HTML_5
from comcrawl import IndexClient
import pandas as pd
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

n_threads = 5   #amount of threads used for crawling
url_toCrawl = "edition.cnn.com/WORLD/europe/9904/*"  #URL to crawl      TESTING: edition.cnn.com/WORLD/europe/9904/*
indexes_toCrawl = ["2019-47"]  #indexes to crawl from CommonCrawl

def crawl_routine(client):
    if not os.path.isfile('results.csv'):
        print("Crawling all data for the URL {} and the indexes {}...".format(url_toCrawl, indexes_toCrawl))
        client.search(url_toCrawl, threads=n_threads)  #specifiy crawling attributes (you may enter a keyword)
        client.results = (pd.DataFrame(client.results)      #create a pandas dataframe which is sorted by timestamp. duplicates are excluded
                        .sort_values(by="timestamp")
                        .drop_duplicates("urlkey", keep="last")
                        .to_dict("records"))
        client.download(threads=n_threads)  #start crawling

        pd.DataFrame(client.results).to_csv("results.csv")  #save the crawled dataframe to a csv file
    else:
        print("There already exists a results.csv file. Skipping crawling.")

def dataframe_to_json(df):
    count = 0
    list_df = []    #the list which will be used to create a dataframe later

    print("Handling the crawled data...")
    for index, element in df.iterrows() :   #use beautiful soup to extract useful text from the crawled html formatted string 
        soupHtml = BeautifulSoup(element['html'], 'html.parser')
        url = element['url']
        timestamp = pd.to_datetime(element['timestamp'])
        lang = element['languages']
        with open('souptxt.txt', 'w') as f:
            f.write(element.to_string())
        list_df.append([None, datetime.now(), None, timestamp, None, None, lang, None, None, formate_maintext_json(soupHtml), soupHtml.title.get_text(), None, None, url])   #append title and text to the list
        count += 1    

    results = pd.DataFrame(list_df, columns=["authors", "date_download", "date_modify", "date_publish", "description", "image_url", "language", "localpath", "source_domain", "maintext", "title", "title_page", "title_rss", "url"])  #create a dataframe from the list
    print('Amount of crawled articles: {}'.format(count))

    data = results.to_json('results.json', orient='index', indent=2, date_format='iso') #save the formatted texts (html excluded) to a json-layout 
    
    print("All crawled data has been written to results.json.")
    data 

def formate_maintext_json(soup):    #mix the soup until it has a nice taste
    regex = re.compile(r'[\n\r\t\"\/]')
    text = soup.find_all('p')
    result = ''
    for element in text:
        element = element.get_text()
        element = regex.sub("", element)  #remove special characters
        element = re.sub(u'(\u2018|\u2019)', "'", element)
        element = re.sub('\s+',' ', element)  #replace more than 2 whitespaces with a single whitespaces
        result += str(element) + ' '
    return result

###############################################################################

def main():
    client = IndexClient(indexes_toCrawl, verbose=False) #initialize client to crawl, change verbose to see logs
    crawl_routine(client)   #crawling
    df = pd.read_csv("results.csv") #read out the dataframe from the csv file
    results = dataframe_to_json(df)  #transform crawled data to json layout

if __name__ == "__main__":
    main()