# -*- coding: utf-8 -*-
import scrapy
import time
import random
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
import requests
# from script_manager.proxy_manager import get_proxies
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


def get_headers():
    user_agent_list = [
        # Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 '
        'Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
        'Safari/537.36',
        # Firefox
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; '
        '.NET CLR 3.5.30729) '
    ]
    user_agent = random.choice(user_agent_list)
    return {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': user_agent,
        'X-Requested-With': 'XMLHttpRequest'
    }


class WindowAcSpider(scrapy.Spider):
    name = 'window_ac'

    page_number = 1

    start_urls = [
        'https://www.amazon.com/s?rh=n%3A1055398%2Cn%3A%211063498%2Cn%3A3206324011%2Cn%3A14554126011%2Cn%3A3737721'
        '&page=1'
    ]

    def parse(self, response):
        start_time = time.time()
        proxies = get_proxies()
        headers = get_headers()
        proxy_pool = cycle(proxies)
        if WindowAcSpider.page_number == 1:
            pdp_url = response.css('a.s-access-detail-page::attr(href)').extract()
        else:
            pdp_url = response.css('h2.a-size-mini a.a-link-normal::attr(href)').extract()
        for pdp_urls in pdp_url:
            # proxy = next(proxy_pool)
            if WindowAcSpider.page_number == 1:
                new_url = pdp_urls
            else:
                new_url = 'https://www.amazon.com' + pdp_urls
            request = scrapy.Request(
                'https://www.amazon.com/Emerson-Quiet-Kool-EARC15RSE1-Conditioner/dp/B07PZQ5MDB',
                callback=self.get_product_description,
                cb_kwargs=dict(page_url=response.url, start_time=start_time),
                errback=self.get_https_errors, dont_filter=True)
            yield request
        if WindowAcSpider.page_number == 1:
            next_page = response.css('div#pagn span.pagnRA a.pagnNext::attr(href)').extract_first()
        else:
            next_page = response.css('ul.a-pagination li.a-last a::attr(href)').extract_first()
        WindowAcSpider.page_number += 1
        next_page = 'https://www.amazon.com/s?rh=n%3A1055398%2Cn%3A%211063498%2Cn%3A3206324011%2Cn%3A14554126011%2Cn%3A3737721&page='+ str(WindowAcSpider.page_number)
        if WindowAcSpider.page_number == 1:
            next_page_url = 'https://www.amazon.com' + next_page
            yield response.follow(next_page, callback=self.parse)

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
        pdp_information_matrix_list = []
        pdp_customer_rating_matrix_list = []
        print(response)
        pdp_title = response.css('span#productTitle::text').extract_first()
        pdp_price = response.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()').extract()
        # pdp_price = response.css(
        #     'div#price tr#priceblock_ourprice_row td.a-span12 span#priceblock_ourprice::text').extract_first()
        pdp_saving_price = response.css(
            'div#price tr td.a-size-base span.priceBlockStrikePriceString::text').extract_first()
        pdp_bullet_description = response.css('div#feature-bullets span.a-list-item::text').extract()
        pdp_bullet_dec = [s.strip() for s in pdp_bullet_description]
        pdp_time_taken = str(time.time() - start_time) + ' ' + 'second'
        pdp_description = response.css('div#productDescription p::text').extract_first()
        pdp_size = response.css('div.variation_size_name span.selection::text').extract_first()
        all_desc_details = response.css('div#prodDetails table.prodDetTable tr')
        for desc_data in all_desc_details:
            decs_hdr_col1 = desc_data.css('th.prodDetSectionEntry::text').extract()
            decs_hdr_col12 = desc_data.css('td.a-size-base::text').extract()
            for (col1, col12) in zip(decs_hdr_col1, decs_hdr_col12):
                pdp_item = {col1.strip(): col12.strip()}
                pdp_information_matrix_list.append(pdp_item)
        pdp_brand = response.css(
            'div#bylineInfo_feature_div div a#bylineInfo::text').extract_first()
        pdp_rating = response.css(
            'div#averageCustomerReviews span.a-declarative a#acrCustomerReviewLink span#acrCustomerReviewText::text').extract_first()
        cst_title = response.css('div#customerReviewsAttribute_feature_div div.a-section div.a-row '
                                 'span.a-size-base::text').extract()
        cst_rating_point = response.css('div#customerReviewsAttribute_feature_div div.a-section div.a-text-right '
                                        'i.a-icon-star-small span.a-icon-alt::text').extract()
        for (c_title, c_rtg_value) in zip(cst_title, cst_rating_point):
            c_item = {c_title.strip(): c_rtg_value.strip()}
            pdp_customer_rating_matrix_list.append(c_item)
        items['page_url'] = page_url
        items['pdp_url'] = response.request.url
        items['pdp_title'] = pdp_title.strip()
        items['pdp_price'] = pdp_price
        items['pdp_saving_price'] = pdp_saving_price
        items['pdp_size'] = pdp_size.strip() if pdp_size else pdp_size
        items['pdp_brand'] = pdp_brand.strip() if pdp_brand else pdp_brand
        items['pdp_rating'] = pdp_rating.strip() if pdp_rating else pdp_rating
        items['pdp_bullet_description'] = list(filter(None, pdp_bullet_dec))
        items['pdp_information'] = pdp_information_matrix_list
        items['pdp_descriptions'] = pdp_description.strip() if pdp_description else pdp_description
        items['pdp_customer_rating'] = pdp_customer_rating_matrix_list
        items['pdp_time_taken'] = pdp_time_taken

        yield items
