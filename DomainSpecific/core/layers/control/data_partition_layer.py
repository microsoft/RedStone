#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback

def data_partition_layer(lines, variables=dict(), WORKER_ID=-1):
    ret = list()
    try:
        worker_id = variables.get("worker_id", 0)
        worker_num = variables.get("worker_num", 1)
        n = len(lines)
        if WORKER_ID == -1:
            ret = [lines[i] for i in range(worker_id, n, worker_num)]
        else:
            ret = lines if WORKER_ID == worker_id else list()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lines = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    variables = {"worker_id": 0, "worker_num": 2}
    lines = data_partition_layer(lines, variables=variables)
    print(lines)
