#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import sys
import traceback

# Spec of adding a new layer:
# 1. the layer function should be registered in __init__.py file of current folder.
# 2. the layer function should return tuple value, even though the return value is empty.
# 3. the layer function should contain a "variables" variable in dictionary type for the access of global shared variables.
# 4. It's better to implement the unit test and put it to the "__main__" function.
# 5. It's better to have exception handling for the function logic.
# 6. It's better to end with "_layer" for the name of function.
# 7. It's better to write comments for the function of purpose, input and output.
# 8. It's better to be lowercase for the name of input datas.
# 9. It's better to be uppercase for the name of input parameters.

def template_layer(input, variables=dict(), PARAM=None):
    ret = None
    try:
        ret = input
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == "__main__":
    input = None
    output = template_layer(input)
