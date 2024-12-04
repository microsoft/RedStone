#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback

def data_filter_layer(lines, variables=dict(), IN=False, FILTERS=(None,)):
    ret = list()
    try:
        ret = list(filter(lambda line: line in FILTERS if IN else line not in FILTERS, lines))
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lines = ["a", None, "b"]
    FILTERS = (None,)
    lines = data_filter_layer(lines, FILTERS=FILTERS)
    print(lines)
