import tempfile
import os

import pyarrow.parquet as pq
from tqdm import tqdm
from warcio.archiveiterator import ArchiveIterator
from loguru import logger

from .download_utils import download
from .algos.trafilatura_process import trafilatura_process, EmptyResultException
from .algos.fasttext_classifier import FASTTEXT_LID_176_URL, FastTextClassifier
from .algos.rule_based_filters.ruleset.refinedweb import apply_refinedweb_rules

LA_PROB_THRESHOLD = 0.65


def process_items(remote_cc_path, items, disable_tqdm=False):
    # items to dict
    uri_to_item = dict()
    for item in items:
        assert item["cc_path"] == remote_cc_path
        uri_to_item[item["uri"]] = item

    # main processing
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as tmp_dir:
        logger.info(f"downloading warc file {remote_cc_path}")
        local_cc_file = download(remote_cc_path, tmp_dir)
        # prepare lid model
        logger.info(f"downloading fasttext lid model {FASTTEXT_LID_176_URL}")
        local_lid_model = download(FASTTEXT_LID_176_URL, tmp_dir)
        lid_classfier = FastTextClassifier(local_lid_model)

        results = []
        with open(local_cc_file, "rb") as fd:
            for record in tqdm(ArchiveIterator(fd), disable=disable_tqdm):
                warc_type = record.rec_headers.get_header("WARC-Type")
                if warc_type != "response":
                    continue

                uri = record.rec_headers.get_header("WARC-Target-URI")
                if uri not in uri_to_item:
                    continue
                # article extraction
                raw_html = record.content_stream().read()
                try:
                    traf_res = trafilatura_process(raw_html)
                except EmptyResultException:
                    logger.warning(f"trafilatura: failed to convert record: {uri}")

                traf_text = traf_res["text"]
                # lid
                la, la_prob = lid_classfier.predict(traf_text)
                if la != "en" or la_prob < LA_PROB_THRESHOLD:
                    continue
                # rule based filter
                filtered_text = apply_refinedweb_rules(traf_text, la)
                if filtered_text is None:
                    continue

                result_item = {
                    **uri_to_item[uri],
                    "text": filtered_text,
                }

                results.append(result_item)

    return results


def process_file(index_path):
    items = pq.read_table(index_path).to_pylist()
    assert len(items) > 0
    cc_path = items[0]["cc_path"]
    return process_items(cc_path, items)
