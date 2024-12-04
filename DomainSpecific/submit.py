#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import argparse

def submit_job(network_path, run_mode, docker_path, computation_path, storage_path):
    if run_mode in ("Single", "MultiProcess",):
        from tools.submit_local_job import submit_local_job as func
    elif run_mode == "Batch":
        from tools.submit_batch_job import submit_batch_job as func
    else:
        assert False
    func(network_path, run_mode, docker_path, computation_path, storage_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool of job submission.")
    parser.add_argument("--network_path", type=str, default="./configs/network_template.json", help="The config path of data network.")
    parser.add_argument('--run_mode', type=str, default="Single", help="The running mode: Single, MultiProcess, and Batch.")
    parser.add_argument('--docker_path', type=str, default="./resources/environment/local.yaml", help="The path of environment (docker) config file.")
    parser.add_argument('--computation_path', type=str, default="./resources/computation/local.yaml", help="The path of computation config file.")
    parser.add_argument('--storage_path', type=str, default="./resources/storage/local.yaml", help="The path of storage config file.")
    args = parser.parse_args()
    
    submit_job(args.network_path, args.run_mode, args.docker_path, args.computation_path, args.storage_path)
