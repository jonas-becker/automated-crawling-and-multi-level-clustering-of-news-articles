import re
import time
import gzip
import json
import requests
import pandas as pd
import urllib
import bs4
from io import BytesIO

query_url = 'http://edition.cnn.com/WORLD/europe/*'

def get_index_url():
    query = urllib.parse.quote_plus(query_url)
    base_url = 'https://index.commoncrawl.org/CC-MAIN-2020-16-index?url='
    index_url = base_url + query + '&output=json'
    return index_url

def get_index_json(index_url):
    payload_content = None
    for i in range(4):
        resp = requests.get(index_url)
        print(resp.status_code)
        time.sleep(0.2)
        if resp.status_code == 200:
            for x in resp.content.strip().decode().split('\n'):
                payload_content = json.loads(x)
            break
    return payload_content

def get_from_index(page):
    warc, header, response = None
    offset, length = int(page['offset']), int(page['length'])
    offset_end = offset + length - 1
    prefix = 'https://commoncrawl.s3.amazonaws.com/'
    try:
        r = requests.get(prefix + page['filename'], headers={'Range':
        'bytes={}-{}'.format(offset, offset_end)})
        raw_data = BytesIO(r.content)
        f = gzip.GzipFile(fileobj=raw_data)
        data = f.read()
    except:
        print('some error in connection?')
    try:
        warc, header, response = data.strip().decode().split('\r\n\r\n', 2)
    except Exception as e:
        pass
        print(e)
    return warc, header, response

def get_paragraphs(response):
    soup = bs4.BeautifulSoup(response,'html.parser')
    p_list = []
    for p in soup.find_all('p'):
        p_list.append(p.text.replace('\n', ' ').strip())
    print(p_list)

def main():
    index_url = get_index_url()
    print(index_url)
    payload_content = get_index_json(index_url)
    warc, header, response = get_from_index(payload_content)
    print(type(response))
    get_paragraphs(response)
    print(warc)
    print(response)

if __name__ == '__main__':
    main()

