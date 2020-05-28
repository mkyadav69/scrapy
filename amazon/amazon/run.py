# # import the spiders you want to run
#
# # scrapy api imports
#
# from scrapy import signals
# from scrapy.crawler import CrawlerRunner
# from scrapy.settings import Settings
# from twisted.internet import reactor
#
# # list of crawlers
#
#
# # crawlers that are running
# RUNNING_CRAWLERS = []
#
# def spider_closing(spider):
#     """
#     Activates on spider closed signal
#     """
#     spider.logger.info('Spider closed: %s', spider)
#     # log.msg("Spider closed: %s" % spider, level=log.INFO)
#     RUNNING_CRAWLERS.remove(spider)
#     if not RUNNING_CRAWLERS:
#         reactor.stop()
#
# # start logger
#
#
# # set up the crawler and start to crawl one spider at a time
# for spider in TO_CRAWL:
#     settings = Settings()
#
#     # crawl responsibly
#     # settings.set("USER_AGENT", "Kiran Koduru (+http://kirankoduru.github.io)")
#     crawler = CrawlerRunner()
#     crawler_obj = spider()
#     RUNNING_CRAWLERS.append(crawler_obj)
#
#     process = CrawlerProcess()
#     process.crawl(MySpider1)
#     process.crawl(MySpider2)
#     process.start()  # the script will block here until all crawling jobs are finished
#     # stop reactor when spider closes
#     crawler.signals.connect(spider_closing, signal=signals.spider_closed)
#     crawler.configure()
#     crawler.crawl(crawler_obj)
#     crawler.start()
#
# # blocks process; so always keep as the last statement
# reactor.run()


import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from amazon.amazon.spiders.floor_mirror import FloorMirrorSpider
from amazon.amazon.spiders.recliner import ReclinerSpider

TO_CRAWL = [FloorMirrorSpider, ReclinerSpider]


class MySpider1(scrapy.Spider):
    # Your first spider definition
    ...


class MySpider2(scrapy.Spider):
    # Your second spider definition
    ...


configure_logging()
runner = CrawlerRunner()
runner.crawl(MySpider1)
runner.crawl(MySpider2)
d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()  # the script will block here until all crawling jobs are finished
