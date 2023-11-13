# topnews
 Universal scraping platform for news and comments

 ## Usage
 Create a ini-file in directory "targets" with parameters according to the template (see below) and just run "topnews". You can add/modify projects without writing any code inside using text-templates (the rules are based on the XPATH).

 ## Examples
 This is a example template for any scrapping project:

 ```ini
 [COMMON]

 name = habr
 description = top of week
 enabled = 1
 demo = 1
 proxy = -1

 [RULES]

 scan_page_depth_max = 50
 scan_article_score_min = 0
 scan_comment_score_min = 0

 block_pages_page = https://habr.com/ru/top/weekly/page%page_num%/
 block_page_record = s.xpath('.//article[@class="post post_preview"]')

 block_record_title = s.xpath('.//h2[@class="post__title"]/a[@class="post__title_link"]/text()')[0]
 block_record_link = s.xpath('.//h2[@class="post__title"]//a[@class="post__title_link"]')[0].get('href')
 block_record_score = int(s.xpath('.//span[@class="post-stats__result-counter voting-wjt__counter_positive "]//text()')[0])
 block_record_date = s.xpath('.//span[@class="post__time"]//text()')[0]
 block_record_author = s.xpath('.//span[@class="user-info__nickname user-info__nickname_small"]//text()')[0]
 block_record_text = s.xpath('.//div[@class="post__body post__body_full"]')[0]
 block_record_comments = s.xpath('.//div[@id="comments"]//div[@class="comment"]')

 block_comment_title = None
 block_comment_text = s.xpath('.//div[@class="comment__message  "]//text()')[0]
 block_comment_link = s.xpath('.//li[@class="inline-list__item inline-list__item_comment-nav"]//a[@class="icon_comment-anchor"]')[0].get('href')
 block_comment_score = int(s.xpath('.//span[@class="voting-wjt__counter voting-wjt__counter_positive  js-score"]//text()')[0])
 block_comment_date = s.xpath('.//time[@class="comment__date-time comment__date-time_published"]//text()')[0]
 block_comment_author = s.xpath('.//span[@class="user-info__nickname user-info__nickname_small user-info__nickname_comment"]//text()')[0]
 ```
 Here you should set definitions for content blocks and parsing settings:
 - name: name of your project
 - description: description of your project
 - enabled: if 1 will be run, otherwise it will be skipped
 - demo: if 1 will be procced only one element of each target structure (good for debugging and testing rules)
 - proxy: proxy server usage (-1 - No Proxy, 0 - TOR Proxy, 1 - Random Proxy)
 - scan_page_depth_max, scan_article_score_min, scan_comment_score_min: limits for resource scraping (page depth, min. article score, min. comment score)
 - block_*: block definition in XPATH format in block hierarchy:
 ```
 block_pages > block_page_record > (block_record_title, ..., block_record_text) > block_record_comments > (block_comment_title, ..., block_comment_author)
 ```

 ## Remarks
 You can create such files for each of your projects and start scraping simultaneously for all projects. Results will be in "output".
