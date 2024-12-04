#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import util

def warc_to_wet_layer(warc_file_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", OVERWRITE=False):
    ret = list()
    try:
        wet_file_name = warc_file_name.replace(".warc.gz", ".warc.wet.gz")
        wat_file_name = warc_file_name.replace(".warc.gz", ".warc.wat.gz")

        src_warc_file_path = os.path.join(INPUT_FOLDER, warc_file_name)
        src_warc_file_path = util.to_real_path(src_warc_file_path, variables)

        dst_wet_file_path = os.path.join(OUTPUT_FOLDER, wet_file_name)
        dst_wet_file_path = util.to_real_path(dst_wet_file_path, variables)

        if os.path.exists(src_warc_file_path) and (OVERWRITE or not os.path.exists(dst_wet_file_path)):
            util.create_folder_by_file_path(dst_wet_file_path)

            # export SPARK_USER=$USER
            java_package = "./dependency/ia-hadoop-tools-jar-with-dependencies.jar"
            commandline = f"sudo java -jar {java_package} WEATGenerator -strictMode -skipExisting batch-id-xyz {src_warc_file_path}"
            exit_status1 = os.system(commandline)
            assert exit_status1 == 0

            tmp_base_path = os.path.dirname(src_warc_file_path)
            tmp_wet_file_path = os.path.join(tmp_base_path, "..", "wet/", wet_file_name)
            tmp_wat_file_path = os.path.join(tmp_base_path, "..", "wat/", wat_file_name)
            exit_status2 = os.system(f"sudo cp -f {tmp_wet_file_path} {dst_wet_file_path}")
            assert exit_status2 == 0

            os.system(f"sudo rm {tmp_wet_file_path}")
            os.system(f"sudo rm {tmp_wat_file_path}")

            ret = [wet_file_name]
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, )


if __name__ == "__main__":
    warc_file_name = "CC-MAIN-20221127073607-20221127103607-00007.warc.gz"
    INPUT_FOLDER = "$(input_data_folder)"
    OUTPUT_FOLDER = "$(output_data_folder)"
    output = warc_to_wet_layer(warc_file_name, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER)
    print(output)
