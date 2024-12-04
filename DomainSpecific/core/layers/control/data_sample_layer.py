#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import random
import traceback

def data_sample_layer(lines, variables=dict(), N=-1, SEED=1):
    ret = list()
    try:
        random.seed(SEED)
        N = min(N, len(lines))
        if N >= 0:
            ret = random.sample(lines, N)
        else:
            ret = lines
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lines = ["a", "b"]
    N = 1
    lines = data_sample_layer(lines, N=N)
    print(lines)
