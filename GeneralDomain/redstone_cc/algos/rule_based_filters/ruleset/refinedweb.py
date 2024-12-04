import regex
from .gopher import gopher_filter
from ..model.document import Document
from ..func.line import (
    line_all_numeric,
    line_uppercase_ratio,
    line_refinedweb_counter,
    line_regex_match,
)

EXCLUDE_PATTERNS = (
    "^sign in",
    "^sign-in",
    "^sign up",
    "^sign-up",
    "read more...$",
    "items in cart",
)
EXCLUDE_PATTERNS = (regex.compile(x) for x in EXCLUDE_PATTERNS)


def refinedweb_filter(doc: Document):
    violations = gopher_filter(doc)
    # line
    res = []
    for i, line in enumerate(doc.sents):
        upper_ratio = line_uppercase_ratio(line)
        if upper_ratio > 0.6:
            res.append(i)
    violations.line("line_upper_ratio", res)

    res = []
    for i, line in enumerate(doc.normalized_sents):
        if line_all_numeric(line):
            res.append(i)
    violations.line("line_all_numeric", res)

    res = []
    for i, line in enumerate(doc.normalized_sents):
        if line_refinedweb_counter(line):
            res.append(i)
    violations.line("line_refinedweb_counter", res)

    res = []
    for i, line in enumerate(doc.normalized_sents):
        if len(line.split()) == 1:
            res.append(i)
    violations.line("line_one_word", res)

    res = []
    for i, line in enumerate(doc.normalized_sents):
        if line_regex_match(line, EXCLUDE_PATTERNS):
            res.append(i)
    violations.line("line_exclude_patterns", res)

    total_words = sum(len(line.split()) for line in doc.normalized_sents)
    excluded_words = sum(
        len(line.split())
        for i, line in enumerate(doc.normalized_sents)
        if i in violations.excluded_lines
    )
    if excluded_words / total_words > 0.05:
        violations.doc("line_document_discarded")

    return violations


def apply_refinedweb_rules(text, lang):
    doc = Document(text, lang)
    violations = refinedweb_filter(doc)
    filtered_text = violations.apply_to_doc(doc)
    return filtered_text
