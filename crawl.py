from comcrawl import IndexClient
import pandas as pd
import os
from bs4 import BeautifulSoup

client = IndexClient(["2019-51", "2019-47"], verbose=True)

if os.path.isfile('results.csv') is False:
    
    client.search("reddit.com/r/MachineLearning/*", threads=4)

    client.results = (pd.DataFrame(client.results)
                    .sort_values(by="timestamp")
                    .drop_duplicates("urlkey", keep="last")
                    .to_dict("records"))

    client.download(threads=4)

    pd.DataFrame(client.results).to_csv("results.csv")

df = pd.read_csv("results.csv")

print(df['html'])
html_body = df['html']

for element in html_body:

    soup = BeautifulSoup(element, 'html.parser')
    print(soup.title.string)


