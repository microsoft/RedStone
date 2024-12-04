#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import gzip
import json
import requests
import traceback

def download_url_list_layer(index_url, variables=dict(), FILTER_SUFFIXES=(), TRIES=1):
    ret = list()
    try:
        for _ in range(TRIES):
            try:
                resp = requests.get(index_url, stream=True)
                urls = list()
                with gzip.open(resp.raw, 'rt') as f:
                    for line in f.readlines():
                        text = "{" + line.strip().split(" {")[1]
                        item = json.loads(text)
                        url = item["url"]
                        suffix = os.path.splitext(url)[1]
                        if suffix in FILTER_SUFFIXES:
                            urls.append(url)
                ret[0:0] = urls
                break
            except:
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, [index_url] if len(ret) == 0 else [])


if __name__ == '__main__':
    index_url = "https://data.commoncrawl.org/cc-index/collections/CC-MAIN-2023-23/indexes/cdx-00000.gz"
    FILTER_SUFFIXES = (".svg",)
    urls = download_url_list_layer(index_url, FILTER_SUFFIXES=FILTER_SUFFIXES)
    print(urls)
