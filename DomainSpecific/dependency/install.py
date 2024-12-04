#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/../wrapper/utility")
import time
import argparse
from load_yaml import load_yaml
from save_yaml import save_yaml
from azure_env import get_local_rank, get_world_rank

ENV_READY = "env_ready"
OS_VERSION = "ubuntu/18.04"# ubuntu/18.04, ubuntu/20.04, ubuntu/22.04

def install(local_id, storage_path):
    local_id = get_local_rank() if get_local_rank() is not None else local_id
    if local_id == 0:
        if os.path.exists(ENV_READY):
            return

        # install python dependencies.
        os.system(f"pip install --upgrade pip")
        os.system(f"pip install -r dependency/requirements.txt")
        os.system(f"pip install guesslang==2.2.1 --no-deps")# don't change the version.

        # install others.
        os.system(f"sudo wget https://packages.microsoft.com/config/{OS_VERSION}/packages-microsoft-prod.deb")
        os.system(f"sudo dpkg -i packages-microsoft-prod.deb")
        os.system(f"sudo apt-get -y update")
        os.system(f"sudo apt-get -y install axel")# for fast file download.

        os.system(f"sudo apt update")
        os.system(f"sudo apt -y install git")
        os.system(f"sudo apt -y install git-lfs")
        os.system(f"sudo apt -y install maven")
        os.system(f"sudo apt -y install openjdk-11-jdk")# java-related 3rd-part library.
        os.system(f"ulimit -n 65536")

        # mount folder: default mount the storage.
        storage_config = load_yaml(storage_path)
        if storage_config.get("mount", True):
            # install fuseblob library
            os.system(f"sudo apt-get -y install libcurl3-gnutls")
            os.system(f"sudo apt-get -y install blobfuse")
            os.system(f"sudo apt-get -y install libfuse2")
            os.system(f"sudo apt-get -y install blobfuse2")

            # create folder to be mounted
            workspace_dir = storage_config["workspace_dir"]
            filecache_dir = storage_config["file_cache"]["path"]

            try:
                os.system(f"sudo umount -l {workspace_dir}")# debug
                #os.system("ps -ef | grep blobfuse | grep -v grep | awk -F ' ' '{print $2}' | xargs sudo kill -9")# debug
            except:
                pass
            
            os.system(f"sudo mkdir -p {workspace_dir}")
            os.system(f"sudo chown $(whoami) {workspace_dir}")

            if os.path.exists(filecache_dir):
                try:
                    os.system(f"sudo rm -rf {filecache_dir}")# debug
                except:
                    pass
            
            os.system(f"sudo mkdir -p {filecache_dir}")
            os.system(f"sudo chown $(whoami) {filecache_dir}")

            os.system(f"sudo blobfuse2 mount {workspace_dir} --config-file={storage_path}")
            print("mount azure storage account.")
        else:
            print("not mount azure storage account.")

        # create env tag
        os.system(f"sudo rm -rf packages-microsoft-prod.deb")
        os.system(f"sudo touch {ENV_READY}")
    else:
        mounting = True
        while mounting:
            mounting = not os.path.exists(ENV_READY)
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install dependencies of Data Network.")
    parser.add_argument('--local_id', type=int, default=0, help="The id of local worker.")
    parser.add_argument('--storage_path', type=str, default="./resources/storage/llmstore.yaml", help="The path of storage config file.")
    args = parser.parse_args()
    install(args.local_id, args.storage_path)
