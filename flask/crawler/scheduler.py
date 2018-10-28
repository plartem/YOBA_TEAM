import celery
import celery.schedules
import config_loader as cfg

file_name = __file__.split('/')[-1]

celery_app = celery.Celery(main=file_name, broker=cfg.cfg['redis']['broker_url'])
celery_app.conf.timezone = cfg.cfg['redis']['timezone']

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes everyday at 23:59
    sender.add_periodic_task(
        celery.schedules.crontab(hour=23, minute=59),
        run_crawlers.s(),
    )

@celery_app.task
def run_crawlers():
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    from crawler.spiders.ab_spider import AutoBazarSpider
    from crawler.spiders.autoportal_spider import AutoPortalSpider
    from crawler.spiders.autoria_spider import AutoriaSpider
    from crawler.spiders.rst import RSTSpider

    process = CrawlerProcess(get_project_settings())
    process.crawl(AutoBazarSpider)
    process.crawl(AutoPortalSpider)
    process.crawl(AutoriaSpider)
    process.crawl(RSTSpider)
    process.start()  # the script will block here until all crawling jobs are finished
