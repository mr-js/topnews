from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import uuid
import hashlib
import configparser
from tqdm import trange, tqdm
import logging

from content import Content

log = logging.getLogger(__name__)
content = Content()


@dataclass
class Target:
    """Target: target website template and data"""
    ID: str = ''
    name: str = ''
    description: str = ''
    enabled: bool = True
    proxy: int = 0
    rules: dict = field(default_factory=dict)
    records: dict = field(default_factory=dict)


    @dataclass
    class Record:
        """Record: target website data format (article or comment)"""
        ID: str = ''
        parentID: str = ''
        title: str = ''
        text: str = ''
        link: str = ''
        score: int = 0
        date: datetime = None
        author: str = ''
        kind: str = ''
        CRC: str = ''
        def __post_init__(self):
            self.ID = str(uuid.uuid4())
            if self.title != None:
                self.CRC = hashlib.sha256(f'{self.title}{self.text}'.encode('utf-8')).hexdigest()
            if self.score == None:
                self.score = 0


    def __init__(self, file):
        config = configparser.ConfigParser()
        config.read(f'{file}')
        self.rules = config._sections['RULES']
        self.name = config['COMMON']['name']
        self.description = config['COMMON']['description']
        self.enabled = config['COMMON'].getboolean('enabled')
        self.demo = config['COMMON'].getboolean('demo')
        self.proxy = int(config['COMMON']['proxy'])
        self.records = dict()
        self.page_depth_max = int(self.rules["scan_page_depth_max"])
        self.article_score_min = float(self.rules["scan_article_score_min"])
        self.comment_score_min = float(self.rules["scan_comment_score_min"])


    def __post_init__(self):
        self.ID = str(uuid.uuid4())


    def scan(self):
        if not self.enabled:
            log.warning(f'target "{self.name}: {self.description}" disabled')
            return False
        else:
            log.info(f'process target "{self.name}: {self.description}"')
            print(f'process target "{self.name}: {self.description}"')
        article_counter = 0
        pbar = tqdm(total=self.page_depth_max+1)
        for page_index in range(1, self.page_depth_max+1):
            page_url = f'{self.rules["block_pages_page"]}'.replace(r'%page_num%', str(page_index))
            log.info(f'process page {page_index}: {page_url}')
            pbar.update(1)
            page_content = content.download(page_url, self.proxy)
            if page_content is not None:
                log.info(f'page content identified')
            else:
                log.error(f'page content not identified')
                return False
            records_content = content.analize(page_content, self.rules["block_page_record"])
            if records_content is not None:
                log.info(f'records content identified')
            else:
                log.error(f'records content not identified')
                return False
            log.info(f'total records: {len(records_content)}')
            for record_content in records_content:
                article_counter += 1
                article = self.Record(parentID = None,
                            title = content.analize(record_content, self.rules["block_record_title"]),
                            link = content.analize(record_content, self.rules["block_record_link"]),
                            score = content.analize(record_content, self.rules["block_record_score"]),
                            date = content.analize(record_content, self.rules["block_record_date"]),
                            author = content.analize(record_content, self.rules["block_record_author"]),
                            text = None,
                            kind = 'Article',
                            )
                article_url = content.analize(record_content, self.rules["block_record_link"])
                if article_url is not None:
                    log.info(f'article url identified')
                else:
                    log.error(f'article url not identified')
                    return False
                log.info(f'process article: {article_url}')
                article_content = content.download(article_url, self.proxy)
                if article_content is not None:
                    log.info(f'article content downloaded')
                else:
                    log.error(f'article content not downloaded')
                    return False
                article.text = content.clean(content.analize(article_content, self.rules["block_record_text"]))
                log.debug(f'{article}')
                if article.text is not None:
                    log.info(f'article text identified')
                else:
                    log.error(f'article text not identified')
                    return False
                self.records[article.ID] = article
                comments_content = content.analize(article_content, self.rules["block_record_comments"])
                if comments_content is not None:
                    log.info(f'comments content identified')
                else:
                    log.error(f'comments content not identified')
                    return False
                if comments_content != []:
                    log.info(f'total comments: {len(comments_content)}')
                    for comment_content in comments_content:
                        comment = self.Record(parentID = article.ID,
                                title = None,
                                text = content.analize(comment_content, self.rules["block_comment_text"]),
                                link = content.analize(comment_content, self.rules["block_comment_link"]),
                                score = content.analize(comment_content, self.rules["block_comment_score"]),
                                date = content.analize(comment_content, self.rules["block_comment_date"]),
                                author = content.analize(comment_content, self.rules["block_comment_author"]),
                                kind = 'Comment',
                                )
                        log.debug(f'{comment}')
                        self.records[comment.ID] = comment
                else:
                    log.warning(f'comments content is null')
                if self.demo == True: log.warning('DEMO mode (interrupted)'); return True ## <-- DEMO MODE
        return True


    def format(self):
        return content.format(self.records, self.article_score_min, self.comment_score_min)


    def save(self, target_output_content, target_output_file):
        return content.save(target_output_content, self.name, target_output_file)
