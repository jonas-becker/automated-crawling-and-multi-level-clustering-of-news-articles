#from bs4.builder import HTML_5
#from comcrawl import IndexClient
import pandas as pd
import urllib.request
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
from time import time
import warc
import boto3
from botocore.handlers import disable_signing
from io import BytesIO

TARGET_WEBSITES = ["cnn.com", "washingtonpost.com", "nytimes.com", "abcnews.go.com", "bbc.com", "cbsnews.com", "chicagotribune.com", "foxnews.com", "huffpost.com", "latimes.com", "nbcnews.com", "npr.org/sections/news", "politico.com", "reuters.com", "slate.com", "theguardian.com", "wsj.com", "usatoday.com"]  #these trings will be compared with the URL and if matched added to datasets. You may add a specific path you are looking for
TEST_TARGETS = ["cnn.com", "washingtonpost.com"]
INDEX = '2020-16'
MAX_ARCHIVE_FILES_PER_URL = 6   #change to increase or decrease the amount of crawled data per URL (Estimated size per archive: 1.2 GB)

def check_url_for_data(url):
    try:
        with urllib.request.urlopen('https://index.commoncrawl.org/CC-MAIN-'+ INDEX +'-index?url='+url+'&output=json') as url:
            resp = []
            for element in url:
                resp.append(json.loads(element))
            return resp
    except Exception as e:
        print(e)
        
def process_warc(file_name, target_websites, limit=1000):    #unpack the gz and process it
    warc_file = warc.open(file_name, 'rb')
    t0 = time()
    n_documents = 0
    url_list = []
    header_list = []
    html_content = []

    for record in warc_file:
        if n_documents >= limit:
            break
        url = record.url
        payload = record.payload.read()
        try:
            header, html = payload.split(b'\r\n\r\n', maxsplit=1)
            html = html.strip()
        except:
            continue
        if url is None or payload is None or html == b'':
            continue
        else:
            try:
                for i in target_websites:
                    if i in url:
                        html_content.append(html)
                        header_list.append(header)
                        url_list.append(url)
                        print("Found matching data for " + url)
                df = pd.DataFrame(list(zip(html_content, header_list, url_list)), columns = ['maintext','header','url'])
            except Exception as e:
                print(e)
                continue
        n_documents += 1
    warc_file.close()
    print('Parsing took %s seconds and went through %s documents' %(time() - t0, n_documents))
    return df

def formate_maintext_for_json(soup):    #mix the soup until it has a nice taste
    regex = re.compile(r'[\n\r\t\"]')
    text = soup.find_all('p')
    result = ''
    for element in text:
        element = element.get_text()
        element = regex.sub("", element)  #remove special characters
        element = re.sub(u'(\u2018|\u2019)', "'", element)
        element = re.sub(u'\/', '/', element)
        element = re.sub(u'\s+',' ', element)  #replace more than 2 whitespaces with a single whitespaces
        result += str(element) + ' '
    return result

def write_results_in_file(element):
    with open('souptxt.txt', 'w') as f:
        f.write(element.to_string())

def dataframe_to_json(df, all_index, index):
    count = 0
    list_df = []    #the list which will be used to create a dataframe later

    print("Handling the crawled data...")
    for i, element in df.iterrows() :   #use beautiful soup to extract useful text from the crawled html formatted string 
        list_df.append([None, datetime.now(), None, None, None, None, None, None, None, df["maintext"][i], "Placeholder title", None, None, df["url"][i]])   #append title and text to the list
        count += 1    

    results = pd.DataFrame(list_df, columns=["authors", "date_download", "date_modify", "date_publish", "description", "image_url", "language", "localpath", "source_domain", "maintext", "title", "title_page", "title_rss", "url"])  #create a dataframe from the list
    print('Amount of crawled articles: {}'.format(count))

    data = results.to_json("./crawl_json/crawl_"+str(all_index)+'_'+str(index)+".json", orient='index', indent=2, date_format='iso') #save the formatted texts (html excluded) to a json-layout 
    
    print("Crawled data of ./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz has been written to ./crawl_json/crawl_"+str(all_index)+'_'+str(index)+".json") 

def get_paragraphs(response):
    soup = BeautifulSoup(response, 'html.parser')
    result = ""
    for para in soup.find_all("p"):
        result += para.get_text() + " "
    return result[:-1]

def check_urls_for_data():
    all_archive_files = []
    
    for url in TEST_TARGETS:
        archiveFiles = check_url_for_data(url)  #get the paths to all archives we may want to download
        archiveFiles = [file for file in archiveFiles if not "crawldiagnostics" in file["filename"]]    #exclude diagnostic files because they do not include useful data
        all_archive_files.append(archiveFiles)
    return all_archive_files

################################################################################################################

def main():
    all_archiveFiles = check_urls_for_data()
    for all_index, archiveFiles in enumerate(all_archiveFiles):
        warc_paths = []
        for element in archiveFiles[:MAX_ARCHIVE_FILES_PER_URL]:
            warc_paths.append(element["filename"])

        print("\nAdded " + str(len(warc_paths)) + " archives to download.")

        for index, element in enumerate(warc_paths):
            print("Downloading from CommonCrawl: " + warc_paths[index])
            resource = boto3.resource('s3')
            resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
            bucket = resource.Bucket('commoncrawl')
            resource.meta.client.download_file('commoncrawl', warc_paths[index], "./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz")
        

        for index, elem in enumerate(warc_paths):
            print("Processing ./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz...")
            df = process_warc("./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz", TARGET_WEBSITES, limit = 100000)
            paragraphs = []

            for element in df["maintext"]:
                if (len(element) != 0):
                    paragraphs.append(get_paragraphs(element))

            df["maintext"] = paragraphs
            pd.DataFrame(df).to_csv("./crawl_csv/crawl_"+str(all_index)+'_'+str(index)+".csv")

            results = dataframe_to_json(df,all_index, index)  #transform crawled data to json layout

if __name__ == '__main__':
    main()