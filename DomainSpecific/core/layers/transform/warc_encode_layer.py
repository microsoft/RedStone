#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# coding=utf-8
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import re
import codecs
import logging
import traceback
import requests
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
from warcio.limitreader import LimitReader
from warcio.warcwriter import WARCWriter
from warcio.archiveiterator import ArchiveIterator
import lxml.etree as ET
import lxml.html as HT
from py_asciimath.translator.translator import MathML2Tex
from pylatexenc.latexwalker import LatexWalker
from charset_normalizer import detect
import util

def tex_in_script_tag(text):
    return text.startswith('<script type="math/tex"') or \
           text.startswith("<script type='math/tex'") or \
           text.startswith('<script type="math/latex"') or \
           text.startswith("<script type='math/latex'") or \
           text.startswith('<script type="math/asciimath"') or \
           text.startswith("<script type='math/asciimath'") or \
           text.startswith('<span class="math-formula">') or \
           text.startswith("<span class='math-formula'>")

def tex_in_math_tag(text):
    return text.startswith("<annotation encoding='application/x-tex'>") or \
           text.startswith('<annotation encoding="application/x-tex">')

def tex_in_math_tag2(text):
    return text.startswith("<math") and "</annotation>" in text

def mathml_in_script_tag(text):
    return text.startswith('<script type="math/mml"') or \
           text.startswith("<script type='math/mml'")

def mathml_in_math_tag(text):
    return text.startswith("<math ") and 'xmlns="http://www.w3.org/1998/Math/MathML"' in text
    #return text.startswith('<math xmlns="http://www.w3.org/1998/Math/MathML"') or \
    #       text.startswith("<math xmlns='http://www.w3.org/1998/Math/MathML'")
    #return text.startswith("<math ")

def is_tex(text):
    return re.match(r"(\$\$.*?\$\$)", text) is not None

def contain_tex(text):
    return re.search(r"(\$\$.*?\$\$)", text) is not None

def check_latex(latex):
    try:
        w = LatexWalker(latex, tolerant_parsing=False)
        (nodelist, pos, len_) = w.get_latex_nodes(pos=0)
        return True
    except:
        return False

def remove_hidden_content(html):
    text = html
    root = HT.document_fromstring(text)

    hidden_nodes = root.xpath('//*[@aria-hidden="true"]')
    for hidden_node in hidden_nodes:
        hidden_node.drop_tree()

    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    if html.strip().startswith(b'<!DOCTYPE'):
        index = html.find(b"<html")
        if index != -1:
            doctype = html[:index].strip()
    new_text = HT.tostring(root, method="html", doctype=doctype)
    new_html = new_text
    return new_html

def remove_attr(text, attr):
    index = text.find(attr)
    if index == -1:
        return text, False
    before = text[:index-1]
    text = text[index:]
    index = len(attr) + 1
    index = text.find(text[index:index+1], index+1) + 1
    after = text[index:]
    text = text[:index]
    text = before + after
    return text, True

def mathml_to_latex1(text):
    mml_dom = ET.fromstring(text)
    xslt = ET.parse("./dependency/xsltml_2.0/mmltex.xsl")
    transform = ET.XSLT(xslt)
    mmldom = transform(mml_dom)
    text = str(mmldom)
    return text

def mathml_to_latex2(text):
    symbol_mappings = {
        "&alpha;": "α",
        "&Alpha;": "A",
        "&beta;": "β",
        "&Beta;": "B",
        "&epsilon;": "ε",
        "&Epsilon;": "Ε",
        "&Mu;": "M",
        "&Nu;": "N",
        "&omicron;": "o",
        "&Omicron;": "O",
        "&iot;": "ι",
        "&conjugate0;": "&#x2015;",
    }
    for key1, key2 in symbol_mappings.items():
        text = text.replace(key1, key2)

    # add xml head.
    head = "<?xml version='1.0' encoding='UTF-8'?>\n" + \
           '<!DOCTYPE math PUBLIC "-//W3C//DTD MathML 2.0//EN" "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd">'
    text = head + text

    # remove unrecognized attributes.
    attrs = ("fontstyle", "ignorefont", "mathcolor", "rtableid", "altimg-valign", "dspmath", "xmlns:md", "specific-use")
    for attr in attrs:
        find = True
        while find:
            text, find = remove_attr(text, attr)
    text = text.replace(' xmlns=""', '')

    logging.disable(logging.WARNING)
    mathml2tex = MathML2Tex()
    text = mathml2tex.translate(text, network=False, from_file=False,)
    #logging.enable(logging.WARNING)
    return text

