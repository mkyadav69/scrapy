# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    page_url = scrapy.Field()
    pdp_url = scrapy.Field()
    pdp_title = scrapy.Field()
    pdp_price = scrapy.Field()
    pdp_saving_price = scrapy.Field()

    pdp_size = scrapy.Field()
    pdp_brand = scrapy.Field()
    pdp_rating = scrapy.Field()
    pdp_bullet_description = scrapy.Field()
    pdp_information = scrapy.Field()
    pdp_descriptions = scrapy.Field()
    pdp_customer_rating = scrapy.Field()
    pdp_time_taken = scrapy.Field()

    # pdp_image = scrapy.Field()