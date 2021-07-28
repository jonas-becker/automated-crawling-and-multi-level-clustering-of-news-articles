## @package pyexample
#  Documentation for the crawler of the project.
#
#  This crawler is downloading data from commoncrawl.
import pandas as pd
import re
import urllib
import urllib.request
import json
import ujson
import os.path
import warc
import boto3
import glob
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from time import time
from botocore.handlers import disable_signing
from langdetect import detect

#The websites we want to keep crawled data from.
#This list of websites should ensure a diverese politcial spectrum within the crawled news articles. The list has been taken from the POLUSA Dataset. More information can be found here: https://arxiv.org/ftp/arxiv/papers/2005/2005.14024.pdf .
TARGET_WEBSITES = [".cnn.com", ".washingtonpost.com", ".nytimes.com", ".abcnews.go.com", ".bbc.com", ".cbsnews.com", ".chicagotribune.com", ".foxnews.com", ".huffpost.com", ".latimes.com", ".nbcnews.com", ".npr.org/sections/news", ".politico.com", ".reuters.com", ".slate.com", ".theguardian.com", ".wsj.com", ".usatoday.com", ".breitbart.com", ".nypost.com", ".cbslocal.com", ".nydailynews.com", ".newsweek.com", ".boston.com", ".denverpost.com", ".seattletimes.com", ".miamiherald.com", ".observer.com", ".washingtontimes.com", ".newsday.com", ".theintercept.com"]  #these trings will be compared with the URL and if matched added to datasets. You may add a specific path you are looking for

#The urls we are asking commoncrawl to search WARC-Paths for. This is different from TARGET_WEBSITES. Also add a website to TARGET_WEBSITES if you want to keep the data.
TEST_TARGETS = [".cnn.com", ".washingtonpost.com", ".nytimes.com", ".abcnews.go.com", ".bbc.com", ".cbsnews.com", ".chicagotribune.com", ".foxnews.com", ".huffpost.com", ".latimes.com", ".nbcnews.com", ".npr.org/sections/news", ".politico.com", ".reuters.com", ".slate.com", ".theguardian.com", ".wsj.com", ".usatoday.com", ".breitbart.com", ".nypost.com", ".cbslocal.com", ".nydailynews.com", ".newsweek.com", ".boston.com", ".denverpost.com", ".seattletimes.com", ".miamiherald.com", ".observer.com", ".washingtontimes.com", ".newsday.com", ".theintercept.com"]

#These indexes define the timeframes we want to crawl data from. For further information please visit: https://index.commoncrawl.org/ .
INDEXES = ["2021-25", "2021-21", "2021-17", "2021-10", "2021-04", "2020-50", "2020-45", "2020-40", "2020-34", "2020-29", "2020-24", "2020-16", "2020-10", "2020-05", "2019-51", "2019-47", "2019-43", "2019-39", "2019-35", "2019-30", "2019-26", "2019-22", "2019-18", "2019-13", "2019-09", "2019-04"]    #The indexes from commoncrawl

MAX_ARCHIVE_FILES_PER_URL = 10   #Change to increase or decrease the amount of crawled data per URL (Estimated size per archive: 1.2 GB)

MINIMUM_MAINTEXT_LENGTH = 200   #How long an article should be in order to be processed. Shorter articles will be disgarded.

MAX_CONNECTION_RETRIES = 3  #The amount of retries to download a WARC-File if the connection fails.

START_NUMERATION_AT = 0     #Start the numeration of WARC-Files and json-files with a specific number (can be used to extend existing datasets)

DESIRED_LANGUAGE = "en"    #Set to None if all languages are desired.


def check_url_for_data(url, i):
    '''
    Check if JSON-Object is available under the URL for a specific CommonCrawl index.
    @param url: URL of TEST_TARGETS
    @param i: The CommonCrawl index
    @return: returns nothing
    '''
    try:
        with urllib.request.urlopen(f'https://index.commoncrawl.org/CC-MAIN-{i}-index?url={url}&output=json') as url:
            resp = []
            if url is not None:
                for element in url:
                    resp.append(json.loads(element))
                return resp
            else:
                return None
    except Exception as e:
        print("Could not gather data from the index: " + i + ", URL: " + url)
        print(e)

def check_urls_for_data():
    '''
    Get the archive files including their WARC-Paths for the given TEST_TARGETS.
    @return: all archive files that are fitting with the TEST_TARGETS
    '''
    all_archive_files = []
    
    for i in INDEXES:
        print("----Checking Index: " + i)
        for url in TEST_TARGETS:
            print("Checking URL for Data: " + url)
            archiveFiles = check_url_for_data(url, i)  #get the paths to all archives we may want to download

            if (archiveFiles is None):
                continue
            else:
                archiveFiles = [file for file in archiveFiles if not ("crawldiagnostics" in file["filename"] or "robotstxt" in file["filename"])]    #exclude diagnostic and robotstxt files because they do not include useful data
                all_archive_files.append(archiveFiles)

    return all_archive_files
          
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
    n_articles = 0
    url_list = []
    header_list = []
    html_content = []
    date_list = []

    for record in warc_file:
        if n_articles >= limit:
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
        n_articles += 1
    warc_file.close()
    print('Processing took %s seconds and went through %s articles' %(time() - t0, n_articles))
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
    text = re.sub(u'\s+',' ', text)  #replace more than 2 whitespaces with a single whitespace
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
        if (len(df["maintext"][i].split()) > MINIMUM_MAINTEXT_LENGTH and (df["detected_lang"][i] == DESIRED_LANGUAGE or DESIRED_LANGUAGE == None )):
            list_df.append([None, (datetime.now()).strftime("%m/%d/%Y, %H:%M:%S"), (datetime.now()).strftime("%m/%d/%Y, %H:%M:%S"), datetime.strptime(df["date"][i], "%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y, %H:%M:%S"), get_description(df["maintext"][i], 50), None, df["detected_lang"][i], None, get_domain(df["url"][i]), format_string(df["maintext"][i]), format_string(df["title"][i]), None, None, df["url"][i]])   #append title and text to the list
            count += 1    

    results = pd.DataFrame(list_df, columns=["authors", "date_download", "date_modify", "date_publish", "description", "image_url", "language", "localpath", "source_domain", "maintext", "title", "title_page", "title_rss", "url"])  #create a dataframe from the list
    print('Amount of extracted articles: {}'.format(count))

    with open(f"./crawl_json/crawl_{str(all_index+START_NUMERATION_AT)}_{str(index)}.json", 'w', encoding='utf-8') as f:
        f.write(ujson.dumps(results.to_dict('index'), indent=4, ensure_ascii=False, escape_forward_slashes=False))

    print(f"Crawled data of ./crawl_data/crawled_data_{str(all_index+START_NUMERATION_AT)+'_'+str(index)}.warc.gz has been written to ./crawl_json/crawl_{str(all_index+START_NUMERATION_AT)}_{str(index)}.json") 

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

