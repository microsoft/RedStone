import sys
from functools import cached_property

import stopit
from loguru import logger
from sentence_splitter import split_text_into_sentences

from ..utils import normalize


if sys.platform == "posix":
    stopit_method = stopit.SignalTimeout
else:
    stopit_method = stopit.ThreadingTimeout


class Document:
    def __init__(self, text, lang):
        self.text = text
        self.lang = lang

    @cached_property
    def sents(self):
        with stopit_method(60) as ctx:
            res = split_text_into_sentences(self.text, self.lang)
        if ctx:
            return res
        else:
            logger.warning("sentence splitter timeout")
            return self.text.split("\n")

    @cached_property
    def paragraphs(self):
        return self.text.split("\n")

    @cached_property
    def normalized_text(self):
        return normalize(self.text)

    @cached_property
    def normalized_sents(self):
        return [normalize(sent) for sent in self.sents]

    @cached_property
    def normalized_words(self):
        return self.normalized_text.split()
