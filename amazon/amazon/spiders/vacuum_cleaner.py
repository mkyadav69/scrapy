# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
import requests
# from script_manager.proxy_manager import get_proxies
from ..items import AmazonItem
from itertools import cycle
from lxml.html import fromstring


def get_proxies():
    proxy_url = 'https://free-proxy-list.net/'
    response_proxy = requests.get(proxy_url)
    parser = fromstring(response_proxy.text)
    proxies_list = set()
    for x in parser.xpath('//tbody/tr')[:10]:
        if x.xpath('.//td[7][contains(text(),"yes")]'):
            proxy_href = ":".join([x.xpath('.//td[1]/text()')[0], x.xpath('.//td[2]/text()')[0]])
            proxies_list.add(proxy_href)
    return proxies_list


class VacuumCleanerSpider(scrapy.Spider):
    name = 'vacuum_cleaner'
    start_urls = ['http://amazon.com/']
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'X-Requested-With': 'XMLHttpRequest'
    }
    proxies = {
        'http': 'http://10.10.1.10:3128',
        'https': 'http://10.10.1.10:1080',
    }
    page_number = 1

    start_urls = [
        'https://www.amazon.com/s?rh=n%3A1055398%2Cn%3A%211063498%2Cn%3A3206324011%2Cn%3A14554126011%2Cn%3A3737721'
        '&page=1'
    ]

    def parse(self, response):
        start_time = time.time()
        proxies = get_proxies()
        proxy_pool = cycle(proxies)
        # end here
        if VacuumCleanerSpider.page_number == 1:
            pdp_url = response.css('a.s-access-detail-page::attr(href)').extract()
        else:
            pdp_url = response.css('h2.a-size-mini a.a-link-normal::attr(href)').extract()
        for pdp_urls in pdp_url:
            proxy = next(proxy_pool)
            if VacuumCleanerSpider.page_number == 1:
                new_url = pdp_urls
            else:
                new_url = 'https://www.amazon.com' + pdp_urls
            request = scrapy.Request(new_url, meta={"http": proxy, "https": proxy},
                                     callback=self.get_product_description,
                                     cb_kwargs=dict(page_url=response.url, start_time=start_time),
                                     errback=self.get_https_errors, dont_filter=True,
                                     headers=self.headers)
            yield request
        if VacuumCleanerSpider.page_number == 1:
            next_page = response.css('div#pagn span.pagnRA a.pagnNext::attr(href)').extract_first()
        else:
            next_page = response.css('ul.a-pagination li.a-last a::attr(href)').extract_first()
        if next_page != '':
            VacuumCleanerSpider.page_number += 1
            next_page_url = 'https://www.amazon.com/' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def get_https_errors(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        # check failure's type:
        if failure.check(HttpError):
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

        # def auth_user(self, response):
        #     return FormRequest.from_response(response, formdata={
        #         'user': 'user', 'pass': 'pass'
        #     })

    def get_product_description(self, response, page_url, start_time):
        self.logger.info('Got successful response from {}'.format(response.url))
        items = AmazonItem()
        pdp_title = response.css('span#productTitle::text').extract_first()
        pdp_price = response.css('span#priceblock_ourprice::text').extract_first()
        pdp_saving_price = response.css('span.priceBlockStrikePriceString::text').extract_first()
        pdp_bullet_description = response.css('div#feature-bullets span.a-list-item::text').extract()
        all_desc_details = response.css('div#prodDetails table.prodDetTable tr')
        pdp_time_taken = str(time.time() - start_time) + ' ' + 'second'
        pdp_description_matrix_list = []
        for desc_data in all_desc_details:
            decs_hdr_col1 = desc_data.css('th.prodDetSectionEntry::text').extract()
            decs_hdr_col12 = desc_data.css('td.a-size-base::text').extract()
            for (col1, col12) in zip(decs_hdr_col1, decs_hdr_col12):
                pdp_item = {col1.strip(): col12.strip()}
                pdp_description_matrix_list.append(pdp_item)
        filter_pdp_bul_dec = [s.strip() for s in pdp_bullet_description]
        items['page_url'] = page_url
        items['pdp_url'] = response.request.url
        items['pdp_title'] = pdp_title.strip()
        items['pdp_price'] = pdp_price
        items['pdp_saving_price'] = pdp_saving_price
        items['pdp_bullet_description'] = list(filter(None, filter_pdp_bul_dec))
        items['pdp_descriptions'] = pdp_description_matrix_list
        items['pdp_time_taken'] = pdp_time_taken

        yield items
