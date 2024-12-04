#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import time
import traceback
import util

def upload_bytes_to_blob_layer(bytes, blob_path, variables=dict(), STORAGE_PATH=None, BLOB_PREFIX="", TRIES=1):
    ret = (None, blob_path)
    try:
        for _ in range(TRIES):
            try:
                assert STORAGE_PATH is not None and os.path.exists(STORAGE_PATH)
                storage_config = util.load_yaml(STORAGE_PATH)
                blob_path = util.to_real_path(os.path.join(BLOB_PREFIX, blob_path), variables)
                util.upload_bytes_to_blob(storage_config, bytes, blob_path)
                ret = (blob_path, None)
                break
            except:
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return ret


if __name__ == '__main__':
    bytes = b"hello"
    blob_path = "$(azure_blob_path)"
    STORAGE_PATH = "resources/environment/llmstore.yaml"
    path = upload_bytes_to_blob_layer(bytes, blob_path, STORAGE_PATH=STORAGE_PATH)
    print(path)
