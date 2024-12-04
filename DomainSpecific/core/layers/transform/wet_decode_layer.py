#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import re
from io import BytesIO
from warcio.limitreader import LimitReader
from warcio.warcwriter import WARCWriter
from warcio.archiveiterator import ArchiveIterator
from pylatexenc.latex2text import LatexNodes2Text
from guesslang import Guess
import util

def decode_tag(tag):
    return tag.replace(b"[[[", b"<").replace(b"]]]", b">")

def latex2text(latex, encoding="utf-8"):
    latexNodes2Text = LatexNodes2Text()
    latex = str(latex, encoding)
    text = latexNodes2Text.latex_to_text(latex)
    text = bytes(text, encoding)
    return text

def separate_content_and_tag(html, start_str, end_str):
    index = html.find(start_str)
    before = html[:index]
    html = html[index:]
    index = html.find(end_str) + len(end_str)
    content = html[:index]
    after = html[index:]
    return content, before, after

def remove_number_and_merge_snippet(html, NumberThred = 7):
    lines = html.split(b'\n')

    for interval in (1, 2, 3, 4):
        line_no_list = list()
        last_code_no = -1
        for line_no in range(0, len(lines), interval):
            try:
                code_no = int(lines[line_no].strip())
            except:
                code_no = -1
            if (last_code_no == -1 and code_no == 1) or last_code_no + 1 == code_no:
                last_code_no = code_no
                line_no_list.append(line_no)
            else:
                if last_code_no > NumberThred:
                    for hist_line_no in line_no_list:
                        lines[hist_line_no] = b''
                line_no_list = list()
                last_code_no = -1
        lines = list(filter(lambda line: len(line) > 0, lines))

    for i in range(2):
        line_no_list = list()
        last_code_no = -1
        for line_no in range(len(lines)):
            try:
                code_no = int(lines[line_no].strip())
            except:
                code_no = -1
            if (last_code_no == -1 and code_no == 1) or last_code_no + 1 == code_no:
                last_code_no = code_no
                line_no_list.append(line_no)
            elif code_no == 0 or code_no == 1:
                if last_code_no > NumberThred:
                    for hist_line_no in line_no_list:
                        lines[hist_line_no] = b''
                line_no_list = [line_no]
                last_code_no = code_no
        lines = list(filter(lambda line: len(line) > 0, lines))
    
    for line_no in range(len(lines)):
        if len(lines[line_no].strip()) == 0:
            lines[line_no] = b''
    lines = list(filter(lambda line: len(line) > 0, lines))

    # merge code snippets which are locate continously with single line.
    #html = re.sub(b"</code-encode>\n<code-encode>\n", b"\n", html)
    code_head = b"<code-encode>"
    code_tail = b"</code-encode>"
    for line_no in range(max(0, len(lines)-3)):
        if code_tail in lines[line_no] and code_head in lines[line_no+1] and code_tail in lines[line_no+3]:
            lines[line_no] = b''
            lines[line_no+1] = b''
    lines = list(filter(lambda line: len(line) > 0, lines))

    # filter issue html.
    cnt = 0
    for line in lines:
        if code_head in line:
            cnt += 1
        elif code_tail in line:
            cnt -= 1
        # error happens.
        if cnt != 0 and cnt != 1:
            return b''
    
    html = b'\n'.join(lines)
    return html

guess = None
def identify_code(text):
    global guess
    if guess is None:
        guess = Guess()
    try:
        #name = guess.language_name(text)
        name, prob = guess.probabilities(text)[0]
    except:
        name, prob = "unknown", 1.0
    return name, prob

