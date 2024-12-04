#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import util

def to_line_file_layer(lines, file_path, variables=dict(), STORAGE_PATH=None):
    ret = None
    try:
        file_path = util.to_real_path(file_path, variables)
        util.create_folder_by_file_path(file_path)

        with open(file_path, "w") as f:
            for line in lines:
                f.write(line + "\n")

        if STORAGE_PATH is not None:
            util.upload_file_to_blob(STORAGE_PATH, file_path, file_path)

        ret = file_path
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    lines = ["line1", "line2"]
    file_path = "test.line"
    file_path = to_line_file_layer(lines, file_path)
    print(file_path)
