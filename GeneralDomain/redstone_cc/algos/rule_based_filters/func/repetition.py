from collections import Counter

import numpy as np
from nltk.util import ngrams


def repetition_ngram_top_char_frac(words, n: int):
    items = list(ngrams(words, n))
    counter = Counter(items)
    most_common = counter.most_common(1)
    if len(most_common) == 0:
        return 0
    most_common_ngram, count = most_common[0]
    if count == 1:
        return 0
    total_chars = sum(len(w) for w in words)
    top_chars = sum(len(w) for w in most_common_ngram) * count

    return top_chars / total_chars


def repetition_ngram_dup_char_frac(words, n: int):
    items = list(ngrams(words, n))
    counter = Counter(items)

    flag_dup = np.zeros(len(words), dtype="bool")
    for i, item in enumerate(items):
        if counter[item] > 1:
            flag_dup[i : i + n] = True
    total_chars = sum(len(w) for w in words)
    dup_chars = sum(len(w) for i, w in enumerate(words) if flag_dup[i])
    return dup_chars / total_chars


def repetition_line_dup_frac(lines):
    if len(lines) == 0:
        return 0, 0

    dup_lines = 0
    dup_chars = 0
    counter = Counter(lines)
    for line, count in counter.items():
        if count > 1:
            dup_lines += count
            dup_chars += len(line) * count
    total_chars = sum(len(line) for line in lines)
    if total_chars == 0:
        return 0, 0

    return dup_lines / len(lines), dup_chars / total_chars


def test_ngram_top():
    words = "a b c a b d a b".split()
    res = repetition_ngram_top_char_frac(words, 2)
    assert res == 6 / len(words)

    # no repetition
    res = repetition_ngram_top_char_frac(words, 3)
    assert res == 0

    words = "a b c a b c a b".split()
    res = repetition_ngram_top_char_frac(words, 3)
    assert res == 6 / len(words)


def test_ngram_dup():
    words = "a b c a b d a b".split()
    res = repetition_ngram_dup_char_frac(words, 2)
    assert res == 6 / len(words)

    words = "a b c a b c a b".split()
    res = repetition_ngram_dup_char_frac(words, 3)
    assert res == 1


def test_dup_line():
    lines = ["a", "b", "c"]
    frac, char_frac = repetition_line_dup_frac(lines)
    assert frac == 0 and char_frac == 0
    lines = []
    frac, char_frac = repetition_line_dup_frac(lines)
    assert frac == 0 and char_frac == 0
    lines = ["", "", ""]
    frac, char_frac = repetition_line_dup_frac(lines)
    assert frac == 0 and char_frac == 0
    lines = ["abc", "de", "abc"]
    frac, char_frac = repetition_line_dup_frac(lines)
    assert frac == 2 / 3 and char_frac == 6 / 8
