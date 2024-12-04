#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import re
import fasttext
import traceback
from unittest.mock import patch
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter, chomp
from newspaper import Article
import global_var

def filter_tags_in_html(soup):
    def del_tags(soup):
        del_tags = ['style', 'script', 'img']
        for tag in del_tags:
            tags = soup.find_all(tag)
            for tag in tags:
                tag.decompose()

        tags = soup.find_all('table')
        for tag in tags:
            if len(tag.text.strip()) == 0:
                for tag in tags:
                    tag.decompose()

    def modify_text(soup):
        modify_tags = ['a']
        for i in range(len(modify_tags)):
            for tag in soup.find_all(modify_tags[i]):
                tag_text = tag.text
                new_tag_text = tag_text.replace('\n', '')
                if len(new_tag_text) != len(tag_text):
                    tag.string = new_tag_text
    del_tags(soup)
    modify_text(soup)

    return soup

def lid(soup, model):
    LID_WIN_SIZE=256
    text = ''.join(soup.text.split())
    span_start, span_end = 0, len(text)
    if len(text) > LID_WIN_SIZE:
        mid = len(text) // 2
        mid_win = LID_WIN_SIZE // 2
        span_start = max(0, int(mid - mid_win))
        span_end = min(len(text), int(mid + mid_win))

    det_text = text[span_start: span_end]
    res = model.predict(det_text)
    la = res[0][0].replace("__label__", "")
    prob = float(res[1][0])
    return la, prob

def get_main_text_html(soup):
    article = Article("padding_url", fetch_images=False, keep_article_html=True)
    article.download(input_html=str(soup))
    article.parse()
    # assert len(article.text.strip()) >= 128
    main_html = article.article_html
    main_text = article.text
    return main_html, main_text

def remove_dup_newline(text):
    fields = text.split('\n')
    for i in range(len(fields)):
        fields[i] = fields[i].strip()
    return re.sub('\n{2,}', '\n\n', '\n'.join(fields)).strip()

class User_MarkdownConverter(MarkdownConverter):
    def convert_tr(self, el, text, convert_as_inline):
        cells = el.find_all(['td', 'th'])
        is_headrow = all([cell.name == 'th' for cell in cells])
        overline = ''
        underline = ''
        if is_headrow and not el.previous_sibling:
            # first row and is headline: print headline underline
            underline += '| ' + ' | '.join(['---'] * len(cells)) + ' |' + '\n'
        elif (not el.previous_sibling
            and (el.parent.name == 'table'
                or (el.parent.name == 'tbody'
                    and not el.parent.previous_sibling))):
            # first row, not headline, and:
            # - the parent is table or
            # - the parent is tbody at the beginning of a table.
            # print empty headline above this row
            overline += '| ' + ' | '.join([''] * len(cells)) + ' |' + '\n'
            overline += '| ' + ' | '.join(['---'] * len(cells)) + ' |' + '\n'
        if len(text.replace('|', ' ').strip()) == 0:
            return overline + underline
        else:
            return overline + '|' + text.replace('\n', ' ') + '\n' + underline

    def convert_a(self, el, text, convert_as_inline):
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        href = el.get('href')
        title = el.get('title')
        # For the replacement see #29: text nodes underscores are escaped
        if (self.options['autolinks']
                and text.replace(r'\_', '_') == href
                and not title
                and not self.options['default_title']):
            # Shortcut syntax
            return '<%s>' % href
        if self.options['default_title'] and not title:
            title = href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        # return '%s[%s](%s%s)%s' % (prefix, text, href, title_part, suffix) if href else text
        return '%s %s %s' % (prefix, text.replace('\n', ' '), suffix) if href else text

    def convert_pre(self, el, text, convert_as_inline):
        if not text:
            return ''
        code_language = self.options['code_language']

        if self.options['code_language_callback']:
            code_language = self.options['code_language_callback'](el) or code_language

        return '\n```%s\n%s\n```\n' % (code_language, text)

def html2text(soup, **options):
    def clean_markdown(md):
        fields = md.split('\n')
        for i in range(len(fields)):
            fields[i] = fields[i].strip()

        new_fields = []
        for i in range(len(fields)):
            field_set = list(set(fields[i]))
            if len(field_set) == 1 and field_set[0] in ['#', '*', '+', '-']:
                continue
            new_fields.append(fields[i])

        fields = new_fields
        md = '\n'.join(fields)

        return re.sub('\n{2,}', '\n\n', md).strip()

    return clean_markdown(User_MarkdownConverter(**options).convert_soup(soup))

def trans2md(html):
    soup = BeautifulSoup(html, 'html5lib')
    markdown_text = html2text(soup)
    # assert len(markdown_text) > 50 and len(markdown_text.split('\n')) != 1
    if markdown_text.startswith('.') and markdown_text.endswith('.'):
        markdown_text = markdown_text[1:-1]
    main_text = remove_dup_newline(soup.text)
    return markdown_text, main_text

@classmethod
def _patch_newspaper_parser_clean(cls, node):
    return node

@patch('newspaper.parsers.Parser.clean_article_html', new=_patch_newspaper_parser_clean)
def extract(soup):
    main_html, main_text = get_main_text_html(soup)
    markdown_text, _new_main_text = trans2md(main_html)
    return markdown_text, main_text

def extract_article_layer(id_html, variables=dict()):
    ret = None
    try:
        LA_TIER1 = ["en", "es", "ja", "fr", "de", "pt", "it", "zh"]
        LA_TIER2 = ["nl", "sv", "da", "fi", "ru", "no", "ko", "zh", "pl", "tr", "ar", "he", "pt", "cs", "hu", "th", "hi"]
        LA_TIER = LA_TIER1 + LA_TIER2
        article_id, html = id_html
        
        soup = BeautifulSoup(html, 'html5lib')
        soup = filter_tags_in_html(soup)
        la, la_prob = lid(soup, global_var.lid_model)
        if la in LA_TIER:
            main_md, main_text = extract(soup)
            if len(main_text) >= 128:
                ret = {"id": article_id, "text": main_text, "lang": la, "lang_prob": la_prob}
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == '__main__':
    id_html = (None, None)
    id_text_la = extract_article_layer(id_html)
    print(id_text_la)
