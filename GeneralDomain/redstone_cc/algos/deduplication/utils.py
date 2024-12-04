import unicodedata
import re
import string

import regex
import ftfy
from nltk import ngrams

DIGIT_RE = regex.compile(r"\d")
PUNCT_OR_NON_PRINTING_CHARS_RE = regex.compile(r"(\p{P}|\p{C})")


def ccnet_normalize(line) -> str:
    line = line.strip()
    if not line:
        return line
    # normalize
    line = unicodedata.normalize("NFKC", line)
    # case
    line = line.lower()
    # numbers
    line = DIGIT_RE.sub("0", line)
    line = PUNCT_OR_NON_PRINTING_CHARS_RE.sub("", line)
    return line


SLIMPAJAMA_LENGTH_THRESHOLD = 200


# https://github.com/Cerebras/modelzoo/blob/de67aaec12ba684ebedc6fb841e0c4d0ff8cd2e8/modelzoo/transformers/data_processing/slimpajama/preprocessing/filter.py#L28
def slimpajama_tokenize(text, num_ngrams=13):
    text = ftfy.fix_text(text, normalization="NFC")
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) < SLIMPAJAMA_LENGTH_THRESHOLD:
        return
    tokens = map(lambda x: "".join(x), ngrams(text, num_ngrams))
    return tokens


def spm_tokenize(text, spm_model, num_ngrams=5):
    text = text.lower()
    tokens = spm_model.encode(text, out_type=str)
    tokens = ngrams(tokens, num_ngrams)
    tokens = {" ".join(t).strip() for t in tokens}
    return tokens
