from datetime import timedelta

import scrapy
import re
import sys
import mysql.connector
import pymongo
import smtplib
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawler.spiders.ab_spider import AutoBazarSpider
from crawler.spiders.autoportal_spider import AutoPortalSpider
from crawler.spiders.autoria_spider import AutoriaSpider
from crawler.spiders.rst import RSTSpider
from crawler.spiders.autos_spider import AutosSpider

import config

process = CrawlerProcess(get_project_settings())
process.crawl(AutoBazarSpider)
process.crawl(AutoPortalSpider)
process.crawl(AutoriaSpider)
process.crawl(RSTSpider)
process.crawl(AutosSpider)
process.start()

dbstate = mysql.connector.connect(
    host=config.MYSQL_CONFIG['host'],
    port=config.MYSQL_CONFIG['port'],
    user=config.MYSQL_CONFIG['user'],
    password=config.MYSQL_CONFIG['password'],
    database=config.MYSQL_CONFIG['dbname']
)
connection = pymongo.MongoClient(
    "localhost",
    27017
)

server = smtplib.SMTP(config.MAIL_CONFIG['server'], 587)

server.starttls()
# Next, log in to the server
server.login(config.MAIL_CONFIG['username'], config.MAIL_CONFIG['password'])

db = connection["crawler_db"]
collection = db["cars"]

mycursor = dbstate.cursor()
mycursor.execute(
    "SELECT * FROM queries INNER JOIN users ON queries.user_id = users.id WHERE TIMESTAMPDIFF(MINUTE, queries.updatedAt, CURRENT_TIMESTAMP) >= queries.timeinterval")
myresult = mycursor.fetchall()

for x in myresult:
    temp = 0
    x = list(x)
    if x[1] == "":  # mark
        x[1] = ".+"
    if x[2] == "":  # model
        x[2] = ".+"
    if x[3] == -1:  # high_pr
        x[3] = sys.maxsize
    if x[4] == -1:  # lw_pr
        x[4] = -sys.maxsize
    if x[5] == -1:  # year
        x[5] = sys.maxsize
    else:
        temp = x[5]
    if x[6] == -1:  # mileage
        x[6] = sys.maxsize

    regx_mark = re.compile("^%s$" % x[1], re.IGNORECASE)
    regx_model = re.compile("^%s$" % x[2], re.IGNORECASE)

    cars = list(collection.find({"mark_name": regx_mark, "model_name": regx_model,
                                 "mileage": {"$lte": x[6]},
                                 "year": {"$gte": temp, "$lte": x[5]},
                                 "price": {"$gte": x[4], "$lte": x[3]},
                                 "date": {"$gte": x[9]}}))
    msg = ""
    for car in cars:
        msg += car['mark_name'] + " " + car["model_name"] + "\n"
    msg += "Queries list: 127.0.0.1:5000/queries\n"
    print(msg.encode('utf8'))
    server.sendmail(config.MAIL_CONFIG['def_sender'], x[12], msg.encode('utf8'))
    mycursor.execute("UPDATE queries SET updatedAt=CURRENT_TIMESTAMP WHERE id=%s", (x[0],))
dbstate.commit()


# the script will block here until all crawling jobs are finished
