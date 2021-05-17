import re
import time
import gzip
import json
import requests
try:
    from io import BytesIO
except:
    from StringIO import StringIO
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
index_json = get_index_json(index_url)
print(index_json)

