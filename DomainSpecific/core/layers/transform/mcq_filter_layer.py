#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import re
import json
import fasttext
import requests
from io import BytesIO
from gensim.utils import simple_preprocess
from warcio.limitreader import LimitReader
from warcio.warcwriter import WARCWriter
from warcio.archiveiterator import ArchiveIterator
import util
import global_var


def detect_lang(text):
    try:
        LID_WIN_SIZE = 256
        text = ''.join(text.split())
        span_start, span_end = 0, len(text)
        if len(text) > LID_WIN_SIZE:
            mid = len(text) // 2
            mid_win = LID_WIN_SIZE // 2
            span_start = max(0, int(mid - mid_win))
            span_end = min(len(text), int(mid + mid_win))
        det_text = text[span_start: span_end]
        res = global_var.lid_model.predict(det_text)
        lang = res[0][0].replace("__label__", "")
        prob = float(res[1][0])
        return lang
    except:
        return "unkown"


def detect_choice_exercise_by_rule(uri, html):
    uri = uri.lower()
    html = html.lower()
    contain_cnt = 0

    keywords_in_text = [b"choice question"]
    for keyword in keywords_in_text:
        if keyword in html:
            contain_cnt += 1
            break

    combo_keywords_in_text = [
        (b"a.",   b"b.",   b"c.",   b"d."),
        (b"a)",   b"b)",   b"c)",   b"d)"),
        (b"\na ", b"\nb ", b"\nc ", b"\nd "),
        (b">a<",  b">b<",  b">c<",  b">d<"),

        (b"1.",   b"2.",   b"3.",   b"4."),
        (b"1)",   b"2)",   b"3)",   b"4)"),
        (b"\n1 ", b"\n2 ", b"\n3 ", b"\n4 "),
        (b">1<",  b">2<",  b">3<",  b">4<"),

        (b"i.",   b"ii.",   b"iii.",   b"iv."),
        (b"i)",   b"ii)",   b"iii)",   b"iv)"),
        (b"\ni ", b"\nii ", b"\niii ", b"\niv "),
        (b">i<",  b">ii<",  b">iii<",  b">iv<"),
    ]

    for combo_keyword in combo_keywords_in_text:
        if combo_keyword[0] in html and combo_keyword[1] in html and combo_keyword[2] in html and combo_keyword[3] in html:
            contain_cnt += 1
            break

    return contain_cnt == 2


def detect_choice_exercise_by_ft_model(uri, text, thred=0.5):
    try:
        if not isinstance(text, str) or len(text.strip()) == 0:
            return False
        x = " ".join(simple_preprocess(text))
        ret = global_var.ft_mcq_model.predict(x)
        label, prob = ret[0][0], ret[1][0]
        if label == "__label__0" and prob < thred:
            return True
        return label == "__label__1"
    except:
        return False

"""
def detect_choice_exercise_by_pt_model(uri, text, thred=0.5):
    try:
        if not isinstance(text, str) or len(text.strip()) == 0:
            return False
        label = global_var.py_mcq_model.run(text, thred)
        return label == "LABEL_1"
    except:
        return False
"""


def detect_choice_exercise_by_LLM(text, engine=None):
    system = '''
You will be given a text converted from a webpage. Your task is to detect whether it contains choice question by responding with 'yes' or 'no'.
'''
    answer = global_var.gpt_api.run(system=system, question=text, engine=engine)
    answer = answer.lower().strip()
    if answer.startswith("yes"):
        return True
    elif answer.startswith("no"):
        return False
    else:
        return False


