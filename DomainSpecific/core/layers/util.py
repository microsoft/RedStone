#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import copy
import yaml
import hashlib
import logging
import datetime
import requests
from urllib.parse import urljoin
from azure.storage.blob import ContainerClient, BlobSasPermissions, generate_blob_sas
from azure.identity import DefaultAzureCredential
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def load_yaml(config_path):
    config = None
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    return config

def save_yaml(config, config_path):
    if os.path.exists(os.path.dirname(config_path)):
        with open(config_path, "w") as file:
            yaml.safe_dump(config, file)

def str2bytes(data):
    data = bytes(data, "utf-8")
    return data

def md5(data):
    if isinstance(data, str):
        data = str2bytes(data)
    md5 = hashlib.md5(data).hexdigest()
    return md5

def sha256(data):
    if isinstance(data, str):
        data = str2bytes(data)
    sha256 = hashlib.sha256(data).hexdigest()
    return sha256

def suffix(path):
    suffix = os.path.splitext(path)[1]
    return suffix

def relative2absolute_path(prefix, link):
    # Root-relative path.
    if link.startswith("/"):
        link = urljoin(prefix, link)
    else:
        colon_count = link[:10].count(":")
        # Document-relative path.
        if link.startswith(".") or colon_count == 0:
            link = urljoin(prefix, link)
        # Absolute paths, such as `http://`, `https://`, `ftp://`, or 'file://'.
        else:
            link = link
    return link

def create_folder_by_file_path(local_file_path):
    local_folder_path = os.path.dirname(local_file_path)
    if not os.path.exists(local_folder_path) and len(local_folder_path.strip()) != 0:
        try:
            os.makedirs(local_folder_path, exist_ok=True)
        except:
            pass

def to_real_path(path, variables):
    keys = ("workspace_dir", "worker_id", "worker_num")
    path = copy.copy(path)
    for name, value in variables.items():
        if name in keys:
            path = path.replace("{%s}" % name, str(value))
    return path

def get_container_client(storage_config):
    if isinstance(storage_config, ContainerClient):
        return storage_config

    if isinstance(storage_config, str) and os.path.exists(storage_config):
        storage_config = load_yaml(storage_config)

    account_domain = "blob.core.windows.net"
    account_name = storage_config["azstorage"]["account-name"]
    #account_key = storage_config["azstorage"]["account-key"]
    container_name = storage_config["azstorage"]["container"]
    identity_id = storage_config["azstorage"]["appid"]
    credential = DefaultAzureCredential(managed_identity_client_id=identity_id)

    container_client = ContainerClient(
        account_url=f"https://{account_name}.{account_domain}/",
        container_name=container_name,
        credential=credential#account_key
    )

    return container_client

def get_blob_client(storage_config, blob_path):
    container_client = get_container_client(storage_config)
    blob_client = container_client.get_blob_client(blob_path)
    return blob_client

def exist_blob(container_client, blob_path):
    with container_client.get_blob_client(blob_path) as blob_client:
        blob_path_exists = blob_client.exists()
        return blob_path_exists

def get_blob_size(container_client, blob_path):
    with container_client.get_blob_client(blob_path) as blob_client:
        properties = blob_client.get_blob_properties()
        size = properties.size
        return size

def list_blob_dir(container_client, blob_path):
    names = list()
    for blob in container_client.walk_blobs(name_starts_with=blob_path):
        names.append(blob.name)
    return names

def create_blob_dir(container_client, blob_path):
    container_client.upload_blob(name=os.path.join(blob_path, "_"), data=b"", overwrite=True)

def upload_bytes_to_blob(storage_config, content, blob_path):
    with get_blob_client(storage_config, blob_path) as blob_client:
        blob_client.upload_blob(content, overwrite=True)
    return blob_path

def upload_file_to_blob(storage_config, local_path, blob_path):
    with open(local_path, "rb") as content:
        upload_bytes_to_blob(storage_config, content, blob_path)
    return blob_path

def upload_bytes_to_internet(content, blob_path):
    # TODO: to be implemented.
    return blob_path

def upload_file_to_internet(local_path, blob_path):
    # TODO: to be implemented.
    return blob_path

def download_bytes_from_blob(storage_config, blob_path):
    with get_blob_client(storage_config, blob_path) as blob_client:
        content = blob_client.download_blob().readall()
    return content

def download_file_from_blob(storage_config, blob_path, local_path):
    content = download_bytes_from_blob(storage_config, blob_path)
    create_folder_by_file_path(local_path)
    with open(local_path, "wb") as data:
        data.write(content)
    return local_path

def download_bytes_from_internet(url, timeout=3):
    try:
        resp = requests.get(url, allow_redirects=True, timeout=timeout)
        if resp.status_code == 200:
            content = resp.content
            return content
        else:
            return None
    except:
        return None

def download_file_from_internet(url, local_path):
    try:
        content = download_bytes_from_internet(url)
        if content is not None:
            create_folder_by_file_path(local_path)
            with open(local_path, "wb") as data:
                data.write(content)
            return local_path, len(content)
        else:
            return None, 0
    except:
        return None, 0
