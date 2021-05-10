from comcrawl import IndexClient
import pandas as pd
import os
import re
from bs4 import BeautifulSoup

n_threads = 5   #amount of threads used for crawling
url_toCrawl = "edition.cnn.com/WORLD/europe/9904/*"  #URL to crawl
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

def dataframe_to_json(html_body):
    count = 0
    list_df = []    #the list which will be used to create a dataframe later

    print("Handling the crawled data...")
    for element in html_body:   #use beautiful soup to extract useful text from the crawled html formatted string 
        soup = BeautifulSoup(element, 'html.parser')
        list_df.append([soup.title.get_text(), formate_body_json(soup)])   #append title and text to the list
        count += 1    

    results = pd.DataFrame(list_df, columns=["title", "body"])  #create a dataframe from the list
    print('Amount of crawled articles: {}'.format(count))

    data = results.to_json('results.json', orient='index', indent=2) #save the formatted texts (html excluded) to a json-layout 
    print("All crawled data has been written to results.json.")
    data 

def formate_body_json(soup):
    regex = re.compile(r'[\n\r\t\/]')
    text = soup.get_text()
    text = regex.sub("", text)
    text = regex2.sub("", text)
    return text

###############################################################################

def main():
    client = IndexClient(indexes_toCrawl, verbose=False) #initialize client to crawl, change verbose to see logs
    crawl_routine(client)   #crawling
    df = pd.read_csv("results.csv") #read out the dataframe from the csv file
    html_body = df['html']
    results = dataframe_to_json(html_body)  #transform crawled data to json layout


if __name__ == "__main__":
    main()