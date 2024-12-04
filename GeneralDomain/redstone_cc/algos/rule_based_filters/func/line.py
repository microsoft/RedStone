import regex

RE_UPPER = regex.compile(r"\p{Lu}")
RE_LETTER = regex.compile(r"\p{L}")


def line_uppercase_ratio(line):
    cnt_upper = len(RE_UPPER.findall(line))
    cnt_letter = len(RE_LETTER.findall(line))
    if cnt_letter == 0:
        return 0
    return cnt_upper / cnt_letter


RE_NUMERICAL = regex.compile(r"^(\p{N}|\p{Z}|\p{C})+$")


def line_all_numeric(line):
    return RE_NUMERICAL.fullmatch(line) is not None


RE_REFINEDWEB_COUNTER = regex.compile(r"^\d+\s+[a-zA-Z]+$")


def line_refinedweb_counter(line):
    return RE_REFINEDWEB_COUNTER.fullmatch(line.strip()) is not None


def line_regex_match(line, patterns):
    for pattern in patterns:
        if regex.search(pattern, line) is not None:
            return True
    return False


def test_line_uppercase_ratio():
    line = "ASDzxczxc a././.,./,/.123"
    res = line_uppercase_ratio(line)
    # ignore number, space and puncts
    assert res == 3 / 10
    line = ".,/./././"
    res = line_uppercase_ratio(line)
    assert res == 0


def test_line_all_numeric():
    line = "1231    34\t345345"
    assert line_all_numeric(line)
    line = "asd1231as"
    assert not line_all_numeric(line)


def test_line_refinedweb_counter():
    line = "3 emails"
    assert line_refinedweb_counter(line)
    line = "3 emails emails"
    assert not line_refinedweb_counter(line)


def test_line_regex_match():
    pattern = "^sign in"
    line = "sign in 123"
    assert line_regex_match(line, [pattern])
    line = "123 sign in 123"
    assert not line_regex_match(line, [pattern])

    pattern = "read more...$"
    line = "123 read more..."
    assert line_regex_match(line, [pattern])
    line = "read more...."
    assert not line_regex_match(line, [pattern])

    pattern = "target"
    line = "asdtargetasd"
    assert line_regex_match(line, [pattern])
