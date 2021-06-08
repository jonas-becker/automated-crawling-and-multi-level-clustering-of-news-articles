"""@package docstring
"""
from numpy import tile
import pandas as pd
import re
import urllib
from urllib.parse import urlparse
import urllib.request
import json
import ujson
from bs4 import BeautifulSoup
from datetime import datetime
from time import time
import os.path
import warc
import boto3
from botocore.handlers import disable_signing
from io import BytesIO
from langdetect import detect

TARGET_WEBSITES = [".cnn.com", ".washingtonpost.com", ".nytimes.com", ".abcnews.go.com", ".bbc.com", ".cbsnews.com", ".chicagotribune.com", ".foxnews.com", ".huffpost.com", ".latimes.com", ".nbcnews.com", ".npr.org/sections/news", ".politico.com", ".reuters.com", ".slate.com", ".theguardian.com", ".wsj.com", ".usatoday.com", ".breitbart.com", ".nypost.com", ".cbslocal.com", ".nydailynews.com", ".newsweek.com", ".boston.com", ".denverpost.com", ".seattletimes.com", ".miamiherald.com", ".observer.com", ".washingtontimes.com", ".newsday.com", ".theintercept.com"]  #these trings will be compared with the URL and if matched added to datasets. You may add a specific path you are looking for
TEST_TARGETS = ["cnn.com", "washingtonpost.com"]
INDEX = '2020-16'
MAX_ARCHIVE_FILES_PER_URL = 1   #change to increase or decrease the amount of crawled data per URL (Estimated size per archive: 1.2 GB)


def check_url_for_data(url):
    '''
    Check if JSON-Object is available under the URL.
    @param url: URL of TEST_TARGETS
    @return: returns nothing
    '''
    try:
        with urllib.request.urlopen('https://index.commoncrawl.org/CC-MAIN-'+ INDEX +'-index?url='+url+'&output=json') as url:
            resp = []
            for element in url:
                resp.append(json.loads(element))
            return resp
    except Exception as e:
        print(e)

def get_language(html):
    '''
    Get language from HTML-body
    @param html:
    @return: Returns the language
    '''
    soup = BeautifulSoup(html, 'html.parser')
    lang = soup.html['lang']
    if lang is None:
        return 'default'
    else:
        return lang
          
def process_warc(file_name, target_websites, limit=1000):    #unpack the gz and process it
    '''
    Extracts Data from WARC-File and writes it into a Dataframe.
    @param file_name: Name of WARC-File
    @param target_websites: The websites that are worth saving to us
    @param limit: The maximum amount of articles extracted from the WARC-File
    @return: returns Dataframe
    '''
    warc_file = warc.open(file_name, 'rb')
    t0 = time()
    n_documents = 0
    url_list = []
    header_list = []
    html_content = []
    date_list = []

    for record in warc_file:
        #print(record['WARC-Date'])

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
                        date_list.append(record['WARC-Date'])
                        print("Found matching data for " + url)
                df = pd.DataFrame(list(zip(html_content, header_list, url_list, date_list)), columns = ['maintext','header','url','date'])
            except Exception as e:
                print(e)
                continue
        n_documents += 1
    warc_file.close()
    print('Parsing took %s seconds and went through %s documents' %(time() - t0, n_documents))
    return df

def format_string(text):    #mix the soup until it has a nice taste
    '''
    Filters special characters and replaces them.
    @param text: to format text
    @return: returns formatted text
    '''
    regex = re.compile(r'[\n\r\t\"]')
    text = regex.sub("", text)  #remove special characters
    text = re.sub(u'(\u2018|\u2019)', "'", text)
    text = re.sub(u'(\u00fa|\u00ed|\u00e9|\u00f1|\u201c|\u00e1|\u00f3|\u4e0b|\u8f7d|\u9644|\u4ef6|\u00a9|\u00bd|\u00bc|\u2014|\u0005|\u0007|\u0006|\u4fdd|\u5b58|\u5230|\u76f8|\u518c|\u201d|\u00e8|\u00e0)', "", text)
    text = re.sub(u'\/', '/', text)
    text = re.sub(u'\s+',' ', text)  #replace more than 2 whitespaces with a single whitespaces
    return text

def format_url(text):
    #unfinished
    return text

def get_domain(text):
    '''
    Extract the domain from a given URL.
    @param text: The text url to get the domain from
    @return: the extracted domain 
    '''
    domain = urlparse(text).netloc
    return domain

def get_description(text, wordCount):
    '''
    Get the description for a specific article maintext.
    @param text: The text to extract the description from
    @param wordCount: The maximum amount of words a description should contain
    @return: the extracted description
    '''
    desc = ' '.join(text.split()[:wordCount])
    if (len(desc) < 5):
        desc = None
    else:
        desc = format_string(desc)
    return desc
    

