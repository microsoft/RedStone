#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import re
import requests
import fasttext
from gensim.utils import simple_preprocess
import pyarrow as pa
import pyarrow.parquet as pq
import util
import global_var

whilte_list = {r"\\displaystyle", r"\\alpha", r"\\beta", r"\\gamma", r"\\delta", r"\\zeta", r"\\eta", r"\\iota", r"\\kappa", r"\\mu", r"\\nu", r"\\xi", r"\\rho", r"\\tau", r"\\phi", r"\\chi", r"\\psi", r"\\omicron", r"\\epsilon", r"\\pi", r"\\lambda", r"\\omega", r"\\sigma", r"\\theta", r"\\vartheta", r"\\times", r"\\cdot", r"\\dot", r"\\div", r"\\frac", r"\\log", r"\\exp", r"\\poly", r"\\eq", r"\\neq", r"\\leq", r"\\geq", r"\\approx", r"\\infty", r"\\int", r"\\sum", r"\\lim", r"\\begin", r"\\subset", r"\\supset", r"\\top", r"\\star", r"\\sim", r"\\simeq", r"\\ne", r"\\ll", r"\\gg", r"\\pm", r"\\mp", r"\\triangleleft", r"\\triangleright", r"\\ast", r"\\circ", r"\\bullet", r"\\oplus", r"\\odot", r"\\otimes", r"\\ominus", r"\\oslash", r"\\bigcirc", r"\\wr", r"\\dagger", r"\\bigtriangleup", r"\\bigtriangledown", r"\\setminus", r"\\sqcup", r"\\wedge", r"\\dotplus", r"\\centerdot", r"\\ltimes", r"\\rtimes", r"\\prod", r"\\coprod", r"\\iint", r"\\iiint", r"\\iiiint", r"\\idotsint", r"\\bigoplus", r"\\big", r"\\oint", r"\\rightarrow", r"\\to", r"\\leftarrow", r"\\gets", r"\\uparrow", r"\\downarrow", r"\\forall", r"\\exists", r"\\pmod", r"\\cup", r"\\cap", r"\\hat", r"\\acute", r"\\check", r"\\grave", r"\\vec", r"\\ddot", r"\\tilde", r"\\breve", r"\\mathring", r"\\land", r"\\lor", r"\\lnot", r"\\in", r"\\smile", r"\\frown", r"\\infty", r"\\mid", r"\\sin", r"\\cos", r"\\tan", r"\\equiv", r"\\circ", r"\\dfrac", r"\\prec", r"\\preccurlyeq", r"\\sqrt",}
black_list = {r"\\text", r"\\if", r"\\local", r"\\usr", r"\\include", r"\\lib", r"\\bin", r"\\url", r"\\program", r"\\microsoft", r"\\temp", r"\\windows", r"\\documents", r"\\users", r"\\my", r"\\the",}
keywords1 = whilte_list - black_list
keywords1 = set(map(lambda x: x + "[^a-zA-Z]", keywords1))

keywords2 = {r"\+", r"\-", r"\*", r"\/", r"\%", r"\=", r"\!\=", r"\<", r"\>", r"\^", r"\_", r"\(", r"\)", r"\[", r"\]", r"\{", r"\}", r"\|\|", r"\&\&", r"sqrt", r"sum", r"int", r"\$", r"\<math\>", r"\[math\]", }

pattern0 = re.compile(r"\\[A-Z]{0,9}[a-z]{2,9}")
pattern1 = re.compile("|".join(keywords1))
pattern2 = re.compile("|".join(keywords2))

def ismath_by_model(text, model, thred=0.5):
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

def math_filter_layer(pq_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", OVERWRITE=False):
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
            except:
                traceback.print_exc()
            
            # filter records containing math.
            records = list()
            for record in table.to_pylist():
                try:
                    text = record["text"]

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

                    symbols0 = set(pattern0.findall(text))
                    if len(symbols0) <= 0:
                        continue

                    symbols1 = set(pattern1.findall(text.lower()))
                    symbols1 = set(map(lambda sym: sym[:-1], symbols1))
                    if len(symbols1) <= 0:
                        continue

                    symbols2 = set(pattern2.findall(text.lower()))
                    if len(symbols1) == 1 and len(symbols2) <= 0:
                        continue

                    ismath = len(symbols1) >= 5 or ismath_by_model(text, global_var.ft_math_model)
                    if not ismath:
                        continue

                    records.append(record)
                except:
                    traceback.print_exc()

            # write parquet file.
            try:
                table = pa.Table.from_pylist(records)
                pq.write_table(table, out_pq_path)
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
    ret = math_filter_layer(snapshot, variables=variables, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER, STORAGE_PATH=STORAGE_PATH)
    print(ret)
