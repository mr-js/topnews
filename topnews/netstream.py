import sys
import traceback
import requests
import asyncio
import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from fake_useragent import UserAgent
from timeit import default_timer
import logging
import datetime
from dataclasses import dataclass
from dataclasses import field
from lxml import html
from random import choice
import codecs
import logging


log = logging.getLogger(__name__)
log.level =logging.ERROR
## target processing timer
START_TIME = default_timer()


def main():
    ## mode: -1 - No Proxy, 0 - TOR Proxy, 1 - Random Proxy
    mode = 1
    ## targets: [urls]
    urls = [f'https://habr.com/ru/top/page{page_num}/' for page_num in range(1,1+2)]
    netstream = Netstream()
    ## result: (data received, data total, data content)
    result = netstream.download(mode=mode, targets=urls)
    log.debug(f'!RESULT: {result}')


@dataclass
class Netstream():
    mode: int = 1
    attemps: int = 10
    timeout: int = 5
    proxies: dict = field(default_factory=dict)
    data_total: int = 0
    data_received: int = 0
    data_content: dict = field(default_factory=dict)


    def finish(self):
        time_total = "{:5.2f}s".format(default_timer() - START_TIME)
        log.debug(f'finished at {time_total}')


    async def get_page(self, client, target):
        async with client.get(target) as response:
            if response.status != 200:
                log.debug(f'no response from url: {target}')
                return ''
            return await response.read()


    async def get_data(self, target):
        attemp = 0
        loop = asyncio.get_running_loop()
        while (attemp <= self.attemps):
            attemp += 1
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                connector = None
                if self.mode == -1:
                    proxy = 'No Proxy'
                if self.mode == 0:
                    proxy = 'socks5://127.0.0.1:9150'
                    connector = ProxyConnector.from_url(proxy)
                if self.mode == 1:
                    proxy = choice(self.proxies)
                    connector = ProxyConnector.from_url(proxy)
                headers = {'User-Agent': UserAgent().chrome}
                async with aiohttp.ClientSession(loop=loop, headers=headers, connector=connector, timeout=timeout) as client:
                    log.debug(f'receiving page content: {target} ({attemp}/{self.attemps} {proxy})')
                    self.data_content[target] = ''
                    data = await self.get_page(client, target)
                    self.data_content[target] = data.decode('utf-8')
                    log.debug(f'!received page content: {target} ({attemp}/{self.attemps} {proxy})')
                    self.data_received += 1
                    log.debug(f'total progress: {self.data_received}/{self.data_total}')
                    return
            except:
##                log.debug(traceback.format_exc())
                pass


    async def start(self, targets):
        log.debug(f'started')
        await asyncio.gather(*(self.get_data(target) for target in targets))


    def get_proxies(self):
        log.debug(f'receiving proxies...')
        try:
            res = requests.get('https://www.socks-proxy.net/')
            data = html.fromstring(res.content).xpath('//tbody//tr')
            self.proxies = [f"{item.xpath('.//td[5]//text()')[0]}://{item.xpath('.//td[1]//text()')[0]}:{item.xpath('.//td[2]//text()')[0]}".lower() for item in data]
##            log.debug(f'proxies: {self.proxies}')
            log.debug(f'!received proxies: {len(self.proxies)}')
        except:
##            log.debug(traceback.format_exc())
            pass


    def download(self, mode, targets):
        self.mode = mode
        self.data_total = len(targets)
        if self.mode == 1:
            self.get_proxies()
        asyncio.run(self.start(targets))
        self.finish()
        return self.data_received, self.data_total, self.data_content


if __name__ == "__main__":
    main()
