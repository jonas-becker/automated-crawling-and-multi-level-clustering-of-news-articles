file_name = './test.warc.gz'
import boto3
from botocore.handlers import disable_signing
import requests
import gzip
from bs4.builder import HTML_5
from comcrawl import IndexClient
import pandas as pd
import os
import urllib
import re
import json
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
from time import time
import warc
from io import BytesIO

def process_warc(file_name, limit=1000):    #unpack the gz and process it
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
                html_content.append(html)
                header_list.append(header)
                url_list.append(url)
            except Exception as e:
                print(e)
                continue
        n_documents += 1
    pd.DataFrame(warc_file).to_csv("results.csv")  #save the crawled dataframe to a csv file
    warc_file.close()
    print('Parsing took %s seconds and went through %s documents' %(time() - t0, n_documents))
    return header_list, html_content, url_list
    

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

def dataframe_to_json(df):
    count = 0
    list_df = []    #the list which will be used to create a dataframe later

    print("Handling the crawled data...")
    for index, element in df.iterrows() :   #use beautiful soup to extract useful text from the crawled html formatted string 
        soupHtml = BeautifulSoup(element, 'html.parser')
        write_results_in_file(element)
        list_df.append([None, datetime.now(), None, None, None, None, None, None, None, formate_maintext_for_json(soupHtml), None, None, None, None])   #append title and text to the list
        count += 1    

    results = pd.DataFrame(list_df, columns=["authors", "date_download", "date_modify", "date_publish", "description", "image_url", "language", "localpath", "source_domain", "maintext", "title", "title_page", "title_rss", "url"])  #create a dataframe from the list
    print('Amount of crawled articles: {}'.format(count))

    data = results.to_json('results.json', orient='index', indent=2, date_format='iso') #save the formatted texts (html excluded) to a json-layout 
    
    print("All crawled data has been written to results.json.") 


url = 'https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2020-16/warc.paths.gz'
warc_path = 'crawl-data/CC-MAIN-2020-16/segments/1585370490497.6/warc/CC-MAIN-20200328074047-20200328104047-00000.warc.gz'
r = requests.get(url)
print("Downloading from CommonCrawl...")
compressed_file = BytesIO(r.content)
f = gzip.GzipFile(fileobj=compressed_file)
print(f.read(326).decode("utf-8"))

resource = boto3.resource('s3')
resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
bucket = resource.Bucket('commoncrawl')
resource.meta.client.download_file('commoncrawl', warc_path, file_name)


print("Unpacking the warc.gz...")
with gzip.open('test.warc.gz', 'rb') as f_in:   #unpacks the warc.gz
    with open('test.warc', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


file_name = 'test.warc'
#header_list, html_content, url_list = process_warc("test.warc.gz", limit = 1000)

df = pd.read_csv("results.csv") #read out the dataframe from the csv file
results = dataframe_to_json(df)  #transform crawled data to json layout

