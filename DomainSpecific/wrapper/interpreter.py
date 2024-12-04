#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import collections
from core import DataType
from core import Layer, LayerType, JointType, LayerType2Func
from core import Network
from wrapper import Parser

class Interpreter:
    def __init__(self):
        self.fields = ("name", "description", "date", "version", "author", "input", "output", "layer")
        self.parser = Parser()

    def check_config(self, config):
        try:
            # fileds check.
            for field in self.fields:
                assert field in config

            data_name2type = collections.defaultdict(set)

            # check imported modules.
            module_data2type = dict()
            module_names = config.get("import", list())
            for name in module_names:
                sub_config = self.parser(f"./configs/{name.replace('.', '/')}.json")
                self.check_config(sub_config)
                for name, data in sub_config["input"].items():
                    module_data2type[name] = DataType[data["type"]]
                for name, data in sub_config["output"].items():
                    module_data2type[name] = DataType[data["type"]]

            # check input.
            inputs = config.get("input", dict())
            for name, data in inputs.items():
                assert data["type"] in DataType.__members__
                data_type = DataType[data["type"]]
                data_name2type[name].add(data_type)

            # check output.
            outputs = config.get("output", dict())
            for name, data in outputs.items():
                assert data["type"] in DataType.__members__
                data_type = DataType[data["type"]]
                data_name2type[name].add(data_type)

            # check layer.
            layers = config.get("layer", dict())
            for _, layer in layers.items():
                assert layer["type"] in LayerType.__members__ or layer["type"] in module_names
                input_names = layer["input"]
                output_names = layer["output"]
                if layer["type"] in LayerType.__members__:
                    layer_type = LayerType[layer["type"]]
                    func, input_types, output_types, enabled = LayerType2Func[layer_type]
                else:
                    input_types = list(map(lambda input_name: module_data2type[input_name], input_names))
                    output_types = list(map(lambda output_name: module_data2type[output_name], output_names))
                assert len(input_names) == len(input_types)
                assert len(output_names) == len(output_types)
                assert layer.get("joint", "Default") in JointType.__members__
                joint_type = JointType[layer.get("joint", "Default")]
                for name, data_type in zip(input_names, input_types):
                    if joint_type in (JointType.Map, JointType.FlatMap):
                        data_type = DataType(data_type.value + 10)
                    data_name2type[name].add(data_type)
                for name, data_type in zip(output_names, output_types):
                    if joint_type in (JointType.Map,):
                        data_type = DataType(data_type.value + 10)
                    data_name2type[name].add(data_type)

            # check joint.
            for data_name, data_type in data_name2type.items():
                for t1 in data_type:
                    for t2 in data_type:
                        assert DataType.belong(t1, t2) or DataType.belong(t2, t1)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
            sys.exit()

    def __call__(self, config_path):
        # parse config file.
        config = self.parser(config_path)

        # interpret network.
        network = Network()
        try:
            assert config is not None and isinstance(config, dict)
            config["base_dir"] = os.path.dirname(config_path)

            # check config.
            self.check_config(config)

            # imported modules.
            name2module = dict()
            module_names = config.get("import", list())
            for name in module_names:
                name2module[name] = self(f"./configs/{name.replace('.', '/')}.json")

            # input datas.
            input_datas = config.get("input", dict())
            network.set_input_names(list(input_datas.keys()))
            for name, data in input_datas.items():
                value = data.get("value")
                network.add_data(name, value)

            # output datas
            output_datas = config.get("output", dict())
            network.set_output_names(list(output_datas.keys()))

            # layers in graph.
            layers = config.get("layer", dict())
            for name, layer in layers.items():
                if layer["type"] in name2module:
                    value = name2module[layer["type"]]
                    # set params of sub-network.
                    for layers_param_name, param_value in layer.get("param", dict()).items():
                        layers_param_name = layers_param_name.split(".")
                        layers_name = layers_param_name[:-1]
                        param_name = layers_param_name[-1]
                        net = value
                        for layer_name in layers_name:
                            net = net.layers[layer_name]
                        net.param[param_name] = param_value
                else:
                    value = Layer(
                        type=layer["type"], 
                        joint=layer.get("joint", "Default"), 
                        repetition=layer.get("repetition", 1),
                        param=layer.get("param", dict()),
                        input_names=layer.get("input", list()),
                        output_names=layer.get("output", list()),
                    )
                network.add_layer(name, value)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
        return network


if __name__ == "__main__":
    config_path = f"{os.path.dirname(os.path.realpath(__file__))}/../configs/network_template.json"
    
    interpreter = Interpreter()
    network = interpreter(config_path)
    
    # compute in network.
    outputs = network()
    #from core import DataType
    #inputs = [["a", "b", "c", "d", "e"]]
    #outputs = network(inputs)
    
    print(outputs[0])
