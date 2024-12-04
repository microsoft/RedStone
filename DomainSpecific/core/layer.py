#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
from enum import Enum
from tqdm import tqdm
from core.layers import LayerType, LayerType2Func

class JointType(Enum):
    Default = 0 # Only process data as whole (frequently used in data IO and control layers).
    Map     = 1 # Firstly split data list into data unit, then process data unit to any type, finnaly return the list of processed data unit.
    FlatMap = 2 # Firstly split data list into data unit, then process data unit to list type, then concat the whole processed data lists, finnally return the concated data list.

class Layer:
    def __init__(self, type, joint=JointType.Default, repetition=1, param=dict(), input_names=list(), output_names=list()):
        self.type = type if isinstance(type, LayerType) else LayerType[type]
        self.func, self.input_types, self.output_types, self.enabled = LayerType2Func[self.type]
        self.joint = joint if isinstance(joint, JointType) else JointType[joint]
        self.repetition = repetition
        self.param = param
        self.input_names = input_names
        self.output_names = output_names

    def __call__(self, inputs, worker_id=0, worker_num=1, variables=dict()):
        outputs = list()
        try:
            variables["worker_id"] = worker_id
            variables["worker_num"] = worker_num

            if not isinstance(inputs, list):
                raise Exception(f"The inputs of layer should be list data type.")
            if len(inputs) != len(self.input_types):
                raise Exception(f"The number of inputs is not {len(self.input_types)}.")
            for i, (data, input_type) in enumerate(zip(inputs, self.input_types)):
                # TODO: add the check of input type.
                # check the data type of input.
                #if data.type != DataType[input_type]:
                #    raise Exception(f"The {i}th data, whose type is {data.type.name}, does not match the input type {input_type}")
                # Condition of empty input.
                if data is None:
                    outputs = [None for _ in self.output_types]
                    return outputs

            # TODO: to address the situation of repetition > 1.
            for i in range(self.repetition):
                if self.joint == JointType.Default:
                    values = list(self.func(*inputs, variables, **self.param))
                else:
                    n = min([len(data) for data in inputs])
                    if n != max([len(data) for data in inputs]):
                        raise Exception(f"Element amount of input datas are not equal.")

                    values = [[] for _ in self.output_types]
                    for i in tqdm(range(n), desc=f"Layer: {self.type.name}, worker_id: {worker_id}/{worker_num}"):
                        _values = self.func(*[data[i] for data in inputs], variables, **self.param)
                        for value, _value in zip(values, _values):
                            if _value is None:
                                continue
                            if self.joint == JointType.Map:
                                value.append(_value)
                            elif self.joint == JointType.FlatMap:
                                if not isinstance(_value, list):
                                    raise Exception(f"The output of layer should be list data type.")
                                value.extend(_value)
                            else:
                                raise Exception(f"Using unsupported joint type for {self.type.name} layer.")

                outputs = values
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
        return outputs


if __name__ == "__main__":
    inputs = [["a", "b", "c", "d", "e"]]
    layer = Layer(LayerType.Data_Sample, param={"N": 2})
    outputs = layer(inputs)
    print(layer)
