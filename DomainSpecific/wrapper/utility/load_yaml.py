#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import yaml

def load_yaml(config_path):
    config = None
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    return config
