# -*- coding: utf-8 -*-
import scrapy
import time
import random
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
import requests
# from script_manager.proxy_manager import get_proxies
# from script_manager.proxy_manager import get_proxies
from ..items import PriceTrackingItem
from itertools import cycle
from lxml.html import fromstring


class PriceTestingSpider(scrapy.Spider):
    name = 'price_testing'
    start_urls = [
        'https://www.amazon.com/KINGERSONS-Friedrich-Conditioner-Cooling-Heating/dp/B07S1CVJ3B'
    ]

    def parse(self, response):
        items = PriceTrackingItem()
        sale_price = response.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()').extract()
        if sale_price == '':
            seller_info = response.css('div#availability span.a-size-medium a::attr(href)').extract_first()
            seller_info_url = 'https://www.amazon.com' + str(seller_info)
            request = scrapy.Request(seller_info_url,callback=self.get_seller_price, dont_filter=True)
            yield request
        #use this yield content and combine with main response
        # items['sale_price'] = ''.join(sale_price).strip()
        # items['seller_info'] = ''.join(seller_info).strip()

    def get_seller_price(self, response):
        get_all_seller_data = response.css('div.a-spacing-double-large')
        for sel_data in get_all_seller_data:
            header = sel_data.css('div.a-spacing-mini div.a-column span.a-color-secondary::text').extract()
            price = sel_data.css('div.olpOffer div.olpPriceColumn span.olpOfferPrice::text').extract_first()
            condition = sel_data.css('div.olpOffer div.olpConditionColumn span.olpCondition::text').extract_first()
            delivery_ship_form = sel_data.css('div.olpOffer div.olpDeliveryColumn ul.olpFastTrack '
                                              'span.a-list-item::text').extract_first()
            delivery_ship_rate_policy = sel_data.css('div.olpOffer div.olpDeliveryColumn ul.olpFastTrack '
                                                     'span.a-list-item a::attr(href)').extract_first()
            delivery_ship_rate_policy_url = 'https://www.amazon.com' + delivery_ship_rate_policy

            seller_info = sel_data.css('div.olpOffer div.olpSellerColumn h3.olpSellerName span.a-text-bold a::text').extract_first()
            seller_rating = sel_data.css('div.olpOffer div.olpSellerColumn p i.a-icon '
                                         'span.a-icon-alt::text').extract_first()
            seller_positive_rating = sel_data.css('div.olpOffer div.olpSellerColumn p a b::text').extract_first()


