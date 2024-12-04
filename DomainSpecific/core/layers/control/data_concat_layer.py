#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback

def data_concat_layer(lists, variables=dict()):
    ret = list()
    try:
        for a_list in lists[::-1]:
            if a_list is not None:
                ret[0:0] = a_list
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lists = [["a"], ["b", "c"], None, ["d", "e", "f"]]
    lines = data_concat_layer(lists)
    print(lines)