def separate_content_and_tag(html, start_str, end_str, s=0):
    index = html.find(start_str, s)
    before = html[:index]
    html = html[index:]
    index = html.find(end_str) + len(end_str)
    content = html[:index]
    after = html[index:]
    return content, before, after

def detect_code(text):
    keywords = (
        'if', 'else', 'for', 'while', 'def', 'class', 'include', 'switch', 'case', 
        'default', 'const', 'static', 'try', 'catch', 'exception', 'continue', 'open', 
        'close', 'import', 'var', 'None', 'null', 'true', 'True', 'false', 'False', 'print', 'return',
        'sudo', 'apt-get', 'wget',
        '\+', '-', '\*', '/', '=',
        #'//', '#', '/*', '*/',
    )
    patterns = [
        rf'\b(?:{"|".join(keywords)})\b', # keywords
        r'[{};]', # code indicators (curly braces, semicolon)
        r'\w+\s*\(.*\)', # function calls or declarations
        r'\w+\s*=\s*\w+', # variable assignments
    ]

    for pattern in patterns:
        if re.search(pattern, text):
            return True

    return False

def encode_code(node, code_tag, not_code_tag):
    # situation 1. <pre><code>
    # situation 2. <pre><span>
    # situation 3. <pre><code><span>
    # situation 4. <table><tbody>
    # situation 5. <table><tbody><pre>...

    if node.tag == "code":
        parent_node = node.getparent()
        parent_tag = parent_node.tag

        if parent_tag == "tbody":
            code_node = parent_node
        elif parent_tag == "pre":
            code_node = parent_node
            # below could be commentted.
            while parent_node is not None:
                parent_node = parent_node.getparent()
                if parent_node is not None and parent_node.tag == "tbody":
                    code_node = parent_node
                    break
        else:
            #code_node = node
            code_node = None

        if code_node is not None:
            text = code_node.text_content()

            # delete the whole attributes.
            for key, value in code_node.attrib.items():
                code_node.attrib.pop(key)
            if detect_code(text):
                code_node.tag = code_tag# + "-" + lang
                return True
            else:
                #code_node.tag = not_code_tag# debug
                return False

    child_nodes = node.getchildren()
    contain = False
    for child_node in child_nodes:
        if encode_code(child_node, code_tag, not_code_tag):
            contain = True
    return contain

def filter_code(html, code_tag, not_code_tag):
    root = HT.document_fromstring(html)

    contain = encode_code(root, code_tag, not_code_tag)

    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    if html.strip().startswith(b'<!DOCTYPE'):
        index = html.find(b"<html")
        if index != -1:
            doctype = html[:index].strip()
    new_text = HT.tostring(root, method="html", doctype=doctype)
    new_html = new_text

    return new_html, contain

def encode_image(uri, node, image_tag):
    if node.tag == "img":
        node.tag = image_tag

        link = node.attrib.get("src")
        if link is not None:
            link = util.relative2absolute_path(uri, link)
        alt = node.attrib.get("alt")
        width = node.attrib.get("width")
        height = node.attrib.get("height")
        name = util.md5(link) + Path(urlparse(link).path).suffix if link is not None else None
        attrs = {"link": link, "alt": alt, "width": width, "height": height, "name": name}
        node.text = str(attrs)

        # delete the whole attributes.
        for key, value in node.attrib.items():
            node.attrib.pop(key)
        return True

    child_nodes = node.getchildren()
    contain = False
    for child_node in child_nodes:
        if encode_image(uri, child_node, image_tag):
            contain = True
    return contain

def filter_image(uri, html, image_tag):
    root = HT.document_fromstring(html)

    contain = encode_image(uri, root, image_tag)

    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    if html.strip().startswith(b'<!DOCTYPE'):
        index = html.find(b"<html")
        if index != -1:
            doctype = html[:index].strip()
    new_text = HT.tostring(root, method="html", doctype=doctype)
    new_html = new_text

    return new_html, contain

