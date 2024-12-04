#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
from warcio.archiveiterator import ArchiveIterator
import util

def from_wet_file_layer(file_path, variables=dict(), STORAGE_PATH=None):
    ret = None
    try:
        file_path = util.to_real_path(file_path, variables)
        if STORAGE_PATH is not None:
            util.download_file_from_blob(STORAGE_PATH, file_path, file_path)

        if os.path.exists(file_path):
            items = list()
            with open(file_path, "rb") as input:
                records = ArchiveIterator(input, arc2warc=False)
                for idx, record in enumerate(records):
                    if record.rec_type == "conversion":
                        item = dict()
                        item["uri"] = record.rec_headers.get("WARC-Target-URI")
                        item["lang"] = record.rec_headers.get("Detected-Language")
                        item["content_length"] = record.rec_headers["Content-Length"]
                        item["text"] = record.content_stream().read()
                        items.append(item)
            ret = items
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    file_path = "test.warc.wet.gz"
    data = from_wet_file_layer(file_path)
    print(data)
