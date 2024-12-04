#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import argparse
import traceback
from enum import Enum
from threading import Thread
from multiprocessing import Process
from wrapper import Interpreter
from wrapper.utility import get_world_rank, get_world_size, get_process_per_node

class RunMode(Enum):
    Single = 0
    MultiProcess = 1
    Batch = 2

class Runner:
    def __init__(self, network_path):
        interpreter = Interpreter()
        self.network = interpreter(network_path)

    def __call__(self, run_mode, worker_id, worker_num, workspace_dir):
        try:
            input = list()
            variables = {"workspace_dir": workspace_dir}
            if run_mode == RunMode.Single:
                for worker_id in range(worker_num):
                    self.network(input, worker_id, worker_num, variables)
            elif run_mode == RunMode.MultiProcess:
                processes = list()
                for worker_id in range(worker_num):
                    process = Process(target=self.network, args=(input, worker_id, worker_num, variables))
                    process.start()
                    processes.append(process)
                for process in processes:
                    process.join()
            elif run_mode == RunMode.Batch:
                process_per_node = get_process_per_node()
                worker_id = process_per_node * get_world_rank()
                worker_num = process_per_node * get_world_size()
                processes = list()
                for worker_id in range(worker_id, worker_id + process_per_node):
                    process = Process(target=self.network, args=(input, worker_id, worker_num, variables))
                    process.start()
                    processes.append(process)
                for process in processes:
                    process.join()
            else:
                raise Exception(f"Unknown running mode: {run_mode}")
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
            return False
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Runner of Data Network.")
    parser.add_argument('--network_path', type=str, default="./configs/network_template.json", help="The config path of data network.")
    parser.add_argument('--run_mode', type=str, default="Single", help="The running mode: Single, MultiProcess, and Batch.")
    parser.add_argument('--workspace_dir', type=str, default="./workspace/", help="The path of workspace folder.")
    parser.add_argument('--worker_id', type=int, default=0, help="The id of world worker.")
    parser.add_argument('--worker_num', type=int, default=1, help="The number of world worker.")
    args = parser.parse_args()

    runner = Runner(args.network_path)
    success = runner(RunMode[args.run_mode], args.worker_id, args.worker_num, args.workspace_dir)
