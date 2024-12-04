#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import traceback
import util

def download_bytes_from_internet_layer(url, variables=dict(), TRIES=1):
    ret = (None, None, url)
    try:
        for _ in range(TRIES):
            try:
                url = util.to_real_path(url, variables)
                file_name = util.md5(url) + util.suffix(url)
                bytes = util.download_bytes_from_internet(url)
                ret = (file_name, bytes, None)
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
    bytes = download_bytes_from_internet_layer(url)
    print(bytes)
