#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import gzip
import requests
import traceback

def download_warc_indice_layer(index_url, variables=dict(), TRIES=1, URL_PREFIX="https://data.commoncrawl.org/"):
    ret = list()
    try:
        for _ in range(TRIES):
            try:
                resp = requests.get(index_url, stream=True)
                urls = list()
                with gzip.open(resp.raw, 'rt') as f:
                    for line in f.readlines():
                        warc_url = URL_PREFIX + line.strip()
                        urls.append(warc_url)
                ret = urls
                break
            except:
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, [index_url] if len(ret) == 0 else [])


if __name__ == '__main__':
    index_url = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2022-49/warc.paths.gz"
    warc_urls = download_warc_indice_layer(index_url)
    print(warc_urls[0][0])
