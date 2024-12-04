#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import traceback
import util

def download_file_from_blob_layer(blob_path, variables=dict(), DOWNLOAD_PATH=".", STORAGE_PATH=None, TRIES=1):
    ret = (None, blob_path)
    try:
        for _ in range(TRIES):
            try:
                assert STORAGE_PATH is not None and os.path.exists(STORAGE_PATH)
                storage_config = util.load_yaml(STORAGE_PATH)
                blob_path = util.to_real_path(blob_path, variables)
                file_name = util.md5(blob_path) + util.suffix(blob_path)
                file_path = os.path.join(DOWNLOAD_PATH, file_name)
                file_path = util.to_real_path(file_path, variables)
                util.download_file_from_blob(storage_config, blob_path, file_path)
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
    blob_path = "$(azure_blob_path)"
    DOWNLOAD_PATH = "$(local_folder_path)"
    STORAGE_PATH = "resources/environment/llmstore.yaml"
    path = download_file_from_blob_layer(blob_path, DOWNLOAD_PATH=DOWNLOAD_PATH, STORAGE_PATH=STORAGE_PATH)
    print(path)
