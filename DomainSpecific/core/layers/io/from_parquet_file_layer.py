#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import pyarrow as pa
import pyarrow.parquet as pq
import util

def from_parquet_file_layer(file_path, variables=dict(), STORAGE_PATH=None):
    ret = None
    try:
        file_path = util.to_real_path(file_path, variables)
        if STORAGE_PATH is not None:
            util.download_file_from_blob(STORAGE_PATH, file_path, file_path)

        table = pq.read_table(file_path)
        ret = table.to_pylist()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    file_path = "test.parquet"
    data = from_parquet_file_layer(file_path)
    print(data)
