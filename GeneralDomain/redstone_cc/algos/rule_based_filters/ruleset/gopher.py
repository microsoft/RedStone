from ..model.document import Document
from ..model.violations import Violations
from ..func.document import (
    document_alpha_words,
    document_end_with_ellipsis,
    document_gopher_stopwords,
    document_gopher_symbols,
    document_mean_word_length,
    document_start_with_bullet,
    document_word_count,
)
from ..func.repetition import (
    repetition_ngram_top_char_frac,
    repetition_ngram_dup_char_frac,
    repetition_line_dup_frac,
)

KEY_PREFIX_TOP_NGRAM = "rr_ngram_top_"
THRESHOLD_TOP_NGRAM = {2: 0.2, 3: 0.18, 4: 0.16}
KEY_PREFIX_DUP_NGRAM = "rr_ngram_dup_"
THRESHOLD_DUP_NGRAM = {5: 0.15, 6: 0.14, 7: 0.13, 8: 0.12, 9: 0.11, 10: 0.10}


def gopher_filter(doc: Document):
    violations = Violations()
    # repetition
    for n, thresh in THRESHOLD_TOP_NGRAM.items():
        val = repetition_ngram_top_char_frac(doc.normalized_words, n)
        if val > thresh:
            violations.doc(KEY_PREFIX_TOP_NGRAM + str(n))
    for n, thresh in THRESHOLD_DUP_NGRAM.items():
        val = repetition_ngram_dup_char_frac(doc.normalized_words, n)
        if val > thresh:
            violations.doc(KEY_PREFIX_DUP_NGRAM + str(n))
    sent_frac, sent_char_frac = repetition_line_dup_frac(doc.sents)
    if sent_frac > 0.3:
        violations.doc("rr_sent_frac")
    if sent_char_frac > 0.2:
        violations.doc("rr_sent_char_frac")
    para_frac, para_char_frac = repetition_line_dup_frac(doc.paragraphs)
    if para_frac > 0.3:
        violations.doc("rr_para_frac")
    if para_char_frac > 0.2:
        violations.doc("rr_para_char_frac")
    # document
    word_count = document_word_count(doc.normalized_words)
    if word_count < 50 or word_count > 100_000:
        violations.doc("doc_word_count")
    mean_word_len = document_mean_word_length(doc.normalized_words)
    if mean_word_len < 3 or mean_word_len > 10:
        violations.doc("doc_mean_word_len")
    symbol_to_word = document_gopher_symbols(doc.normalized_text) / len(
        doc.normalized_words
    )
    if symbol_to_word > 0.1:
        violations.doc("doc_gopher_symbol_to_word")
    alpha_word_rate = document_alpha_words(doc.normalized_words) / len(
        doc.normalized_words
    )
    if alpha_word_rate < 0.8:
        violations.doc("doc_alpha_word_rate")
    el_end_line_rate = document_end_with_ellipsis(doc.normalized_sents) / len(
        doc.normalized_sents
    )
    if el_end_line_rate > 0.3:
        violations.doc("doc_el_end_line_rate")
    bullet_start_line_rate = document_start_with_bullet(doc.normalized_sents) / len(
        doc.normalized_sents
    )
    if bullet_start_line_rate > 0.9:
        violations.doc("doc_bullet_start_line_rate")
    stopword_cnt = document_gopher_stopwords(doc.normalized_words)
    if stopword_cnt < 2:
        violations.doc("doc_gopher_stopword_count")

    return violations


def apply_gopher_rules(text, lang):
    doc = Document(text, lang)
    violations = gopher_filter(doc)
    filtered_text = violations.apply_to_doc(doc)
    return filtered_text