def decode_html(uri, html, encoding, TAG):
    if html is None:
        return None, False

    if TAG == "math":
        decode_table = {
            b"[[[less]]]": b"<",
            b"[[[large]]]": b">",
        }

        tag_head_mathml = b"[[[math-ml]]]"
        tag_tail_mathml = b"[[[/math-ml]]]"
        tag_head_mathtex = b"[[[math-tex]]]"
        tag_tail_mathtex = b"[[[/math-tex]]]"

        start_end = (
            (tag_head_mathml, tag_tail_mathml),
            (tag_head_mathtex, tag_tail_mathtex),
        )

        for (start, end) in start_end:
            while start in html:
                content, before, after = separate_content_and_tag(html, start, end)
                formula = content[len(start): -len(end)]

                if len(formula.strip()) != 0:
                    # decode < and >.
                    for key1, key2 in decode_table.items():
                        formula = formula.replace(key1, key2)
                    
                    # decode math tag.
                    content = decode_tag(start) + formula + decode_tag(end)

                    # dedup math formula around context.
                    formula_ascii = latex2text(formula).strip()
                    n = len(formula_ascii)
                    if n > 0 and before.rstrip()[-n:] == formula_ascii:
                        before = before.rstrip()[:-n]
                    elif n > 0 and after.lstrip()[:n] == formula_ascii:
                        after = after.lstrip()[n:]
                    html = before + content + after
                else:
                    # remove empty formula.
                    html = before + after

    elif TAG == "code":
        tag_head_code = b"[[[code-encode]]]"
        tag_tail_code = b"[[[/code-encode]]]"
        #tag_head_notcode = b"[[[not-code-encode]]]"# debug
        #tag_tail_notcode = b"[[[/not-code-encode]]]"# debug

        start_end = (
            (tag_head_code, tag_tail_code),
            #(tag_head_notcode, tag_tail_notcode),# debug
        )

        for (start, end) in start_end:
            while start in html:
                content, before, after = separate_content_and_tag(html, start, end)
                code = content[len(start): -len(end)].strip()

                if len(code) != 0:
                    lang, prob = identify_code(code)
                    #lcnt = code.count(b"\n")
                    #meta_lang = bytes(f"<metadata lang={lang} prob={prob:.2f} lines={lcnt} />", encoding=encoding)
                    meta_lang = bytes(f"<metadata lang={lang} prob={prob:.2f} />", encoding=encoding)
                    decode_start = decode_tag(start)
                    decode_end = decode_tag(end)
                    #content = decode_start + b"\n" + code + b"\n" + decode_end
                    content = decode_start + meta_lang + b"\n" + code + b"\n" + decode_end
                    html = before + content + after
                else:
                    # remove empty code.
                    html = before + after

        # remove number of code block.
        html = remove_number_and_merge_snippet(html)

    elif TAG == "image":
        tag_head_image = b"[[[image-encode]]]"
        tag_tail_image = b"[[[/image-encode]]]"

        start_end = (
            (tag_head_image, tag_tail_image),
        )

        for (start, end) in start_end:
            while start in html:
                content, before, after = separate_content_and_tag(html, start, end)
                image_meta = content[len(start): -len(end)].strip()

                if len(image_meta) != 0:
                    decode_start = decode_tag(start)
                    decode_end = decode_tag(end)
                    content = decode_start + image_meta + decode_end
                    html = before + content + after
                else:
                    # remove empty image.
                    html = before + after
                    return None, False

    elif TAG == "video":
        tag_head_video = b"[[[video-encode]]]"
        tag_tail_video = b"[[[/video-encode]]]"

        start_end = (
            (tag_head_video, tag_tail_video),
        )

        for (start, end) in start_end:
            while start in html:
                content, before, after = separate_content_and_tag(html, start, end)
                video_meta = content[len(start): -len(end)].strip()

                if len(video_meta) != 0:
                    decode_start = decode_tag(start)
                    decode_end = decode_tag(end)
                    content = decode_start + video_meta + decode_end
                    html = before + content + after
                else:
                    # remove empty video.
                    html = before + after
                    return None, False

    # remove continous empty lines.
    if html is not None and len(html) > 0:
        html = re.sub(b"(\n\r)+", b"\n", html)
        html = re.sub(b"(\r\n)+", b"\n", html)
        html = re.sub(b"\n+", b"\n", html)

    contain = False
    for (start, end) in start_end:
        decode_start = decode_tag(start)
        if decode_start in html:
            contain = True

    return html, contain

def wet_decode_layer(wet_file_name, variables=dict(), INPUT_FOLDER="./", OUTPUT_FOLDER="./", TAG=None, OVERWRITE=False):
    ret = list()
    try:
        BLACK_URLS = ("blame.php", "diff.php")
        regex = re.compile('|'.join(BLACK_URLS))
        src_wet_file_path = os.path.join(INPUT_FOLDER, wet_file_name)
        src_wet_file_path = util.to_real_path(src_wet_file_path, variables)
        dst_wet_file_path = os.path.join(OUTPUT_FOLDER, wet_file_name)
        dst_wet_file_path = util.to_real_path(dst_wet_file_path, variables)

        if os.path.exists(src_wet_file_path) and (OVERWRITE or not os.path.exists(dst_wet_file_path)):
            util.create_folder_by_file_path(dst_wet_file_path)
            with open(dst_wet_file_path, "wb") as output:
                writer = WARCWriter(output, gzip=True)
                with open(src_wet_file_path, "rb") as input:
                    records = ArchiveIterator(input, arc2warc=False)
                    for id, record in enumerate(records):
                        #lang = record.rec_headers["WARC-Identified-Content-Language"]
                        #if lang != "en":
                        #    continue

                        if record.rec_type == "conversion":
                            try:
                                uri = record.rec_headers["WARC-Target-URI"]
                                if regex.search(uri):
                                    continue

                                # read raw html.
                                html = record.content_stream().read()
                                encoding = "utf-8"

                                # decode html.
                                if encoding is not None:
                                    if TAG is not None:
                                        html, contain_tag = decode_html(uri, html, encoding, TAG)
                                    else:
                                        contain_tag_cnt = 0
                                        TAGS = ("math", "code", "image")# "video"
                                        for tag in TAGS:
                                            html, contain_tag = decode_html(uri, html, encoding, tag)
                                            if contain_tag:
                                                contain_tag_cnt += 1
                                        contain_tag = contain_tag_cnt > 0
                                else:
                                    html = None
                                    contain_tag = False

                                # write decoded html.
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
            #ret = [wet_file_name]
            ret = [dst_wet_file_path]
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
    output = wet_decode_layer(warc_file_name, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER, TAG=TAG)
    print(output)
