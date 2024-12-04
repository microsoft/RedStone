#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import requests
import logging
import traceback
import xml.etree.ElementTree as ET

def download_urls_from_website_layer(website_url, variables=dict(), FILTER=None):
    ret = list()
    try:
        robot_url = website_url + "/robots.txt"
        logging.disable(logging.WARNING)

        # get sitemap.
        xml_urls = list()
        whilte_url_prefixs = list()
        black_url_prefixs = list()
        resp = requests.get(robot_url)
        crawler = None
        for line in resp.text.split("\n"):
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith("#"):
                continue

            if line.startswith("User-agent:"):
                crawler = line.split(":")[-1].strip()
                continue

            if crawler != "*":
                continue
            if crawler == "*" and line.startswith("Disallow:"):
                url_prefix = line.replace("Disallow:", "").strip()
                black_url_prefixs.append(url_prefix)
                continue
            if crawler == "*" and line.startswith("Allow:"):
                url_prefix = line.replace("Allow:", "").strip()
                whilte_url_prefixs.append(url_prefix)
                continue
            if crawler == "*" and line.startswith("Sitemap:"):
                xml_url = line.replace("Sitemap:", "").strip()
                if (FILTER is None or FILTER in xml_url) and xml_url.endswith(".xml"):
                    xml_urls.append(xml_url)
                continue

        # get urls.
        html_urls = set()
        for xml_url in xml_urls:
            try:
                resp = requests.get(xml_url)
                root = ET.fromstring(resp.content)
                for sitemap in root:
                    html_url = list(sitemap)[0].text
                    html_urls.add(html_url)
                #nodes = tree.xpath('//a/@href')
                #nodes = tree.xpath("//loc")
            except:
                pass

        ret = list(html_urls)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == '__main__':
    website_url = "https://byjus.com/"
    FILTER = "math"
    urls = download_urls_from_website_layer(website_url, FILTER=FILTER)
    print(urls[0][0])