def LCS(str1, str2):
    m = len(str1)
    n = len(str2)

    dp = [[0 for _ in range(n+1)] for _ in range(m+1)]

    for i in range(1, m+1):
        for j in range(1, n+1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return round(1.0 * dp[m][n] / n, 6)


def localize_choice_exercise_by_LLM(text, engine=None):
    system = '''
Purpose:
Create a multiple-choice question dataset.

Task:
Extract all multiple-choice questions from the provided text.

Requirements:
1. If the given text does not contain multiple-choice questions, respond only with "No multiple-choice questions found".
2. Do not modify the original multiple-choice questions.
3. Ensure all multiple-choice questions are copied without omissions.
4. Ensure all multiple-choice questions are copied in order.
5. Ensure all multiple-choice questions are copied under the original layout.
6. Copy the questions along with their options.
7. If answers and explanations are provided, copy them as well.
8. If source materials or reading passage is provided, copy it as well.
9. Don't add content not from original given text.

Please strictly adhere to these requirements while performing the task.
'''
    exercises = global_var.gpt_api.run(system=system, question=text, engine=engine)
    exercises = exercises.strip()
    if len(exercises) == 0 or "no multiple-choice question" in exercises.lower():
        return None
    else:
        exercises = exercises.replace("Multiple Choice Questions\n", "")
        exercises = exercises.replace("Multiple-choice questions:\n", "")
        exercises = exercises.replace("No other multiple-choice questions found.", "")
        exercises = exercises.replace("No other multiple-choice questions found in the text.", "")
        exercises = exercises.replace("No multiple-choice questions found.", "")
        exercises = exercises.replace("No more multiple-choice questions found.", "")

        sim = LCS(text, exercises)
        if sim < 0.9:
            return None
        else:
            return exercises


# rule + model + GPT3.5 turbor.
def mcq_filter_layer(wet_file_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", OVERWRITE=False):
    ret = list()
    try:
        src_wet_file_path = os.path.join(INPUT_FOLDER, wet_file_name)
        src_wet_file_path = util.to_real_path(src_wet_file_path, variables)
        jsonl_file_name = wet_file_name.replace(".warc.wet.gz", ".jsonl")
        dst_jsonl_file_path = os.path.join(OUTPUT_FOLDER, jsonl_file_name)
        dst_jsonl_file_path = util.to_real_path(dst_jsonl_file_path, variables)

        if os.path.exists(src_wet_file_path) and (OVERWRITE or not os.path.exists(dst_jsonl_file_path)):
            items = list()
            with open(src_wet_file_path, "rb") as input:
                records = ArchiveIterator(input, arc2warc=False)
                for id, record in enumerate(records):
                    if record.rec_type == "conversion":
                        try:
                            # read raw html.
                            uri = record.rec_headers["WARC-Target-URI"]
                            bs = record.content_stream().read()
                            if bs is None:
                                continue

                            text = str(bs, "utf-8")
                            if text is None:
                                continue

                            # 1st round filter.
                            round1_contain_exercise = detect_choice_exercise_by_rule(uri, bs)
                            if not round1_contain_exercise:
                                continue

                            # 2nd round filter.
                            round2_contain_exercise = detect_choice_exercise_by_ft_model(uri, text, thred=0.825)
                            if not round2_contain_exercise:
                                continue
                            #round2_contain_exercise = detect_choice_exercise_by_pt_model(uri, text, thred=0.99)
                            #if not round2_contain_exercise:
                            #    continue

                            """
                            # 3rd round filter.
                            round3_contain_exercise = detect_choice_exercise_by_LLM(text, "gpt-35-turbo")
                            if not round3_contain_exercise:
                                continue
                            """

                            item = dict()
                            item["uri"] = uri
                            item["text"] = text
                            lang = detect_lang(text)
                            item["lang"] = lang
                            #exercises = localize_choice_exercise_by_LLM(text, "gpt-35-turbo")
                            #item["exercises"] = exercises
                            items.append(item)
                        except:
                            traceback.print_exc()
                            pass
            with open(dst_jsonl_file_path, "w") as output:
                for item in items:
                    output.write(json.dumps(item) + "\n")
            ret = [dst_jsonl_file_path]
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, )


if __name__ == '__main__':
    wet_file_name = "CC-MAIN-20210115134101-20210115164101-00005_5.warc.wet.gz"
    variables = {"workspace_dir": r"workspace", "worker_id": 0, "worker_num": 1}
    INPUT_FOLDER = "$(input_data_folder)"
    OUTPUT_FOLDER = "$(output_data_folder)"
    ret = mcq_filter_layer(wet_file_name, variables=variables, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER, OVERWRITE=True)
    print(ret)
