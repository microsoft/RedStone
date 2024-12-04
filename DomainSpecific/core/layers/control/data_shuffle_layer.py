#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import random
import traceback

def data_shuffle_layer(lines, variables=dict(), SEED=1):
    ret = list()
    try:
        random.seed(SEED)
        random.shuffle(lines)
        ret = lines
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lines = ["a", "b"]
    lines = data_shuffle_layer(lines)
    print(lines)
