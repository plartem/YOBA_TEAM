import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawler.spiders.ab_spider import AutoBazarSpider
from crawler.spiders.autoportal_spider import AutoPortalSpider
from crawler.spiders.autoria_spider import AutoriaSpider
from crawler.spiders.rst import RSTSpider
from crawler.spiders.autos_spider import AutosSpider


process = CrawlerProcess(get_project_settings())
process.crawl(AutoBazarSpider)
process.crawl(AutoPortalSpider)
process.crawl(AutoriaSpider)
process.crawl(RSTSpider)
process.crawl(AutosSpider)
process.start()

# the script will block here until all crawling jobs are finished
