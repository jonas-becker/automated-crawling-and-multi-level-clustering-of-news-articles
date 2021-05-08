from comcrawl import IndexClient
import pandas as pd
import os
from bs4 import BeautifulSoup

n_threads = 5   #amount of threads used for crawling

client = IndexClient(["2019-47"], verbose=True) #initialize client to crawl

if not os.path.isfile('results.csv'):
    
    client.search("reddit.com/r/MachineLearning/*", threads=n_threads)  #specifiy crawling attributes (you may enter a keyword)
    client.results = (pd.DataFrame(client.results)      #create a pandas dataframe which is sorted by timestamp. duplicates are excluded
                    .sort_values(by="timestamp")
                    .drop_duplicates("urlkey", keep="last")
                    .to_dict("records"))
    client.download(threads=n_threads)  #start crawling

    pd.DataFrame(client.results).to_csv("results.csv")  #save the crawled dataframe to a csv file

df = pd.read_csv("results.csv") #read out the dataframe from the csv file

html_body = df['html']
results = html_body #copy the dataframe to create one of the same size, values will get overwritten
count = 0

for element in html_body:   #use beautiful soup to extract useful text from the crawled html formatted string 
    soup = BeautifulSoup(element, 'html.parser')
    results[count] = soup.title.get_text() + " --- " + soup.body.get_text()
    count += 1    

print(results)
print('Amount of crawled articles: {}\n'.format(count))

results.to_json('results.json') #save the formatted texts (html excluded) to a json-layout 





