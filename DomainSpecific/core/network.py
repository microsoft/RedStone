#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
from core.layers import LayerType, util

class Network:
    def __init__(self):
        self.type = None
        self.input_names = list()
        self.output_names = list()
        self.datas = dict()
        self.layers = dict()

    def set_input_names(self, input_names):
        self.input_names = input_names

    def set_output_names(self, output_names):
        self.output_names = output_names

    def add_data(self, name, value):
        self.datas[name] = value

    def add_layer(self, name, value):
        self.layers[name] = value

    def next_layer(self, invisited_layer_names):
        for name in invisited_layer_names:
            layer = self.layers[name]
            input_names = layer.input_names
            if set(input_names) <= set(self.datas.keys()):
                input_values = [self.datas[input_name] for input_name in input_names]
                invisited_layer_names.remove(name)
                return layer, name, input_values
        return None
    
    def __call__(self, inputs=list(), worker_id=0, worker_num=1, variables=dict()):
        outputs = list()
        try:
            if len(inputs) == len(self.input_names):
                for name, value in zip(self.input_names, inputs):
                    self.add_data(name, value)
            
            invisited_layer_names = sorted(list(self.layers.keys()))
            while len(invisited_layer_names) > 0:
                item = self.next_layer(invisited_layer_names)
                if item is None:
                    raise Exception("There are some layers which misses input data.")
                layer, layer_name, input_values = item
                print(f"{layer_name} - input: {layer.input_names}, output: {layer.output_names}", flush=True)

                output_values = layer(input_values, worker_id=worker_id, worker_num=worker_num, variables=variables)
                for name, value in zip(layer.output_names, output_values):
                    self.add_data(name, value)
            outputs = [self.datas[output_name] for output_name in self.output_names]
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
        return outputs

    """
    def spark(self, inputs, spark_session, spark_context, worker_num=1, variables=dict()):
        from pyspark import TaskContext, StorageLevel

        def merge(x, n):
            if n == 0:
                return []
            elif n == 1:
                return [x]
            elif n == 2:
                return list(x)
            else:
                for _ in range(n - 2):
                    x = x[0] + x[1:]
                return list(x)
        
        def func(layer, input, worker_id, worker_num, variables):
            input = list(input)
            assert len(input) == 1
            input = input[0]
            output = layer(input, worker_id=worker_id, worker_num=worker_num, variables=variables)
            return [output]
        
        outputs = list()
        try:
            if len(inputs) == len(self.input_names):
                for name, value in zip(self.input_names, inputs):
                    self.add_data(name, value)
            
            for name, data in self.datas.items():
                input_rdd = spark_context.parallelize(worker_num * [data], worker_num)
                # Avoid recomputation, because each rdd may be used multiple times.
                input_rdd.persist(StorageLevel.MEMORY_AND_DISK)
                self.add_data(name, input_rdd)
            
            invisited_layer_names = sorted(list(self.layers.keys()))
            while len(invisited_layer_names) > 0:
                item = self.next_layer(invisited_layer_names)
                if item is None:
                    raise Exception("There are some layers which misses input data.")
                layer, layer_name, input_values = item

                input_rdds = None
                for i, input_rdd in enumerate(input_values):
                    input_rdds = input_rdd if i == 0 else input_rdds.zip(input_rdd)
                input_rdds = input_rdds.map(lambda x: merge(x, len(layer.input_names)))

                native_io = True
                if native_io:
                    output_rdds = input_rdds.mapPartitionsWithIndex(
                        lambda worker_id, input: 
                        func(layer, input, worker_id, worker_num, variables), preservesPartitioning=True
                    )
                else:# (Deprecated)
                    #if layer.type in (LayerType.To_Line_File, LayerType.To_Jsonl_File, LayerType.To_Parquet_File):
                    if layer.type == LayerType.To_Line_File:
                        inputs = input_rdds.collect()
                        outputs = list()
                        for worker_id, input in enumerate(inputs):
                            variables["worker_id"] = worker_id
                            variables["worker_num"] = worker_num
                            assert len(input) == 2
                            file_path = util.to_real_path(input[1], variables)
                            
                            spark_context.parallelize(input[0], 1).saveAsTextFile(file_path)
                            #rdd = spark_context.parallelize(input[0], 1)
                            #rdd.toDF().write.mode("overwrite").text(file_path)
                            #rdd.toDF().write.mode("overwrite").json(file_path)
                            #rdd.toDF().write.mode("overwrite").parquet(file_path)
                            
                            output = [file_path]
                            outputs.append(output)
                        output_rdds = spark_context.parallelize(outputs, worker_num)
                    #elif layer.type in (LayerType.From_Line_File, LayerType.From_Jsonl_File, LayerType.From_Parquet_File):
                    elif layer.type == LayerType.From_Line_File:
                        inputs = input_rdds.collect()
                        outputs = list()
                        for worker_id, input in enumerate(inputs):
                            variables["worker_id"] = worker_id
                            variables["worker_num"] = worker_num
                            assert len(input) == 1
                            file_path = util.to_real_path(input[0], variables)
                            
                            lines = spark_context.textFile(file_path).collect()
                            #rdd = spark_session.read.option("mode", "DROPMALFORMED").text(file_path).rdd
                            #rdd = spark_session.read.option("mode", "DROPMALFORMED").json(file_path).rdd
                            #rdd = spark_session.read.option("mode", "DROPMALFORMED").parquet(file_path).rdd
                            #lines = rdd.collect()
                            
                            output = [lines]
                            outputs.append(output)
                        output_rdds = spark_context.parallelize(outputs, worker_num)
                    else:
                        output_rdds = input_rdds.mapPartitionsWithIndex(
                            lambda worker_id, input: 
                            func(layer, input, worker_id, worker_num, variables), preservesPartitioning=True
                        )

                # Avoid recomputation, because each rdd may be used multiple times.
                output_rdds.persist(StorageLevel.MEMORY_AND_DISK)
                for i, name in enumerate(layer.output_names):
                    output_rdd = output_rdds.map(lambda _:_[i])
                    # Avoid recomputation, because each rdd may be used multiple times.
                    output_rdd.persist(StorageLevel.MEMORY_AND_DISK)
                    self.add_data(name, output_rdd)

                print(f"{layer_name} - {layer.input_names}, {layer.output_names}", flush=True)
            outputs = [self.datas[output_name].collect() for output_name in self.output_names]
        except KeyboardInterrupt:
            sys.exit()
        except Exception as ex:
            traceback.print_exc()
        return outputs
    """


if __name__ == "__main__":
    network = Network()
    print(network)
