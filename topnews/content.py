from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from lxml.html.clean import Cleaner
from lxml import html, etree
from lxml.html import tostring
from operator import itemgetter, attrgetter
import traceback
import base64
import logging
from netstream import Netstream


log = logging.getLogger(__name__)
netstream = Netstream()


@dataclass
class Content:
    """Content: target data content"""
    def download(self, url, proxy):
        log.debug(f'downloading data content: {url}')
        received, total, content = netstream.download(proxy, [url])
        data = content.get(url)
        if data == '':
            log.error(f'download error: empty content data')
            return None
        # log.debug(f'!downloaded data content (all text): {data}')
        content = html.fromstring(data)
        log.debug(f'!downloaded data content (LXML fmt): {content}')
        return content


    def analize(self, content, pattern):
        result = None
        s = content
        try:
            result = eval(pattern)
            log.debug(f'{pattern} -> {str(result).strip()}')
        except:
            log.error(f'{pattern} -> ERROR:')
            log.debug(traceback.format_exc())
        return result


    def get_base64_encoded_image(self, url, proxy):
        content = self.download(url, proxy)
        log.info(content)
        data = base64.b64encode(content).decode('utf-8')
        new_item_src_base64 = f'data:image/jpeg;base64,{get_base64_encoded_image(new_item_src_abs)}'
        return new_item_src_base64


    def clean(self, content):
        cleaner = Cleaner(
            scripts=True, javascript=True, comments=True, style=True, links=True,
            meta=True, page_structure=False, processing_instructions=True,
            embedded=True, frames=True, forms=True, annoying_tags=True,
            remove_tags=[], allow_tags=[], remove_unknown_tags=True,
            safe_attrs_only=True, add_nofollow=True, host_whitelist=[],
            whitelist_tags = [])
        text = None
        try:
            text = cleaner.clean_html(tostring(content)).decode('utf-8')
            text = text.replace(r'<img', r'<img style="width:100%;"')
        except:
            ...
            # log.error('html clean error')
        return text


    def format(self, records, article_score_min, comment_score_min):
        result = ''
        articles = sorted([record for id, record in records.items() if record.kind=='Article'], key=attrgetter('score'), reverse=True)
        article_score_min = int(float(article_score_min / 100.0) * max(item.score for item in articles))
        articles = filter(lambda x: x.score > article_score_min, articles)
        article_counter = 0
        for article in articles:
            article_counter += 1
            result += f'<hr>' + \
                      f'<p>{article.score}<br><b><a href="{article.link}">{article.title}</a>' + \
                      f'<a href="javascript:toggle(\'toggleText{article_counter}\', \'displayText{article_counter}\');" id="displayText{article_counter}">&nbsp;↓&nbsp;</a></b>' + \
                      f'</p><hr><p><div id="toggleText{article_counter}" style="display: none;">{article.text}</p><hr>'
            comments = sorted([record for id, record in records.items() if record.kind=='Comment' and record.parentID==article.ID], key=attrgetter('score'), reverse=True)
            comments_table = ''
            if comments is not None and comments != []:
                comment_score_min = int(float(comment_score_min / 100.0) * max(item.score for item in comments))
                comments = filter(lambda x: x.score >= comment_score_min, comments)
                comments_table = self.html_table('Комментарии', [{'Оценка' : ''}, {'Дата' : ''}, {'Комментарий': ''}], [[{comment.score: ''}, {comment.date: comment.link}, {comment.text: ''}] for comment in comments])
            result += f'{comments_table}</div>'
        return result


    def html_table(self, caption, header, tbody):
        log.debug(f'{caption=}, {header=}, {tbody=}')
        content = ''
        columns = len(header)
        for th in header:
            for k, v in th.items():
                if v != '':
                    content += f'<th><a target="_blank" href="{v}">{k}</a></th>\n'
                else:
                    content += f'<th>{k}</th>\n'
        for tr in tbody:
            row = ''
            for td in tr:
                for k, v in td.items():
                    if v != '':
                        row += f'<td><a target="_blank" href="{v}">{k}</a></td>\n'
                    else:
                        row += f'<td>{k}</td>\n'
            content += f'<tr>\n{row}</tr>\n'
        content = f'<table cellspacing="0" border="1" cellpadding="5">\n<caption><i>{caption}</i></caption>\n<tbody>\n{content}</tbody>\n</table>\n'
        return content


    def save(self, content, title, filename):
        timestamp = str(datetime.today().strftime('%d.%m.%Y %H:%M'))
        script = '<script>' + \
            'function toggle(toggleText, displayText)' + \
            '	{' + \
            '	var elmt = document.getElementById(toggleText);' + \
            '	var text = document.getElementById(displayText);' + \
            '	if(elmt.style.display == "block")' + \
            '	{' + \
            '		elmt.style.display = "none";' + \
            '		text.innerHTML = "&nbsp;&darr;&nbsp;";' + \
            '	}' + \
            '	else' + \
            '	{' + \
            '		elmt.style.display = "block";' + \
            '		text.innerHTML = "&nbsp;&uarr;&nbsp;";' + \
            '	}' + \
            '}' + \
            '</script>'
        title = f'{title}'
        filename = f'{filename}.html'
        header = f'<head><meta http-equiv="content-type" content="text/html; charset=utf-8" /></head>\n'
        style = '<style>a {text-decoration: none;} </style>' + '\n'
        body = f'<body style="font-family:Arial">{content}<hr>{title}: {timestamp}</body>'
        content = f'<!DOCTYPE html><html>{header}{style}{body}{script}</html>'
        with open(filename, 'w', encoding='utf8') as f:
            f.write(content)
        return filename