def download_archives(warc_paths, all_index):
    '''
    Downloads the archives from the given URLs.
    @param warc_paths: The file path of the WARC-Files we want to download
    @param all_index: The index of the TEST_TARGETS
    @return: returns nothing
    '''

    for index, _ in enumerate(warc_paths):
        retries = 0
        while True:
            try:
                print("Downloading from CommonCrawl: " + warc_paths[index])
                resource = boto3.resource('s3')
                resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
                meta_data = resource.meta.client.head_object(Bucket="commoncrawl", Key=warc_paths[index])
                total_length = int(meta_data.get('ContentLength', 0))
                downloaded = 0

                def progress(chunk):    #Progress Bar
                    nonlocal downloaded
                    downloaded += chunk
                    done = int(50 * downloaded / total_length)
                    sys.stdout.write("\r[%s%s] %s MB / %s MB" % ('=' * done, ' ' * (50-done), str(round(downloaded/100000)), str(round(total_length/100000))))
                    sys.stdout.flush()

                if (os.path.isfile(f"crawl_json/crawl_{str(all_index+START_NUMERATION_AT)}_{str(index)}.json") is False):   #only download when the json isnt already processed from an earlier crawl
                    resource.meta.client.download_file('commoncrawl', warc_paths[index], f"./crawl_data/crawled_data_{str(all_index+START_NUMERATION_AT)}_{str(index)}.warc.gz", Callback=progress)
                    print("\n")
                break   #break out of while true loop when the download was successful
            except Exception as e:
                retries = retries+1
                print("\n")
                print("An error happened while trying to connect to download the WARC-File.")
                print(e)
                if retries >= MAX_CONNECTION_RETRIES:
                    break
                else:
                    pass

def get_detected_lang(text):
    '''
    Detects the language of a given text.
    @param text: The text to get the language from
    @return: The language
    '''
    try:
        lang = detect(text)
    except:
        lang = 'default'
    return lang

def delete_all_warc_files():
    '''
    Deletes all WARC-Files in the directory "./crawl_data/".
    @return: returns nothing
    '''
    files = glob.glob('./crawl_data/*')
    for f in files:
        os.remove(f)
    print("All downloaded warc files have been deleted after processing to save storage.")

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
        try:
            soup = BeautifulSoup(element, 'html.parser')
            if (len(element) != 0 and soup.title != None):
                paragraphs.append(get_paragraphs(soup))
                langs.append(get_detected_lang(paragraphs[i]))
                titles.append(soup.title.text)
            else:
                paragraphs.append("Undefined")
                langs.append("Undefined")
                titles.append("Undefined")
        except Exception as e:
            print("An error happened while gathering the maintext and title.")
            print(e)
            paragraphs.append("Undefined")
            langs.append("Undefined")
            titles.append("Undefined")
            pass
        

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

    if (len(archiveFiles) > MAX_ARCHIVE_FILES_PER_URL):
        for element in archiveFiles[:MAX_ARCHIVE_FILES_PER_URL]:
            warc_paths.append(element["filename"])
    else:
        for element in archiveFiles:
            warc_paths.append(element["filename"])

    print("\nAdded " + str(len(warc_paths)) + " archives to download.")
    return warc_paths



################################################################################################################

def main():

    all_archiveFiles = check_urls_for_data()
    for all_index, archiveFiles in enumerate(all_archiveFiles):
        warc_paths = get_warc_paths(archiveFiles)
        print(warc_paths)
        download_archives(warc_paths, all_index)

        for index, _ in enumerate(warc_paths):
            if (os.path.isfile(f"crawl_json/crawl_{str(all_index+START_NUMERATION_AT)}_{str(index)}.json") is False):
                print(f"Processing ./crawl_data/crawled_data_{str(all_index+START_NUMERATION_AT)}_{str(index)}.warc.gz...")
                df = process_warc(f"./crawl_data/crawled_data_{str(all_index+START_NUMERATION_AT)}_{str(index)}.warc.gz", TARGET_WEBSITES, limit = 100000)
                df = get_maintext_and_title(df)
                #pd.DataFrame(df).to_csv(f"./crawl_csv/crawl_{str(all_index)}_{str(index)}.csv")
                dataframe_to_json(df,all_index, index)  #transform crawled data to json layout
            else:
                print(f"Skipped processing of crawled_data_{str(all_index+START_NUMERATION_AT)}_{str(index)}.warc.gz because there already exists a corresponding json file.")
        delete_all_warc_files() #delete warc files that are not needed anymore to save storage

if __name__ == '__main__':
    main()