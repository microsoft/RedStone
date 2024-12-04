#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback

def data_order_layer(lines, variables=dict(), REVERSE=False):
    ret = list()
    try:
        ret = sorted(lines, reverse=REVERSE)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lines = [1, 3, 2]
    lines = data_order_layer(lines)
    print(lines)
