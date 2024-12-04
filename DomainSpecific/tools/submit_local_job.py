#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
import argparse
os.sys.path.append("./core/layers/")
import util

def submit_local_job(network_path, run_mode, docker_path, computation_path, storage_path):
    docker_config = util.load_yaml(docker_path)
    computation_config = util.load_yaml(computation_path)
    storage_config = util.load_yaml(storage_path)

    script_entry = "./wrapper/runner.py"
    script_dependency = "./dependency/install.py"
    commandline = f"python {script_dependency} --storage_path={storage_path} && python {script_entry} --network_path={network_path} --run_mode={run_mode} --workspace_dir={storage_config['workspace_dir']} --worker_num={computation_config['worker_num']}"
    os.system(commandline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool of job submission in local machine.")
    parser.add_argument('--network_path', type=str, default="./configs/network_template.json", help="The config path of data network.")
    parser.add_argument('--run_mode', type=str, default="Single", help="The running mode: Single, MultiProcess.")
    parser.add_argument('--docker_path', type=str, default="./resources/environment/local.yaml", help="The path of environment (docker) config file.")
    parser.add_argument('--computation_path', type=str, default="./resources/computation/local.yaml", help="The path of computation config file.")
    parser.add_argument('--storage_path', type=str, default="/resources/storage/local.yaml", help="The path of storage config file.")
    args = parser.parse_args()
    submit_local_job(args.network_path, args.run_mode, args.docker_path, args.computation_path, args.storage_path)
