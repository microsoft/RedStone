# Redstone General CC

Library for reproducing the general CC part of RedStone dataset from the released index Parquet file.

## How to use

### Install the lib

```bash
pip install "redstone-cc @ git+https://github.com/microsoft/redstone#subdirectory=general_cc/"
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

- About trafilatura processing failures
    - Our original data was processed using `trafilatura` version 1.8.1, which may behave differently from the current version. If you need to reproduce our result exactly, please consider manually pinning the version of trafilatura.
