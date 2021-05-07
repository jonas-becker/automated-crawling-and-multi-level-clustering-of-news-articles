from comcrawl import IndexClient
import pandas as pd
import os
from bs4 import BeautifulSoup

n_threads = 5

client = IndexClient(["2019-51", "2019-47"], verbose=True)

if not os.path.isfile('results.csv'):
    
    client.search("reddit.com/r/MachineLearning/*", threads=n_threads)
    client.results = (pd.DataFrame(client.results)
                    .sort_values(by="timestamp")
                    .drop_duplicates("urlkey", keep="last")
                    .to_dict("records"))
    client.download(threads=n_threads)

    pd.DataFrame(client.results).to_csv("results.csv")

df = pd.read_csv("results.csv")

html_body = df['html']
results = html_body
count = 0

for element in html_body:

    print('Title:')
    print('________________________________________')
    soup = BeautifulSoup(element, 'html.parser')
    title = soup.title.string
    print(title)
    print('Body:')
    print('________________________________________')
    body = soup.body.get_text()
    print(body)
    print('\n')
    count += 1
    if title or body is None:
        continue
    else:
        results['html'][count] = 'Title:{}\n\nBody:\n{}'.format(title.string, body.string)

print('Amount of crawled articles: {}\n'.format(count))

results.to_json('results.json')





