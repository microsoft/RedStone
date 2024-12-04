#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os

def get_local_rank():
    # Azure Singularity.
    if "OMPI_COMM_WORLD_LOCAL_RANK" in os.environ:
        return int(os.environ["OMPI_COMM_WORLD_LOCAL_RANK"])
    return None

def get_world_rank():
    # Azure Singularity.
    if "OMPI_COMM_WORLD_RANK" in os.environ:
        return int(os.environ["OMPI_COMM_WORLD_RANK"])
    # Azure Batch.
    elif "NODE_ID" in os.environ:
        return int(os.environ["NODE_ID"])
    return None

def get_world_size():
    # Azure Singularity.
    if "OMPI_COMM_WORLD_SIZE" in os.environ:
        return int(os.environ["OMPI_COMM_WORLD_SIZE"])
    # Azure Batch.
    elif "NODE_NUM" in os.environ:
        return int(os.environ["NODE_NUM"])
    # Azure Spark.
    elif "NUM_EXECUTORS" in os.environ:
        return int(os.environ["NUM_EXECUTORS"])
    return None

def get_process_per_node():
    # Azure Batch.
    if "PROCESS_PER_NODE" in os.environ:
        return int(os.environ["PROCESS_PER_NODE"])
    # Azure Spark.
    elif "EXECUTOR_CORES" in os.environ:
        return int(os.environ["EXECUTOR_CORES"])
    return None
