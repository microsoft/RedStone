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

def to_parquet_file_layer(data, file_path, variables=dict(), STORAGE_PATH=None):
    ret = None
    try:
        file_path = util.to_real_path(file_path, variables)
        util.create_folder_by_file_path(file_path)

        table = pa.Table.from_pylist(data)
        pq.write_table(table, file_path)

        if STORAGE_PATH is not None:
            util.upload_file_to_blob(STORAGE_PATH, file_path, file_path)

        ret = file_path
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    data = [{'id': "1", 'html': "hello"}, {'id': "2", 'html': "hi"}]
    file_path = "test.parquet"
    file_path = to_parquet_file_layer(data, file_path)
    print(file_path)
