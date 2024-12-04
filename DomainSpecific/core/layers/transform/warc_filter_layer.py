#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import re
from io import BytesIO
from warcio.warcwriter import WARCWriter
from warcio.limitreader import LimitReader
from warcio.archiveiterator import ArchiveIterator
import util

def warc_filter_layer(warc_file_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", TAGS=(), OVERWRITE=False):
    ret = list()
    try:
        src_warc_file_path = os.path.join(INPUT_FOLDER, warc_file_name)
        src_warc_file_path = util.to_real_path(src_warc_file_path, variables)
        dst_warc_file_path = os.path.join(OUTPUT_FOLDER, warc_file_name)
        dst_warc_file_path = util.to_real_path(dst_warc_file_path, variables)
        TAGS = list(map(lambda tag: bytes(tag, "ascii"), TAGS))
        regex = re.compile(b'|'.join(TAGS))

        if os.path.exists(src_warc_file_path) and (OVERWRITE or not os.path.exists(dst_warc_file_path)):
            util.create_folder_by_file_path(dst_warc_file_path)
            with open(dst_warc_file_path, "wb") as output:
                writer = WARCWriter(output, gzip=True)
                with open(src_warc_file_path, "rb") as input:
                    reader = ArchiveIterator(input, arc2warc=True)
                    for i, record in enumerate(reader):
                        if record.rec_type == "response" and record.http_headers.get_header("Content-Type", "").startswith("text/html"):
                            try:
                                # read raw html.
                                html = record.content_stream().read()

                                # filter.
                                if regex.search(html):
                                    content = BytesIO(html)
                                    assert len(html) == record.payload_length
                                    record.raw_stream = LimitReader(content, record.payload_length)
                                    writer.write_record(record)
                            except:
                                traceback.print_exc()
            
            ret = [warc_file_name]
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, )


if __name__ == "__main__":
    warc_file_name = "CC-MAIN-20221127073607-20221127103607-00007.warc.gz"
    INPUT_FOLDER = "$(input_data_folder)"
    OUTPUT_FOLDER = "$(output_data_folder)"
    TAGS = (
        "<math",
        "MathJax",
    )
    output = warc_filter_layer(warc_file_name, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER, TAGS=TAGS)
    print(output)
