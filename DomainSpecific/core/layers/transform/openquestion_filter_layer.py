#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import re
import gc
import requests
import fasttext
from gensim.utils import simple_preprocess
import pyarrow as pa
import pyarrow.parquet as pq
sys.path.append(".")
import util
import global_var

question_keywords = ("q&a", "q & a", "q:", "que:", "question:", "quiz:", "exam:", "examination:", "probe:", "request:", "challenge:", "test:", "query:", "survey:")
#question_keywords2 = ("what ", "where ", "why ", "when ", "who ", "whoes ", "how ", "\?")
question_keywords2 = ("what", "where", "why", "when", "who", "whoes", "how")
question_keywords += question_keywords2
question_keywords = set(map(lambda x: "[^a-zA-Z]" + x + "[^a-zA-Z]", question_keywords))
question_pattern = re.compile("|".join(question_keywords))

answer_keywords = ("q&a", "q & a", "a:", "ans:", "answer:", "solution:", "reply:", "response:", "result:", "outcome:", "explanation:", "conclusion:", "finding:", "assertion:", "statement:", "clarification:")
answer_keywords = set(map(lambda x: "[^a-zA-Z]" + x + "[^a-zA-Z]", answer_keywords))
answer_pattern = re.compile("|".join(answer_keywords))


def is_openquestion_by_model(text, model, thred=0.5):
    if model is None:
        return False
    if not isinstance(text, str) or len(text.strip()) == 0:
        return False
    try:
        x = " ".join(simple_preprocess(text))
        ret = model.predict(x)
        label, prob = ret[0][0], ret[1][0]
        return label != "__label__0"
    except:
        traceback.print_exc()
        return False

def check_yes_no_question(text_before, text_after):
    text_after = text_after.lower().strip()
    keywords = ("yes", "y", "no", "n")
    for keyword in keywords:
        if text_after.startswith(keyword) and not text_after[len(keyword)].isalnum():
            return True
    return False

def check_multiple_choise_question(text_before, text_after):
    combo_keywords_list = [
        ("a.",   "b.",   "c.",   "d."),
        ("a)",   "b)",   "c)",   "d)"),
        ("\na ", "\nb ", "\nc ", "\nd "),
        (">a<",  ">b<",  ">c<",  ">d<"),

        ("1.",   "2.",   "3.",   "4."),
        ("1)",   "2)",   "3)",   "4)"),
        ("\n1 ", "\n2 ", "\n3 ", "\n4 "),
        (">1<",  ">2<",  ">3<",  ">4<"),

        ("i.",   "ii.",   "iii.",   "iv."),
        ("i)",   "ii)",   "iii)",   "iv)"),
        ("\ni ", "\nii ", "\niii ", "\niv "),
        (">i<",  ">ii<",  ">iii<",  ">iv<"),
    ]
    text_before = text_before.lower().strip()
    for combo_keywords in combo_keywords_list:
        t = 0
        for combo_keyword in combo_keywords:
            t = text_before.find(combo_keyword, t)
            if t == -1:
                break
        if t != -1:
            return True
        #if combo_keywords[0] in text_before and combo_keywords[1] in text_before and combo_keywords[2] in text_before:
        #    return True
    return False

def check_fill_in_question(text_before, text_after):
    text_before = text_before.lower().strip()
    if "___" in text_before or "()" in text_before or "..." in text_before:
        return True
    return False

def check_quality(item):
    text = item["text"]
    lines = text.split("\n")
    lens = list(map(lambda l: len(l.strip()), lines))
    max_len = max(lens)

    #if max_len > 1024:
    if max_len > 2048:
        return False
    if max_len <= 128:
        return False

    if len(lens) <= 3:
        return False
    if len(lens) > 256:
        return False

    if len(text) < 256:
        return False
    if len(text) > 1024 * 16:
        return False

    if 1.0 * text.count(" ") / len(text) > 0.33:
        return False

    if 1.0 * text.count("  ") / len(text) > 0.1:
        return False

    if 1.0 * text.count("\t") / len(text) > 0.1:
        return False

    if 1.0 * text.count(".") / len(text) > 0.1:
        return False

    if 1.0 * text.count("-") / len(text) > 0.1:
        return False

    if 1.0 * text.count("#") / len(text) > 0.1:
        return False

    if 1.0 * text.count("|") / len(text) > 0.1:
        return False

    if 1.0 * text.count(",") / len(text) > 0.1:
        return False

    sl_cnt = 1.0 * len(list(filter(lambda x: len(x.strip()) <= 32, lines))) / len(lines)
    if sl_cnt > 0.67:
        return False

    return True

def openquestion_filter_layer(pq_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", OVERWRITE=False):
    ret = list()
    try:
        in_pq_path = os.path.join(INPUT_FOLDER, pq_name)
        in_pq_path = util.to_real_path(in_pq_path, variables)
        out_pq_path = os.path.join(OUTPUT_FOLDER, pq_name)
        out_pq_path = util.to_real_path(out_pq_path, variables)

        if os.path.exists(in_pq_path) and (OVERWRITE or not os.path.exists(out_pq_path)):
            util.create_folder_by_file_path(out_pq_path)

            # read parquet file.
            try:
                table = pq.read_table(in_pq_path)
                records = table.to_pylist()
            except:
                traceback.print_exc()
            
            # filter records containing open question.
            openquestion_records = list()
            for record_idx, record in enumerate(records):
                try:
                    text = record["text"]
                    text_low = text.lower()

                    if record["la"] != "en":
                        continue

                    #if item["la_prob"] < 0.65:
                    #    continue
                    #if text is None or len(text) < 64:
                    #    continue
                    #if text.count("\\u") >= 10:
                    #    continue

                    #if not check_quality(record):
                    #    continue

                    contain_question = len(question_pattern.findall(text_low)) >= 2
                    if not contain_question:
                        continue
                    
                    contain_answer = len(answer_pattern.findall(text_low)) >= 2
                    if not contain_answer:
                        continue

                    contain_openquestion = is_openquestion_by_model(text, global_var.ft_openquestion_model)
                    if not contain_openquestion:
                        continue

                    openquestion_records.append(record)
                except:
                    traceback.print_exc()

            # write parquet file.
            try:
                openquestion_table = pa.Table.from_pylist(openquestion_records)
                pq.write_table(openquestion_table, out_pq_path)
            except:
                traceback.print_exc()
            
            ret = [out_pq_path]
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, )


if __name__ == '__main__':
    snapshot = "CC-MAIN-2022-49"
    variables = {"workspace_dir": r"workspace", "worker_id": 0, "worker_num": 1}
    INPUT_FOLDER = "$(input_data_folder)"
    OUTPUT_FOLDER = "$(output_data_folder)"
    STORAGE_PATH = "resources/storage/llmstore.yaml"
    ret = openquestion_filter_layer(snapshot, variables=variables, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER, STORAGE_PATH=STORAGE_PATH)
    print(ret)