def encode_video(uri, node, video_tag):
    if node.tag == "video":
        node.tag = video_tag

        link = node.attrib.get("src")
        if link is not None:
            link = util.relative2absolute_path(uri, link)
        alt = node.attrib.get("alt")
        width = node.attrib.get("width")
        height = node.attrib.get("height")
        name = util.md5(link) + Path(urlparse(link).path).suffix if link is not None else None
        attrs = {"link": link, "alt": alt, "width": width, "height": height, "name": name}
        node.text = str(attrs)

        # delete the whole attributes.
        for key, value in node.attrib.items():
            node.attrib.pop(key)
        return True

    child_nodes = node.getchildren()
    contain = False
    for child_node in child_nodes:
        if encode_video(uri, child_node, video_tag):
            contain = True
    return contain

def filter_video(uri, html, video_tag):
    root = HT.document_fromstring(html)

    contain = encode_video(uri, root, video_tag)

    doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    if html.strip().startswith(b'<!DOCTYPE'):
        index = html.find(b"<html")
        if index != -1:
            doctype = html[:index].strip()
    new_text = HT.tostring(root, method="html", doctype=doctype)
    new_html = new_text

    return new_html, contain

def encode_math_html(uri, html, encoding):
    encode_table = {
        b"<": b"[[[less]]]",
        b">": b"[[[large]]]",
    }

    tag_head_mathml  = b"[[[math-ml]]]"
    tag_tail_mathml  = b"[[[/math-ml]]]"
    tag_head_mathtex = b"[[[math-tex]]]"
    tag_tail_mathtex = b"[[[/math-tex]]]"
    
    start_end_strs = (
        (b"<maths", b"</maths>"),#1
        (b"<math>", b"</math>"),#2
        (b"<math ", b"</math>"),#2
        (b"<annotation encoding='application/x-tex'>", b"</annotation>"),
        (b'<annotation encoding="application/x-tex">', b'</annotation>'),
        (b"<span class='math-formula'>", b"</span>"),
        (b'<span class="math-formula">', b'</span>'),
        (b'<script type="math/mml"', b'</script>'),
        (b"<script type='math/mml'", b"</script>"),
        (b'<script type="math/tex"', b'</script>'),
        (b"<script type='math/tex'", b"</script>"),
        (b'<script type="math/latex"', b'</script>'),
        (b"<script type='math/latex'", b"</script>"),
        (b'<script type="math/asciimath"', b'</script>'),
        (b"<script type='math/asciimath'", b"</script>"),
    )

    sub_start_end_strs = (
        (b"<math", b"</math>"),#1
        (b"<annotation encoding='application/x-tex'>", b"</annotation>"),#2
        (b'<annotation encoding="application/x-tex">', b'</annotation>'),#2
    )

    assert tag_head_mathml not in html and tag_tail_mathml not in html
    assert tag_head_mathtex not in html and tag_tail_mathtex not in html

    contain_tag = False
    for (start_str, end_str) in start_end_strs:
        while start_str in html:
            content, before, after = separate_content_and_tag(html, start_str, end_str)

            if start_str[:5] == b"<math":
                for sub_start_str, sub_end_str in sub_start_end_strs:
                    if sub_start_str in content[len(start_str):-len(end_str)]:
                        content = content[len(start_str):-len(end_str)]
                        content, sub_before, sub_after = separate_content_and_tag(content, sub_start_str, sub_end_str)

            contain = True
            try:
                content_str = str(content, encoding)
            except:
                return html, False

            if contain and (tex_in_script_tag(content_str) or tex_in_math_tag(content_str)):
                try:
                    index1 = content.find(b">") + 1
                    index2 = content.rfind(b"<")
                    formula = content[index1:index2]
                    formula = formula.strip()
                    formula_str = str(formula, encoding)

                    if not check_latex(formula_str):
                        return html, False
                    for key1, key2 in encode_table.items():
                        formula = formula.replace(key1, key2)
                    content = b"<span>" + tag_head_mathtex + formula + tag_tail_mathtex + b"</span>"
                except:
                    contain = False
            elif contain and (tex_in_math_tag2(content_str)):
                try:
                    index2 = content_str.find("</annotation>")
                    index1 = content_str[:index2].rfind("</mrow>") + len("</mrow>")
                    formula = content_str[index1:index2]
                    formula = formula.strip()
                    formula_str = str(formula, encoding)

                    if not check_latex(formula_str):
                        return html, False
                    for key1, key2 in encode_table.items():
                        formula = formula.replace(key1, key2)
                    content = b"<span>" + tag_head_mathtex + formula + tag_tail_mathtex + b"</span>"
                except:
                    contain = False
            elif contain and (mathml_in_script_tag(content_str) or mathml_in_math_tag(content_str)):
                try:
                    # convert mathml to latex.
                    if "<semantics>" in content_str and "</semantics>" not in content_str:
                        content_str = content_str.replace("<semantics>", "")
                    try:
                        formula_str = mathml_to_latex1(content_str)
                    except:
                        formula_str = mathml_to_latex2(content_str)
                    formula = bytes(formula_str, encoding)
                    formula = formula.replace(codecs.BOM_UTF8, b"")
                    formula = formula.strip(b"$")
                    formula = formula.strip()
                    formula_str = str(formula, encoding)

                    if not check_latex(formula_str):
                        return html, False
                    for key1, key2 in encode_table.items():
                        formula = formula.replace(key1, key2)
                    content = b"<span>" + tag_head_mathml + formula + tag_tail_mathml + b"</span>"
                except:
                    contain = False
            else:
                contain = False

            if contain:
                html = before + content + after
                contain_tag = True
            else:
                html = before + after

    return html, contain_tag

