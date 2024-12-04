import unicodedata

import regex

RE_PUNCT = regex.compile(r"\p{P}")
RE_URL = regex.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)

RE_LINE_SEPARATORS = regex.compile(r"(\p{Zl}|\p{Zp})+")
RE_SPACE_SEPARATORS = regex.compile(r"\p{Zs}+")


def remove_url(text):
    return RE_URL.sub("", text)


def remove_consecutive_new_lines(text):
    return RE_LINE_SEPARATORS.sub("\n", text)


def remove_punct(text):
    return RE_PUNCT.sub("", text)


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = text.strip()
    text = remove_consecutive_new_lines(text)
    text = RE_SPACE_SEPARATORS.sub(" ", text)
    return text
