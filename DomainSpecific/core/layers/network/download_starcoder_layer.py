#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import json
from datetime import datetime
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import smart_open
from datasets import load_dataset
import util

s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

def download_contents(blob_id, src_encoding):
    s3_url = f"s3://softwareheritage/content/{blob_id}"
    with smart_open.open(s3_url, "rb", compression=".gz", transport_params={"client": s3}) as fin:
        content = fin.read().decode(src_encoding)
    return content

def download_starcoder_layer(data_repo, variables=dict(), OUTPUT_FOLDER="./", STORAGE_PATH=None, HUGGINGFACE_TOKEN=None):
    ret = 0
    try:
        worker_id = variables["worker_id"]
        worker_num = variables["worker_num"]
        data_repo = util.to_real_path(data_repo, variables)
        output_folder = util.to_real_path(OUTPUT_FOLDER, variables)
        if STORAGE_PATH is not None:
            storage_config = util.load_yaml(STORAGE_PATH)

        ds = load_dataset(data_repo, split="train", streaming=True, token=HUGGINGFACE_TOKEN, cache_dir=f"./cache.{worker_id}/")
        ds = ds.filter(lambda row, idx: idx % worker_num == worker_id, with_indices=True)

        item_count = 0
        for i, row in enumerate(ds):
            for key in row.keys():
                if isinstance(row[key], datetime):
                    row[key] = datetime.timestamp(row[key])

            blob_id = row["blob_id"]
            src_encoding = row["src_encoding"]

            snapshot_prefix = row["snapshot_id"][:4]
            repo_name = row["repo_name"].replace("/", "@")
            branch_name = row["branch_name"].replace("/", "@")
            language = row["language"].replace(" ", "_")
            path = row["path"].lstrip("/")
            filename = row["filename"].strip()
            filename = path
            extension = row["extension"].strip()

            content = download_contents(blob_id, src_encoding)

            code_path = os.path.join(output_folder, snapshot_prefix, repo_name, branch_name, blob_id)
            metadata_path = os.path.join(output_folder, snapshot_prefix, repo_name, branch_name, blob_id + ".json")

            try:
                util.create_folder_by_file_path(code_path)
                with open(code_path, "w") as f:
                    f.write(content)
                if STORAGE_PATH is not None:
                    util.upload_file_to_blob(storage_config, code_path, code_path)

                util.create_folder_by_file_path(metadata_path)
                with open(metadata_path, "w") as f:
                    f.write(json.dumps(row, indent=4) + "\n")
                if STORAGE_PATH is not None:
                    util.upload_file_to_blob(storage_config, metadata_path, metadata_path)

                if STORAGE_PATH is not None:
                    try:
                        os.remove(code_path)
                        os.remove(metadata_path)
                    except OSError:
                        pass
            except:
                traceback.print_exc()
            
            item_count += 1

        ret = item_count
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == '__main__':
    data_repo = "$(local_the_stack_v2_dedup_metadata_path)"
    variables = {"workspace_dir": r"workspace", "worker_id": 0, "worker_num": 1}
    OUTPUT_FOLDER = "$(local_the_stack_v2_dedup_data_path)"
    STORAGE_PATH = "resources/storage/llmstore.yaml"
    HUGGINGFACE_TOKEN = None
    item_count = download_starcoder_layer(data_repo, variables=variables, OUTPUT_FOLDER=OUTPUT_FOLDER, STORAGE_PATH=STORAGE_PATH, HUGGINGFACE_TOKEN=HUGGINGFACE_TOKEN)
    print(item_count)
