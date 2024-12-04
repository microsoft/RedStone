import argparse

import pyarrow as pa
import pyarrow.parquet as pq
from loguru import logger

from .process import process_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("index_path")
    parser.add_argument("output_path")
    args = parser.parse_args()

    logger.info(f"input path: {args.index_path}")
    logger.info(f"output path: {args.output_path}")
    logger.info("processing...")
    res = process_file(args.index_path)

    logger.info("writing results...")
    table = pa.Table.from_pylist(res)
    pq.write_table(table, args.output_path)
    logger.info("finished.")


if __name__ == "__main__":
    main()
