import regex


def document_word_count(words):
    return len(words)


def document_mean_word_length(words):
    return sum(len(x) for x in words) / len(words)


RE_ALPHA = regex.compile(r"\p{L}")


def document_alpha_words(words):
    return sum(int(RE_ALPHA.search(word) is not None) for word in words)


BULLET_POINT_SYMBOLS = (
    "\u2022",  # bullet point
    "\u2023",  # triangular bullet point
    "\u25B6",  # black right pointing triangle
    "\u25C0",  # black left pointing triangle
    "\u25E6",  # white bullet point
    "\u25A0",  # black square
    "\u25A1",  # white square
    "\u25AA",  # black small square
    "\u25AB",  # white small square
    "\u2013",  # en dash
)


def document_start_with_bullet(lines):
    cnt = 0
    for line in lines:
        line = line.lstrip()
        for symbol in BULLET_POINT_SYMBOLS:
            if line.startswith(symbol):
                cnt += 1
                break
    return cnt


ELLIPSIS = "..."


def document_end_with_ellipsis(lines):
    return sum(int(x.strip().endswith(ELLIPSIS)) for x in lines)


GOPHER_SYMBOLS = ("#", "...")


def document_gopher_symbols(text):
    return sum(text.count(x) for x in GOPHER_SYMBOLS)


GOPHER_STOPWORDS = {"the", "be", "to", "of", "and", "that", "have", "with"}


def document_gopher_stopwords(words):
    return sum(int(word in GOPHER_STOPWORDS) for word in words)
