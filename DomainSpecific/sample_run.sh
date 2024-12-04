#!/usr/bin/env bash

# --------------------------------------------------------------------------------------------------------------
# Part 1 - knowledge extraction from html page.
# step 1 - download CC warc url list.
#Put one (or lots of) url(s) of Common Crawl WARC file to workspace/urls.CC-MAIN-2023-23.txt file.
#such as:
wget -P workspace https://data.commoncrawl.org/crawl-data/CC-MAIN-2023-23/warc.paths.gz
gzip -d workspace/warc.paths.gz
mv workspace/warc.paths workspace/urls.CC-MAIN-2023-23.txt

# step 2 - download CC warc.
python submit.py --run_mode MultiProcess --network_path ./configs/cc_warc_download.CC-MAIN-2023-23.json
cat ./workspace/cc_warcs/CC-MAIN-2023-23/paths.*.txt > ./workspace/cc_warcs/CC-MAIN-2023-23/paths.txt

# step 3 - prefilter CC warc.
python submit.py --run_mode MultiProcess --network_path ./configs/cc_warc_filter.CC-MAIN-2023-23.json
cat ./workspace/cc_filtered_warc/CC-MAIN-2023-23/paths.*.txt > ./workspace/cc_filtered_warc/CC-MAIN-2023-23/paths.txt

# step 4 - extract code from html tag.
python submit.py --run_mode MultiProcess --network_path ./configs/cc_warc_to_wet.code.CC-MAIN-2023-23.json

# step 5 - extract math from html tag.
python submit.py --run_mode MultiProcess --network_path ./configs/cc_warc_to_wet.math.CC-MAIN-2023-23.json

# --------------------------------------------------------------------------------------------------------------
# Part 2 - knowledge extraction from text page.
# extract text doc from CC html doc, filter text doc, and save them to parquet files.
# please refer to GeneralDomain processing to get the text pages in parquet format, then uncomment the below commands for further processing.

# step 1 - extract math from plain text.
#python submit.py --run_mode MultiProcess --network_path ./configs/cc_math_filter.CC-MAIN-2023-23.json

# step 2 - extract open questions from plain text.
#python submit.py --run_mode MultiProcess --network_path ./configs/cc_openquestion_filter.CC-MAIN-2023-23.json