def dataframe_to_json(df, all_index, index):
    '''
    Pushes all data from the dataframe into a JSON-Layout.
    @param df: Dataframe
    @param all_index: The index of the crawled test targets
    @param index: The index of the crawled WARC-File per test target
    @return: returns nothing
    '''
    count = 0
    list_df = []    #the list which will be used to create a dataframe later

    print("Handling the crawled data...")
    for i, _ in df.iterrows() :   #use beautiful soup to extract useful text from the crawled html formatted string 
        if (len(df["maintext"][i].split()) > 100):
            list_df.append([None, (datetime.now()).strftime("%m/%d/%Y, %H:%M:%S"), (datetime.now()).strftime("%m/%d/%Y, %H:%M:%S"), df["date"][i], get_description(df["maintext"][i], 50), None, df["detected_lang"][i], None, get_domain(df["url"][i]), format_string(df["maintext"][i]), format_string(df["title"][i]), None, None, df["url"][i]])   #append title and text to the list
            count += 1    

    results = pd.DataFrame(list_df, columns=["authors", "date_download", "date_modify", "date_publish", "description", "image_url", "language", "localpath", "source_domain", "maintext", "title", "title_page", "title_rss", "url"])  #create a dataframe from the list
    print('Amount of crawled articles: {}'.format(count))

    #results.to_json("./crawl_json/crawl_"+str(all_index)+'_'+str(index)+".json", orient='index', indent=2, date_format='iso') #save the formatted texts (html excluded) to a json-layout 
    with open(f"./crawl_json/crawl_{str(all_index)}_{str(index)}.json", 'w', encoding='utf-8') as f:
        f.write(ujson.dumps(results.to_dict('index'), indent=4, ensure_ascii=False, escape_forward_slashes=False))

    print("Crawled data of ./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz has been written to ./crawl_json/crawl_"+str(all_index)+'_'+str(index)+".json") 

def get_paragraphs(soup):
    '''
    Extracts all paragraphs of a soup object
    @param soup: Soup-object
    @return: Returns all paragraphs except the last one because it is useless
    '''
    result = ""
    for para in soup.find_all("p"):
        result += para.get_text() + " "
    return result[:-1]

def check_urls_for_data():
    '''
    Get the archive files including their WARC-Paths for the given TEST_TARGETS.
    @return: all archive files that are fitting with the TEST_TARGETS
    '''
    all_archive_files = []
    
    for url in TEST_TARGETS:
        archiveFiles = check_url_for_data(url)  #get the paths to all archives we may want to download
        archiveFiles = [file for file in archiveFiles if not "crawldiagnostics" in file["filename"]]    #exclude diagnostic files because they do not include useful data
        all_archive_files.append(archiveFiles)
    return all_archive_files

def download_archives(warc_paths, all_index):
    '''
    Downloads the archives from the given URLs.
    @param warc_paths: The file path of the WARC-Files we want to download
    @param all_index: The index of the TEST_TARGETS
    @return: returns nothing
    '''
    for index, _ in enumerate(warc_paths):
        print("Downloading from CommonCrawl: " + warc_paths[index])
        resource = boto3.resource('s3')
        resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
        bucket = resource.Bucket('commoncrawl')
        if os.path.isfile("crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz") is False: 
            resource.meta.client.download_file('commoncrawl', warc_paths[index], "./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz")

def get_detected_lang(text):
    try:
        lang = detect(text)
    except:
        lang = 'default'
    return lang

def get_maintext_and_title(df):
    '''
    Extract the maintext (body) and the title of the articles.
    @param df: Dataframe
    @return: The dataframe with extracted maintext and title
    '''
    paragraphs = []
    titles = []
    langs = []

    for i, element in enumerate(df["maintext"]): 
        soup = BeautifulSoup(element, 'html.parser')
        if (len(element) != 0 and soup.title != None):
            paragraphs.append(get_paragraphs(soup))
            langs.append(get_detected_lang(paragraphs[i]))
            titles.append(soup.title.text)

    df["maintext"] = paragraphs
    df["title"] = titles
    df['detected_lang']  = langs
    return df

def get_warc_paths(archiveFiles):
    '''
    Get a specific amount of WARC-Paths from each archive.
    @param archiveFiles: The archive files where all WARC-Files are listed in
    @return: The file paths of the WARC-Files we want to download
    '''
    warc_paths = []

    for element in archiveFiles[:MAX_ARCHIVE_FILES_PER_URL]:
        warc_paths.append(element["filename"])

    print("\nAdded " + str(len(warc_paths)) + " archives to download.")
    return warc_paths

################################################################################################################

def main():
    all_archiveFiles = check_urls_for_data()
    for all_index, archiveFiles in enumerate(all_archiveFiles):
        warc_paths = get_warc_paths(archiveFiles)
        download_archives(warc_paths, all_index)

        for index, _ in enumerate(warc_paths):
            print("Processing ./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz...")
            df = process_warc("./crawl_data/crawled_data_"+str(all_index)+'_'+str(index)+".warc.gz", TARGET_WEBSITES, limit = 100000)
            df = get_maintext_and_title(df)
            pd.DataFrame(df).to_csv("./crawl_csv/crawl_"+str(all_index)+'_'+str(index)+".csv")
            results = dataframe_to_json(df,all_index, index)  #transform crawled data to json layout

if __name__ == '__main__':
    main()