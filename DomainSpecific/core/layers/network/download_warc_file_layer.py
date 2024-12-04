#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import traceback
import util

def download_warc_file_layer(warc_url, variables=dict(), DOWNLOAD_FOLDER="./", CONNECTS=16, TRIES=1, OVERWRITE=False):
    ret = (None, warc_url)
    try:
        if not warc_url.startswith("https://"):
            warc_url = "https://data.commoncrawl.org/" + warc_url
        #warc_url = warc_url.replace("https://data.commoncrawl.org/", "https://ds5q9oxwqwsfj.cloudfront.net/")# debug
        warc_name = warc_url.split("/")[-3] + "_" + os.path.basename(warc_url)
        warc_path = os.path.join(DOWNLOAD_FOLDER, warc_name)
        warc_path = util.to_real_path(warc_path, variables)

        for _ in range(TRIES):
            if OVERWRITE or not os.path.exists(warc_path):
                util.create_folder_by_file_path(warc_path)
                commandline = f"axel -q -n {CONNECTS} -o {warc_path} {warc_url}"
                exit_status = os.system(commandline)
            else:
                exit_status = 0

            if exit_status == 0:
                break
            time.sleep(1)

        if exit_status == 0:
            ret = (warc_name, None)
        else:
            ret = (None, warc_url)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return ret


if __name__ == '__main__':
    warc_url = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2022-49/segments/1669446706285.92/warc/CC-MAIN-20221126080725-20221126110725-00000.warc.gz"
    DOWNLOAD_FOLDER = "$(local_folder_path)"
    (success_warc_url, failed_warc_url) = download_warc_file_layer(warc_url, DOWNLOAD_FOLDER=DOWNLOAD_FOLDER)
    print(success_warc_url, failed_warc_url)
