#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import traceback
import util

def download_file_from_internet_layer(url, variables=dict(), DOWNLOAD_PATH=".", TRIES=1):
    ret = (None, url)
    try:
        for _ in range(TRIES):
            try:
                url = util.to_real_path(url, variables)
                file_name = util.md5(url) + util.suffix(url)
                file_path = os.path.join(DOWNLOAD_PATH, file_name)
                file_path = util.to_real_path(file_path, variables)
                util.download_file_from_internet(url, file_path)
                #bytes = util.download_bytes_from_internet(url)
                #util.upload_bytes_to_blob(variables["storage_config"], bytes, file_path)
                ret = (file_path, None)
                break
            except:
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return ret


if __name__ == '__main__':
    url = "https://upload.wikimedia.org/wikipedia/commons/4/4f/SVG_Logo.svg"
    DOWNLOAD_PATH = "$(local_folder_path)"
    path = download_file_from_internet_layer(url, DOWNLOAD_PATH=DOWNLOAD_PATH)
    print(path)