def get_tag_info(tag):
    start_tag = f"<{tag}>".encode()
    end_tag = f"</{tag}>".encode()
    encode_start_tag = f"[[[{tag}]]]".encode()
    encode_end_tag = f"[[[/{tag}]]]".encode()
    tag = tag.encode()
    return tag, start_tag, end_tag, encode_start_tag, encode_end_tag

def encode_code_html(uri, html, encoding):
    code_tag_str = "code-encode"
    not_code_tag_str = "not-code-encode"
    code_tag, code_start_tag, code_end_tag, code_encode_start_tag, code_encode_end_tag = get_tag_info(code_tag_str)
    not_code_tag, not_code_start_tag, not_code_end_tag, not_code_encode_start_tag, not_code_encode_end_tag = get_tag_info(not_code_tag_str)
    assert code_start_tag not in html and code_end_tag not in html
    assert not_code_start_tag not in html and not_code_end_tag not in html

    try:
        html, contain = filter_code(html, code_tag_str, not_code_tag_str)

        if contain:
            html = html.replace(code_start_tag, b"<pre>" + b"\n" + code_encode_start_tag + b"\n")
            html = html.replace(code_end_tag, b"\n" + code_encode_end_tag + b"\n" + b"</pre>")

            #html = html.replace(not_code_start_tag, b"<pre>" + b"\n" + not_code_encode_start_tag + b"\n")# debug
            #html = html.replace(not_code_end_tag, b"\n" + not_code_encode_end_tag + b"\n" + b"</pre>")# debug
    except:
        contain = False

    return html, contain

def encode_image_html(uri, html, encoding):
    image_tag_str = "image-encode"
    image_tag, image_start_tag, image_end_tag, image_encode_start_tag, image_encode_end_tag = get_tag_info(image_tag_str)
    assert image_start_tag not in html and image_end_tag not in html

    try:
        html, contain = filter_image(uri, html, image_tag_str)

        if contain:
            #html = html.replace(image_start_tag, b"<pre>" + b"\n" + image_encode_start_tag + b"\n")
            #html = html.replace(image_end_tag, b"\n" + image_encode_end_tag + b"\n" + b"</pre>")
            html = html.replace(image_start_tag, b"<span>" + b"\n" + image_encode_start_tag + b"\n")
            html = html.replace(image_end_tag, b"\n" + image_encode_end_tag + b"\n" + b"</span>")
    except:
        contain = False

    return html, contain

def encode_video_html(uri, html, encoding):
    video_tag_str = "video-encode"
    video_tag, video_start_tag, video_end_tag, video_encode_start_tag, video_encode_end_tag = get_tag_info(video_tag_str)
    assert video_start_tag not in html and video_end_tag not in html

    try:
        html, contain = filter_video(uri, html, video_tag_str)

        if contain:
            #html = html.replace(video_start_tag, b"<pre>" + b"\n" + video_encode_start_tag + b"\n")
            #html = html.replace(video_end_tag, b"\n" + video_encode_end_tag + b"\n" + b"</pre>")
            html = html.replace(video_start_tag, b"<span>" + b"\n" + video_encode_start_tag + b"\n")
            html = html.replace(video_end_tag, b"\n" + video_encode_end_tag + b"\n" + b"</span>")
    except:
        contain = False

    return html, contain

