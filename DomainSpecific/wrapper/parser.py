#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
import json
import traceback

class Parser:
    def __init__(self):
        pass
        
    def __call__(self, config_path):
        config = None
        try:
            if config_path is None or not os.path.exists(config_path):
                raise Exception("Invalid config file path or not exists.")

            with open(config_path, "r") as f:
                config = json.load(f)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
        return config


if __name__ == "__main__":
    config_path = f"{os.path.dirname(os.path.realpath(__file__))}/../configs/network_template.json"
    parser = Parser()
    config = parser(config_path)
    print(config)
