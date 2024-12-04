#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import traceback
import util

def download_bytes_from_blob_layer(blob_path, variables=dict(), STORAGE_PATH=None, TRIES=1):
    ret = (None, None, blob_path)
    try:
        for _ in range(TRIES):
            try:
                assert STORAGE_PATH is not None and os.path.exists(STORAGE_PATH)
                storage_config = util.load_yaml(STORAGE_PATH)
                blob_path = util.to_real_path(blob_path, variables)
                file_name = util.md5(blob_path) + util.suffix(blob_path)
                bytes = util.download_bytes_from_blob(storage_config, blob_path)
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
    blob_path = "$(azure_blob_path)"
    STORAGE_PATH = "resources/environment/llmstore.yaml"
    bytes = download_bytes_from_blob_layer(blob_path, STORAGE_PATH=STORAGE_PATH)
    print(bytes)