def encode_html(uri, html, encoding, TAG):
    if html is None:
        return None, False

    if TAG == "math":
        html, contain_tag = encode_math_html(uri, html, encoding)
    elif TAG == "code":
        html, contain_tag = encode_code_html(uri, html, encoding)
    elif TAG == "image":
        html, contain_tag = encode_image_html(uri, html, encoding)
    elif TAG == "video":
        html, contain_tag = encode_video_html(uri, html, encoding)
    return html, contain_tag


def warc_encode_layer(warc_file_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", TAG=None, DEFAULT_ENCODING=None, OVERWRITE=False):
    ret = list()
    try:
        src_warc_file_path = os.path.join(INPUT_FOLDER, warc_file_name)
        src_warc_file_path = util.to_real_path(src_warc_file_path, variables)
        dst_warc_file_path = os.path.join(OUTPUT_FOLDER, warc_file_name)
        dst_warc_file_path = util.to_real_path(dst_warc_file_path, variables)

        if os.path.exists(src_warc_file_path) and (OVERWRITE or not os.path.exists(dst_warc_file_path)):
            util.create_folder_by_file_path(dst_warc_file_path)
            with open(dst_warc_file_path, "wb") as output:
                writer = WARCWriter(output, gzip=True)
                with open(src_warc_file_path, "rb") as input:
                    records = ArchiveIterator(input, arc2warc=True)
                    for id, record in enumerate(records):
                        if record.rec_type == "response" and record.http_headers.get_header("Content-Type", "").startswith("text/html"):
                            try:
                                uri = record.rec_headers["WARC-Target-URI"]

                                # read raw html.
                                html = record.content_stream().read()

                                # check html codec.
                                charset = record.http_headers["Content-Type"].split(";")[-1].split("=")
                                if charset[0].strip().lower() == "charset":
                                    encoding = charset[1]
                                else:
                                    index1 = html.find(b'<meta charset="')
                                    if index1 >= 0:
                                        index1 += len(b'<meta charset="')
                                        index2 = html.find(b'"', index1)
                                        encoding = str(html[index1:index2], encoding="ascii")
                                    else:
                                        try:
                                            logging.disable(logging.WARNING)
                                            encoding = detect(html)["encoding"]
                                            #logging.enable(logging.WARNING)
                                        except:
                                            encoding = ""
                                if encoding is not None:
                                    encoding = encoding.strip().strip('"').lower()

                                if encoding in ("",):
                                    encoding = DEFAULT_ENCODING
                                
                                # remove hidden tag.
                                if encoding is not None and b'aria-hidden="true"' in html:
                                #if encoding is not None and (b'aria-hidden="true"' in html or b'aria-readonly="true"' in html):
                                    try:
                                        html = remove_hidden_content(html)
                                    except:
                                        encoding = DEFAULT_ENCODING

                                # encode html.
                                if encoding is not None:
                                    if TAG is not None:
                                        html, contain_tag = encode_html(uri, html, encoding, TAG)
                                    else:
                                        contain_tag_cnt = 0
                                        TAGS = ("math", "code", "image")# "video"
                                        for tag in TAGS:
                                            html, contain_tag = encode_html(uri, html, encoding, tag)
                                            if contain_tag:
                                                contain_tag_cnt += 1
                                        contain_tag = contain_tag_cnt > 0
                                else:
                                    html = None
                                    contain_tag = False

                                # write encoded html.
                                if contain_tag and html is not None:
                                    content = BytesIO(html)
                                    assert content.getbuffer().nbytes == len(html)
                                    raw_length = len(html)
                                    record.raw_stream = LimitReader(content, raw_length)

                                    record.rec_headers["Content-Length"] = None
                                    record.length = None

                                    writer.write_record(record)
                            except:
                                traceback.print_exc()

            ret = [warc_file_name]
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret, )


if __name__ == "__main__":
    warc_file_name = "CC-MAIN-20221127073607-20221127103607-00007.warc.gz"
    INPUT_FOLDER = "$(input_data_folder)"
    OUTPUT_FOLDER = "$(output_data_folder)"
    TAG = "math"
    output = warc_encode_layer(warc_file_name, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER, TAG=TAG)
    print(output)
