# -*- coding: utf-8 -*-
import json
import os
import re

import js2xml
import scrapy
import wget
import requests
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils import url
from twisted.internet.error import DNSLookupError, TCPTimedOutError

# from script_manager.proxy_manager import get_proxies
# from script_manager.proxy_manager import get_proxies
from ..items import PriceTrackingItem


class PriceTestingSpider(scrapy.Spider):
    name = 'price_testing'
    start_urls = [
        # 'https://www.amazon.in/LG-Inverter-Window-JW-Q18WUXA1-Discharge/dp/B082TG8SP1/ref=sr_1_5?dchild=1&qid=1591018885&refinements=p_n_feature_thirteen_browse-bin%3A2753047031&s=kitchen&sr=1-5'
        # 'https://www.amazon.in/Voltas-Window-123-Lyi-LZF/dp/B00LWRFC1W/ref=sr_1_6?dchild=1&qid=1591018885&refinements=p_n_feature_thirteen_browse-bin%3A2753047031&s=kitchen&sr=1-6'
        # 'https://www.amazon.in/Toshiba-Inverter-Copper-RAS-13BKCV-RAS-13BACV/dp/B07NX1T2WQ/ref=sr_1_10_sspa?dchild=1&keywords=window+ac&qid=1591007096&sr=8-10-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUFRREdYUzNQVEJMMTEmZW5jcnlwdGVkSWQ9QTA5NjE3NzlHVlZYTVhPN0lVSTgmZW5jcnlwdGVkQWRJZD1BMDc2NDg3NTJQWVQ2UzQyUzVRTEMmd2lkZ2V0TmFtZT1zcF9tdGYmYWN0aW9uPWNsaWNrUmVkaXJlY3QmZG9Ob3RMb2dDbGljaz10cnVl'
        # 'https://www.amazon.in/Croma-Window-Copper-CRAC1152-Installation/dp/B0827XB1WQ/ref=sr_1_1?dchild=1&keywords=window+ac&qid=1591004855&sr=8-1'
        # 'https://www.amazon.in/TCL-Ultra-Inverter-TAC-18CSD-V3S-Connectivity/dp/B083STCRZW/ref=sr_1_9_sspa?dchild=1&keywords=window+ac&qid=1591003260&sr=8-9-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyTzk3N1k2ODlVTTZCJmVuY3J5cHRlZElkPUEwOTAyMzk1MjhZTEszNDZGT1cyVSZlbmNyeXB0ZWRBZElkPUEwMDYzOTMxM0dSTkFaSzFUN05TVSZ3aWRnZXROYW1lPXNwX210ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU='
        # 'https://www.amazon.in/Hitachi-Star-Window-RAW318KUD-White/dp/B00LHO9YTQ/ref=sr_1_9?dchild=1&keywords=window+ac&qid=1590999102&sr=8-9'
        # 'https://www.amazon.in/Sanyo-Inverter-Copper-SI-SO-10T3SCIA/dp/B07NFKG9BP/ref=sr_1_1_sspa?dchild=1&keywords=window+ac&qid=1590992422&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzSkhJVEdINDAyV0ZDJmVuY3J5cHRlZElkPUEwOTExNDQyM0w2QTNZVTJZR1dMSSZlbmNyeXB0ZWRBZElkPUEwNjM5NjE3MloyWEk2MlozSUhMVSZ3aWRnZXROYW1lPXNwX2F0ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU='
        # 'https://www.amazon.com/FRIGIDAIRE-Window-Mounted-Conditioner-Full-Function-Control/dp/B07RFNGZVY'
        # 'https://www.amazon.com/Emerson-Quiet-Kool-EARC5MD1-Conditioner/dp/B071RG6HQ4/ref=sr_1_7?dchild=1&keywords=window+ac&qid=1591065897&sr=8-7'
        'https://www.amazon.com/Emerson-Quiet-Kool-EARC5MD1-Conditioner/dp/B071RG6HQ4/ref=sr_1_7?dchild=1&keywords=window+ac&qid=1591065897&sr=8-7'
    ]

    def parse(self, response):
        items = PriceTrackingItem()
        pdp_technical_specification = []
        # reading images
        js_images = response.xpath("//script[contains(text(), 'register(\"ImageBlockATF\"')]/text()").extract_first()
        xml_images = js2xml.parse(js_images)
        image_selector = scrapy.Selector(root=xml_images)
        # end images

        # reading videos
        js_video = response.xpath("//script[contains(text(), 'register(\"ImageBlockATF\"')]/text()").extract_first()
        xml_video = js2xml.parse(js_video)
        video_selector = scrapy.Selector(root=xml_video)

        # technical specifications
        tech_specifications_data = response.css(
            'div#prodDetails div.a-span-last div.a-section span.a-declarative a::attr(href)').extract()
        tech_specifications_name = response.css(
            'div#prodDetails div.a-span-last div.a-section span.a-declarative a::text').extract()
        for text, name in zip(tech_specifications_name, tech_specifications_data):
            temp_dict = {
                text.strip(): name.strip()
            }
            pdp_technical_specification.append(temp_dict)
        warranty_and_support = response.cssgit ('div#product-details-grid_feature_div div#productDetails_feature_div div '
                                            'div#prodDetails div.a-span-last div.a-spacing-base div.table-padding '
                                            'a::attr(href)').extract()
        pdp_small_image = image_selector.xpath(
            '//property[@name="colorImages"]//property[@name="thumb"]/string/text()').extract()
        pdp_medium_image = image_selector.xpath(
            '//property[@name="colorImages"]//property[@name="large"]/string/text()').extract()
        pdp_large_image = image_selector.xpath(
            '//property[@name="colorImages"]//property[@name="hiRes"]/string/text()').extract()
        pdp_video_url = video_selector.xpath(
            '//property[@name="videos"]')

        pdp_a_plus_content = response.css('div#dpx-aplus-product-description_feature_div div#aplus_feature_div '
                                          'div#aplus div.aplus-v2 div.aplus-module-wrapper '
                                          'table.apm-eventhirdcol-table th.apm-center div.apm-eventhirdcol p '
                                          'img::attr(src)').extract()
        # pattern = re.findall("var obj =(.+?);", response.body.decode("utf-8"), re.S)
        # de = re.findall('url', pattern)
        # print(de)
        sale_price = response.xpath(
            '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()').extract_first()
        if sale_price is None:
            seller_info = response.css('div#availability span.a-size-medium a::attr(href)').get()
            seller_info_url = 'https://www.amazon.com/' + str(seller_info)
            request = scrapy.Request(seller_info_url,
                                     callback=self.get_seller_price,
                                     cb_kwargs=dict(items=items), errback=self.get_https_errors,
                                     dont_filter=True)
            request.meta['pdp_small_image'] = pdp_small_image
            request.meta['pdp_medium_image'] = pdp_medium_image
            request.meta['pdp_large_image'] = pdp_large_image
            request.meta['pdp_video_url'] = pdp_video_url
            request.meta['pdp_technical_specification'] = pdp_technical_specification
            if warranty_and_support:
                request.meta['warranty_and_support'] = 'https://www.amazon.com/'+warranty_and_support[-1]
            else:
                request.meta['warranty_and_support'] = ''
            yield request
        else:
            items['pdp_price'] = sale_price
            items['pdp_small_image'] = pdp_small_image
            items['pdp_medium_image'] = pdp_medium_image
            items['pdp_large_image'] = pdp_large_image
            items['pdp_video_url'] = pdp_video_url
            items['pdp_technical_specification'] = pdp_technical_specification
            if warranty_and_support:
                items['warranty_and_support'] = 'https://www.amazon.com/'+warranty_and_support[-1]
            else:
                items['warranty_and_support'] = ''
            yield items
        os.chmod("/home/manoj/Documents/amazon/", 0o777)
        all_pdp_images = pdp_small_image + pdp_medium_image + pdp_large_image
        for image_url in all_pdp_images:
            image_name = image_url.split('/')[-1]
            with open('/home/manoj/Documents/amazon/' + image_name, 'wb') as handle:
                response = requests.get(image_url, stream=True)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

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

    def get_seller_price(self, response, items):
        # print(response)
        get_all_seller_data = response.css('div.a-spacing-double-large')
        seller_info = []
        seller_formatted_data = []
        price = response.css(
            'div.a-spacing-double-large div.olpOffer div.olpPriceColumn span.olpOfferPrice::text').extract()
        condition = response.css('div.a-spacing-double-large div.olpOffer div.olpConditionColumn '
                                 'span.olpCondition::text').extract()
        delivery_ship_form = response.css('div.a-spacing-double-large div.olpOffer div.olpDeliveryColumn '
                                          'ul.olpFastTrack '
                                          'span.a-list-item::text').extract()
        delivery_ship_rate_policy = response.css('div.a-spacing-double-large div.olpOffer div.olpDeliveryColumn '
                                                 'ul.olpFastTrack '
                                                 'span.a-list-item a::attr(href)').extract()
        # delivery_ship_rate_policy_url = 'https://www.amazon.com' + delivery_ship_rate_policy

        seller_name = response.css(
            'div.a-spacing-double-large div.olpOffer div.olpSellerColumn h3.olpSellerName span.a-text-bold a::text').extract()
        # seller_rating = sel_data.css('div.olpOffer div.olpSellerColumn p i.a-icon '
        #                              'span.a-icon-alt::text').extract()
        # seller_positive_rating = sel_data.css('div.olpOffer div.olpSellerColumn p a b::text').extract()
        # seller_info_list = {
        #     "seller_name": seller_name,
        #     "seller_rating": seller_rating + seller_positive_rating
        # }
        temp_data = {
            "shipping_price": price,
            # "condition (Learn more)": condition,
            # "delivery": delivery_ship_form,
            # "policy": delivery_ship_rate_policy,
            # "positive_rating": seller_positive_rating,
            "seller_info": seller_name
        }
        seller_info.append(temp_data)
        price = temp_data['shipping_price']
        seller_name = temp_data['seller_info']
        for (price, seller_name) in zip(price, seller_name):
            pdp_item = {
                "seller_name": seller_name.strip(),
                "seller_price": price.strip().strip(),
            }
            seller_formatted_data.append(pdp_item)
        items['pdp_price'] = seller_formatted_data
        items['pdp_small_image'] = response.meta['pdp_small_image']
        items['pdp_medium_image'] = response.meta['pdp_medium_image']
        items['pdp_large_image'] = response.meta['pdp_large_image']
        items['pdp_video_url'] = response.meta['pdp_video_url']
        items['pdp_technical_specification'] = response.meta['pdp_technical_specification']
        items['warranty_and_support'] = response.meta['warranty_and_support']
        return items
