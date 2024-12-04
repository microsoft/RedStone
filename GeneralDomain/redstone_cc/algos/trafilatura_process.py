import zlib
import re

import brotlicffi
import lxml.etree as ET
from lxml.html import tostring
from trafilatura import bare_extraction
from trafilatura.xml import xmltotxt
from trafilatura.meta import reset_caches as trafilatura_reset_caches

FLAG_TRAFILATURA_RESET_CACHE = False
ZIP_BOMB_SIZE_THRESHOLD = 100 * 1000 * 1000


class EmptyResultException(Exception):
    pass


def _remove_dup_newline(text):
    fields = text.split("\n")
    for i in range(len(fields)):
        fields[i] = fields[i].strip()

    text = "\n".join(fields)

    return re.sub("\n{2,}", "\n\n", text).strip()


def _normalize_whitespace(tree):
    def _normalize(text):
        text = text.replace("\n", "")
        text = re.sub(r"[\t ]+", " ", text)
        return text

    for item in tree.xpath(
        "//*[not(ancestor-or-self::pre) and not(ancestor-or-self::textarea)]"
    ):
        if item.text is not None:
            item.text = _normalize(item.text)
        for c in item:
            if c.tail is not None:
                c.tail = _normalize(c.tail)
    return tree


def _traf_xml_to_html(tree):
    # replace tag
    for elem in tree.iter(
        "hi", "list", "item", "head", "lb", "quote", "del", "row", "cell", "ab"
    ):
        if elem.tag == "hi":
            rend = elem.get("rend", "b")
            if rend == "#i":
                elem.tag = "i"
            elif rend == "#b":
                elem.tag = "b"
            elif rend == "#u":
                elem.tag = "u"
            elif rend == "#t":
                elem.tag = "code"
            elif rend == "#sub":
                elem.tag = "sub"
            elif rend == "#sup":
                elem.tag = "sup"
            if "rend" in elem.attrib:
                elem.attrib.pop("rend")
        elif elem.tag == "list":
            rend = elem.get("rend", "ul")
            elem.tag = rend
            if "rend" in elem.attrib:
                elem.attrib.pop("rend")
        elif elem.tag == "item":
            rend = elem.get("rend")
            if not rend:
                elem.tag = "li"
            else:
                tag, _idx = rend.split("-", 1)
                elem.tag = tag
            if "rend" in elem.attrib:
                elem.attrib.pop("rend")
        elif elem.tag == "head":
            rend = elem.get("rend", "h6")
            elem.tag = rend
            if "rend" in elem.attrib:
                elem.attrib.pop("rend")
        elif elem.tag == "lb":
            elem.tag = "br"
        elif elem.tag == "quote":
            elem.tag = "pre"
        elif elem.tag == "delete":
            elem.tag = "del"
        elif elem.tag == "row":
            elem.tag = "tr"
        elif elem.tag == "cell":
            if "role" in elem:
                if elem["role"] == "head":
                    elem.tag = "th"
                    elem.attrib.pop("role")
                    continue
            elem.tag = "td"
        elif elem.tag == "ab":
            if "type" in elem:
                if elem["type"] == "header":
                    elem.tag = "h6"
                    elem.attrib.pop("type")
                    continue
            elem.tag = "p"
    return tree


def _build_traf_doc_full(traf_bare_res):
    title = traf_bare_res.get("title", "")
    main = traf_bare_res["body"]
    comments = traf_bare_res.get("commentsbody")
    output = ET.Element("body")
    if title is not None and len(title) > 0:
        ele = ET.Element("h1")
        ele.text = title
        output.append(ele)
    main.tag = "p"
    output.append(main)
    if comments is not None:
        comments.tag = "p"
        output.append(comments)

    output = _traf_xml_to_html(output)
    return output


# no title no comments
def _build_traf_doc(traf_bare_res):
    output = ET.Element("body")

    main = traf_bare_res["body"]
    main.tag = "div"
    output.append(main)

    output = _traf_xml_to_html(output)
    return output


_RESET_CACHES_INTERVAL = 100
_reset_caches_counter = 0


def _reset_caches():
    global _reset_caches_counter, _RESET_CACHES_INTERVAL
    _reset_caches_counter += 1
    if _reset_caches_counter >= _RESET_CACHES_INTERVAL:
        trafilatura_reset_caches()
        _reset_caches_counter = 0


def _detect_zip_bomb(data):
    if isinstance(data, bytes):
        if data[:2] == b"\x1f\x8b":
            try:
                count = 0
                dec = zlib.decompressobj(32 + zlib.MAX_WBITS)
                for i in range(0, len(data), 64):
                    chunk = data[i : i + 64]
                    rv = dec.decompress(chunk)
                    count += len(rv)
                    if count > ZIP_BOMB_SIZE_THRESHOLD:
                        return True
            except (EOFError, OSError):
                pass
        # try brotli
        else:
            try:
                count = 0
                dec = brotlicffi.Decompressor()
                for i in range(0, len(data), 64):
                    chunk = data[i : i + 64]
                    rv = dec.decompress(chunk)
                    count += len(rv)
                    if count > ZIP_BOMB_SIZE_THRESHOLD:
                        return True
            except brotlicffi.error:
                pass  # logging.debug('invalid Brotli file')

    return False


# ref: https://gitlab.gnome.org/GNOME/libxml2/-/blame/master/include/libxml/parserInternals.h#L45
HTML_LENGTH_THRESHOLD = 10_000_000


def trafilatura_process(html):
    assert not _detect_zip_bomb(html), "zip bomb detected"
    assert len(html) < HTML_LENGTH_THRESHOLD, "Skip html that exceed length limit"

    # article extraction
    traf_res = bare_extraction(
        html,
        output_format="txt",
        include_comments=False,
        favor_precision=True,
        include_formatting=True,
        include_tables=True,
        include_images=False,
        include_links=False,
        deduplicate=False,
    )
    if traf_res is None:
        raise EmptyResultException("Trafilatura empty result")
    traf_html_tree = _build_traf_doc(traf_res)
    traf_html_tree = _normalize_whitespace(traf_html_tree)
    traf_html = tostring(traf_html_tree, encoding="unicode")
    traf_text = xmltotxt(traf_html_tree, False)
    traf_text = _remove_dup_newline(traf_text)

    if FLAG_TRAFILATURA_RESET_CACHE:
        _reset_caches()

    return {"text": traf_text, "html": traf_html}


__all__ = [
    "trafilatura_process",
]
