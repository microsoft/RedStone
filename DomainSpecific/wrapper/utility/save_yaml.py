#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import yaml

def save_yaml(config, config_path):
    if os.path.exists(os.path.dirname(config_path)):
        with open(config_path, "w") as file:
            yaml.safe_dump(config, file)
