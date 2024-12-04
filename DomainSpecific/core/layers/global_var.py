#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
import traceback
#import torch
import fasttext
from transformers import AutoTokenizer, RobertaForSequenceClassification
from dependency.gpt_api import GPTAPI

try:
    # silences warnings as the package does not properly use the python 'warnings' package
    # see https://github.com/facebookresearch/fastText/issues/1056
    fasttext.FastText.eprint = lambda *args,**kwargs: None
except:
    pass

"""
class OpenQuestionModel:
    def __init__(self, pretrained_model_path, token_model_path="cardiffnlp/twitter-roberta-base-emotion", local_files_only=False):
        # load tokenizer model.
        self.tokenizer = AutoTokenizer.from_pretrained(token_model_path)

        # load trained model.
        self.model = RobertaForSequenceClassification.from_pretrained(pretrained_model_path, local_files_only=local_files_only)

    def run(self, text, thred=0.5, max_length=512):
        # tokenization.
        inputs = self.tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=max_length)

        # inference.
        with torch.no_grad():
            logits = self.model(**inputs).logits
        logits = logits.softmax(dim=1)[0]
        predicted_idx = logits.argmax().item()
        predicted_label = self.model.config.id2label[predicted_idx]
        predicted_conf = logits[predicted_idx].item()
        if predicted_label == "LABEL_0" and predicted_conf < thred:
            predicted_idx = 1
            predicted_label = "LABEL_1"
        #return predicted_idx, predicted_label, predicted_conf
        return predicted_label
"""

# language detection by fasttext.
LID_MODEL_PATH = "./dependency/models/lid.176.bin"
if os.path.exists(LID_MODEL_PATH):
    lid_model = fasttext.load_model(LID_MODEL_PATH)
else:
    lid_model = None

# math detection by fasttext.
MATH_FT_MODEL_PATH = "./dependency/models/math.bin"
if os.path.exists(MATH_FT_MODEL_PATH):
    ft_math_model = fasttext.load_model(MATH_FT_MODEL_PATH)
else:
    ft_math_model = None

# openquestion detection by fasttext.
OPENQUESTION_MODEL_PATH = "./dependency/models/openquestion.bin"
if os.path.exists(OPENQUESTION_MODEL_PATH):
    ft_openquestion_model = fasttext.load_model(OPENQUESTION_MODEL_PATH)
else:
    ft_openquestion_model = None

# multiple-choice question detection by fasttext.
MCQ_MODEL_PATH = "./dependency/models/mcq.bin"
if os.path.exists(MCQ_MODEL_PATH):
    ft_mcq_model = fasttext.load_model(MCQ_MODEL_PATH)
else:
    ft_mcq_model = None

"""
# multiple-choice question detection by pytorch.
MCQ_PT_MODEL_PATH = "./dependency/models/mcq.pytorch"
if os.path.exists(MCQ_PT_MODEL_PATH):
    py_mcq_model = OpenQuestionModel(MCQ_PT_MODEL_PATH, local_files_only=True)
else:
    py_mcq_model = None
"""

# gpt agent.
gpt_api = GPTAPI()
