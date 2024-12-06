# Redstone General CC

Library for reproducing the general domain part of RedStone dataset from the released index Parquet file.

## How to use

### Install the lib

```bash
pip install "redstone-cc @ git+https://github.com/microsoft/RedStone#subdirectory=GeneralDomain/"
```

### From CLI

```bash
python -m redstone_cc {input_index_path} {output_parquet_path}
```

### From python

```python3
from redstone_cc import process_file

index_file_path = '/path/to/index/file'
items = process_file(index_file_path)

for item in items:
    print(item['uri'], item['text'])
```

## FAQ

- About deduplication steps
    - The `Local**` python class under `algos.deduplciation` is intended for testing purposes only. Due to the scale of the data, we recommended running deduplication steps with a cluster computing system like Spark, you can find some example in the `spark-dedup-example` folder.

- About WET-based data processing
    - WET-based data processing are mainly consists of various deduplication steps. Specifically, the line-wise SHA1 deduplication step from CCNet requires at least a snapshot of the CC data to achieve good results. Therefore, WET related processing code is not included in our repo.

- About trafilatura processing failures
    - Our original data was processed using `trafilatura` version 1.8.1, which may behave differently from the current version. If you need to reproduce our result exactly, please consider manually pinning the version of trafilatura.
