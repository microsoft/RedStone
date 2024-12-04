#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
import argparse
os.sys.path.append("./core/layers/")
import util
import uuid
import datetime
from azure.batch import BatchServiceClient
from azure.common.credentials import BasicTokenAuthentication
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, AzureCliCredential
from azure.batch.models import JobAddParameter, PoolInformation, TaskAddParameter, UserIdentity
from azure.batch.models import AutoUserSpecification, ElevationLevel, TaskConstraints
from azure.batch.models import EnvironmentSetting, ResourceFile, OnAllTasksComplete, ComputeNodeIdentityReference

def submit_batch_job(network_path, run_mode, docker_path, computation_path, storage_path):
    docker_config = util.load_yaml(docker_path)
    computation_config = util.load_yaml(computation_path)
    storage_config = util.load_yaml(storage_path)

    workspace_dir = storage_config["workspace_dir"]
    endpoint = storage_config["azstorage"]["endpoint"]
    container = storage_config["azstorage"]["container"]
    resource_id = storage_config["resource_id"]
    identity = ComputeNodeIdentityReference(resource_id=resource_id)
    mount_blob = storage_config.get("mount", True)

    node_num = computation_config["batch_node_num"]
    process_per_node = computation_config["batch_process_per_node"]
    batch_url = computation_config["batch_url"]
    pool_id = computation_config["batch_pool_id"]

    # credential
    ##########################################
    try:
        credential = AzureCliCredential()
        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
        credential = InteractiveBrowserCredential()
    token = credential.get_token("https://batch.core.windows.net/.default")
    credential2 = BasicTokenAuthentication({"access_token": token.token})

    batch_client = BatchServiceClient(credential2, batch_url=batch_url)
    pool = batch_client.pool.get(pool_id)
    resource_files = list()

    # upload source code.
    package_local_path = "DataNetwork.tar.gz"
    package_blob_path = os.path.join("yanghuan", "package", os.path.basename(package_local_path))
    if True:
        os.system(f"sudo tar \
                    --exclude=env_ready \
                    --exclude=workspace \
                    --exclude=dependency/models \
                    -czf {package_local_path} *")
        util.upload_file_to_blob(storage_config, package_local_path, package_blob_path)
        os.system(f"sudo rm {package_local_path}")
    if True:
        package_url = f"{endpoint}/{container}/{package_blob_path}"
        package_file = ResourceFile(http_url=package_url, file_path=package_blob_path, identity_reference=identity)
        package_path = package_file.file_path
        resource_files.append(package_file)
    else:
        package_path = os.path.join(workspace_dir, package_blob_path)

    # upload model files.
    models_local_path = "models.tar.gz"
    models_blob_path = os.path.join("yanghuan", "package", os.path.basename(models_local_path))
    if True:
        #            --exclude=dependency/models/math.bin \
        #            --exclude=dependency/models/openquestion.bin \
        #            --exclude=dependency/models/mcq.pytorch \
        #            --exclude=dependency/models/mcq.bin \
        os.system(f"sudo tar \
                    -czf {models_local_path} dependency/models/*")
        util.upload_file_to_blob(storage_config, models_local_path, models_blob_path)
        os.system(f"sudo rm {models_local_path}")
    if not mount_blob:
        model_url = f"{endpoint}/{container}/{models_blob_path}"
        models_file = ResourceFile(http_url=model_url, file_path=models_blob_path, identity_reference=identity)
        models_path = models_file.file_path
        resource_files.append(models_file)
    else:
        models_path = os.path.join(workspace_dir, models_blob_path)

    job_id = uuid.uuid4()
    job = JobAddParameter(id=job_id, pool_info=PoolInformation(pool_id=pool_id), on_all_tasks_complete=OnAllTasksComplete.terminate_job)
    batch_client.job.add(job)

    tasks = []
    for node_id in range(node_num):
        batch_script_dependency = "./dependency/install.py"
        batch_script_entry = "./wrapper/runner.py"
        batch_commandline = f"bash -c '\
            sudo tar -xzf {package_path} && \
            sudo apt install python-is-python3 && \
            python {batch_script_dependency} --storage_path={storage_path} && \
            sudo tar -xzf {models_path} && \
            python {batch_script_entry} --network_path={network_path} --run_mode={run_mode} --worker_num={node_num} --workspace_dir={workspace_dir}\
        '"

        task = TaskAddParameter(
            id=f'{job_id}_{node_id}',
            command_line=batch_commandline,
            resource_files=resource_files,
            environment_settings=[EnvironmentSetting(name="NODE_NUM", value=str(node_num)), EnvironmentSetting(name="NODE_ID", value=str(node_id)), EnvironmentSetting(name="PROCESS_PER_NODE", value=str(process_per_node))],
            constraints=TaskConstraints(max_task_retry_count=3, retention_time=datetime.timedelta(days=30)),
            user_identity=UserIdentity(auto_user=AutoUserSpecification(elevation_level=ElevationLevel.admin))
        )
        tasks.append(task)

    batch_client.task.add_collection(job_id, tasks)
    print(f"job id: {job.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool of job submission in local machine.")
    parser.add_argument('--network_path', type=str, default="./configs/network_template.json", help="The config path of data network.")
    parser.add_argument('--run_mode', type=str, default="Batch", help="The running mode: Batch.")
    parser.add_argument('--docker_path', type=str, default="./resources/environment/local.yaml", help="The path of environment (docker) config file.")
    parser.add_argument('--computation_path', type=str, default="./resources/computation/batch_dca.yaml", help="The path of computation config file.")
    parser.add_argument('--storage_path', type=str, default="./resources/storage/llmstore.yaml", help="The path of storage config file.")
    args = parser.parse_args()
    submit_batch_job(args.network_path, args.run_mode, args.docker_path, args.computation_path, args.storage_path)
