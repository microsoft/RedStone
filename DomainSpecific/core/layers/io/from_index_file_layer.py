#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import faiss
import traceback
import util

def from_index_file_layer(file_path, variables=dict(), STORAGE_PATH=None):
    ret = None
    try:
        file_path = util.to_real_path(file_path, variables)
        if STORAGE_PATH is not None:
            util.download_file_from_blob(STORAGE_PATH, file_path, file_path)

        index = faiss.read_index(file_path)
        ret = index
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == '__main__':
    file_path = "index.faiss"
    index = from_index_file_layer(file_path)
    print(index)
